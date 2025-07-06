from models.group import Group
from models.person import Person
from models.expense import Expense
from db.database import (
    init_db, load_expenses_from_db, group_exists, member_exists,
    create_group_in_db, add_member_to_db, load_members_from_db
)
from datetime import datetime
import sqlite3

DB_NAME = 'expenses.db'  # Make sure this matches your database file

# Input validation helpers
def input_int(prompt):
    while True:
        val = input(prompt)
        if val.isdigit():
            return int(val)
        print("Please enter a valid integer.")

def input_float(prompt):
    while True:
        val = input(prompt)
        try:
            return float(val)
        except ValueError:
            print("Please enter a valid number.")

def input_name(prompt):
    while True:
        val = input(prompt).strip()
        if val.isalpha():
            return val
        print("Please enter a valid name (letters only).")

def paid_not_paid_details():
    group_name = input("Enter group name: ")
    if not group_exists(group_name):
        print("Group not found.")
        return
    group = Group(group_name)
    members = load_members_from_db(group_name)
    for name in members:
        group.add_member(Person(name))
    load_expenses_from_db(group)

    print(f"\n--- Paid / Not Paid Details for group '{group_name}' ---")
    balances = {m.name: 0.0 for m in group.members}
    for e in group.expenses:
        print(f"\nExpense: {e.description} | Total: ₹{e.amount:.2f} | Paid by: {e.paid_by}")
        for m in group.members:
            owed = e.split.get(m.name, 0)
            if m.name == e.paid_by:
                print(f"  {m.name} spent ₹{e.amount:.2f} (their share: ₹{owed:.2f})")
            else:
                print(f"  {m.name} owes ₹{owed:.2f}")

        balances[e.paid_by] += e.amount
        for person, share in e.split.items():
            balances[person] -= share

    print("\nOverall Balances (Positive = owed to person, Negative = owes person):")
    for name, bal in balances.items():
        if bal > 0:
            print(f"  {name} is owed ₹{bal:.2f}")
        elif bal < 0:
            print(f"  {name} owes ₹{abs(bal):.2f}")
        else:
            print(f"  {name} is settled.")

def view_raw_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    print("\n--- Groups ---")
    cur.execute("SELECT name FROM groups")
    groups = cur.fetchall()
    if not groups:
        print("No groups found.")
    else:
        for g in groups:
            print(f"Group: {g[0]}")

    print("\n--- Members ---")
    cur.execute("SELECT group_name, member_name FROM members ORDER BY group_name")
    members = cur.fetchall()
    if not members:
        print("No members found.")
    else:
        current_group = None
        for group_name, member_name in members:
            if group_name != current_group:
                print(f"\nGroup: {group_name}")
                current_group = group_name
            print(f"  Member: {member_name}")

    print("\n--- Expenses ---")
    cur.execute("SELECT group_name, description, amount, paid_by, split, date FROM expenses ORDER BY group_name, date")
    expenses = cur.fetchall()
    if not expenses:
        print("No expenses found.")
    else:
        current_group = None
        for group_name, desc, amount, paid_by, split, date in expenses:
            if group_name != current_group:
                print(f"\nGroup: {group_name}")
                current_group = group_name
            print(f"  [{date}] {desc}: ₹{amount:.2f}, paid by {paid_by}, split: {split}")

    conn.close()

def main():
    init_db()

    print("Welcome to Expense Split Tracker")
    mode = input("1. Create new group\n2. Use existing group\nSelect option: ")

    if mode == '1':
        group_name = input("Enter new group name: ")
        create_group_in_db(group_name)
        group = Group(group_name)
        num = input_int("How many members? ")
        for _ in range(num):
            name = input_name("Member name: ")
            person = Person(name)
            group.add_member(person)
            add_member_to_db(group_name, name)

        user = input_name("Enter your name: ")
        if not member_exists(group_name, user):
            print("You are not a member of this group.")
            return
        print(f"Welcome, {user}!")

    elif mode == '2':
        group_name = input("Enter group name: ")
        if not group_exists(group_name):
            print("Group not found.")
            return
        group = Group(group_name)
        members = load_members_from_db(group_name)
        for name in members:
            group.add_member(Person(name))

        user = input_name("Enter your name: ")
        if not member_exists(group_name, user):
            print("You are not a member of this group.")
            return
        print(f"Welcome back, {user}!")

    else:
        print("Invalid option")
        return

    load_expenses_from_db(group)

    while True:
        print("\nOptions:")
        print("1. Add Expense")
        print("2. Show Balances")
        print("3. Show History")
        print("4. Undo Last Expense")
        print("5. Monthly Summary")
        print("6. Member Summary")
        print("7. Settle Up")
        print("8. Exit")
        print("9. Paid/Not Paid Details")
        print("10. View Raw Database")

        choice = input("Select: ")

        if choice == '1':
            desc = input("Description: ")
            amt = input_float("Amount: ")
            paid_by = input_name("Who paid? ")
            if paid_by not in [m.name for m in group.members]:
                print("Invalid member.")
                continue

            split_type = input("Split (equal/custom): ").lower()
            split = {}

            if split_type == 'equal':
                per = round(amt / len(group.members), 2)
                for m in group.members:
                    split[m.name] = per
            elif split_type == 'custom':
                total_share = 0
                for m in group.members:
                    share = input_float(f"{m.name}: ")
                    split[m.name] = share
                    total_share += share
                if round(total_share, 2) != round(amt, 2):
                    print("Split doesn't match total amount.")
                    continue
            else:
                print("Invalid split type")
                continue

            expense = Expense(desc, amt, paid_by, split)
            group.add_expense(expense)

        elif choice == '2':
            group.show_summary()

        elif choice == '3':
            group.show_history()

        elif choice == '4':
            group.undo()

        elif choice == '5':
            try:
                m = input_int("Month (1-12): ")
                y = input_int("Year: ")
                if 1 <= m <= 12:
                    group.monthly_summary(m, y)
                else:
                    print("Invalid month.")
            except ValueError:
                print("Please enter valid numbers for month and year.")

        elif choice == '6':
            name = input_name("Member name: ")
            if name in [m.name for m in group.members]:
                group.member_summary(name)
            else:
                print("Member not found.")

        elif choice == '7':
            group.settle_up()

        elif choice == '8':
            print("Bye!")
            break

        elif choice == '9':
            paid_not_paid_details()

        elif choice == '10':
            view_raw_database()

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
