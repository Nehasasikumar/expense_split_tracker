from db.database import save_expense_to_db, delete_expense_from_db
from datetime import datetime

class Group:
    def __init__(self, name):
        self._name = name
        self._members = []
        self._expenses = []
        self._history = []

    @property
    def name(self):
        return self._name

    @property
    def members(self):
        return self._members

    @property
    def expenses(self):
        return self._expenses

    def add_member(self, person):
        if person.get_name() not in [m.get_name() for m in self._members]:
            self._members.append(person)
        else:
            print(f"{person.get_name()} already exists.")

    def add_expense(self, expense):
        for e in self._expenses:
            if (e.description == expense.description and
                e.amount == expense.amount and
                e.paid_by == expense.paid_by and
                e.date == expense.date):
                print("Duplicate expense detected!")
                return
        self._expenses.append(expense)
        self._history.append(expense)
        save_expense_to_db(expense, self._name)

    def undo(self):
        if not self._history:
            print("Nothing to undo.")
            return
        last = self._history.pop()
        self._expenses.remove(last)
        delete_expense_from_db(last, self._name)
        print(f"Undid: {last.description} of ₹{last.amount:.2f}")

    def show_summary(self):
        balances = {m.get_name(): 0.0 for m in self._members}
        for e in self._expenses:
            balances[e.paid_by] += e.amount
            for person, share in e.split.items():
                balances[person] -= share

        print("\n--- Balances ---")
        for name, bal in balances.items():
            if bal > 0:
                print(f"{name} is owed ₹{bal:.2f}")
            elif bal < 0:
                print(f"{name} owes ₹{abs(bal):.2f}")
            else:
                print(f"{name} is settled.")

    def show_history(self):
        print("\n--- Expense History ---")
        if not self._expenses:
            print("No expenses recorded.")
        for e in self._expenses:
            print(e)

    def monthly_summary(self, month, year):
        print(f"\n--- Monthly Summary for {month}/{year} ---")
        paid_totals = {m.get_name(): 0.0 for m in self._members}
        owed_totals = {m.get_name(): 0.0 for m in self._members}

        for e in self._expenses:
            dt = datetime.strptime(e.date, '%Y-%m-%d %H:%M:%S')
            if dt.month == month and dt.year == year:
                paid_totals[e.paid_by] += e.amount
                for person, share in e.split.items():
                    owed_totals[person] += share

        for name in paid_totals:
            print(f"{name} paid ₹{paid_totals[name]:.2f} (owed ₹{owed_totals[name]:.2f})")

    def member_summary(self, member_name):
        print(f"\n--- Member Summary for {member_name} ---")
        spent = 0.0
        owed = 0.0
        for e in self._expenses:
            if e.paid_by == member_name:
                spent += e.amount
            if member_name in e.split:
                owed += e.split[member_name]

        print(f"Total paid by {member_name}: ₹{spent:.2f}")
        print(f"Total owed by {member_name}: ₹{owed:.2f}")
        net = spent - owed
        if net > 0:
            print(f"Net: {member_name} is owed ₹{net:.2f}")
        elif net < 0:
            print(f"Net: {member_name} owes ₹{abs(net):.2f}")
        else:
            print("Net: Settled.")

    def settle_up(self):
        balances = {m.get_name(): 0.0 for m in self._members}
        for e in self._expenses:
            balances[e.paid_by] += e.amount
            for person, share in e.split.items():
                balances[person] -= share

        creditors = []
        debtors = []
        for name, bal in balances.items():
            if bal > 0:
                creditors.append([name, bal])
            elif bal < 0:
                debtors.append([name, -bal])

        print("\n--- Settle Up Transactions ---")
        i, j = 0, 0
        while i < len(debtors) and j < len(creditors):
            dname, damt = debtors[i]
            cname, camt = creditors[j]
            paid = min(damt, camt)
            print(f"{dname} pays {cname}: ₹{paid:.2f}")
            debtors[i][1] -= paid
            creditors[j][1] -= paid
            if debtors[i][1] == 0:
                i += 1
            if creditors[j][1] == 0:
                j += 1
