import sqlite3
from models.expense import Expense

DB_NAME = 'expenses.db'

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                name TEXT PRIMARY KEY
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS members (
                group_name TEXT,
                member_name TEXT,
                PRIMARY KEY (group_name, member_name)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                description TEXT,
                amount REAL,
                paid_by TEXT,
                split TEXT,
                date TEXT
            )
        ''')

def create_group_in_db(name):
    with get_conn() as conn:
        conn.execute("INSERT INTO groups (name) VALUES (?)", (name,))

def group_exists(name):
    with get_conn() as conn:
        cur = conn.execute("SELECT 1 FROM groups WHERE name=?", (name,))
        return cur.fetchone() is not None

def add_member_to_db(group_name, member_name):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO members (group_name, member_name) VALUES (?, ?)",
            (group_name, member_name)
        )

def member_exists(group_name, member_name):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT 1 FROM members WHERE group_name=? AND member_name=?",
            (group_name, member_name)
        )
        return cur.fetchone() is not None

def load_members_from_db(group_name):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT member_name FROM members WHERE group_name=?", (group_name,)
        )
        return [row[0] for row in cur.fetchall()]

def save_expense_to_db(expense, group_name):
    with get_conn() as conn:
        conn.execute('''
            INSERT INTO expenses (group_name, description, amount, paid_by, split, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (group_name, expense.description, expense.amount, expense.paid_by,
              str(expense.split), expense.date))

def delete_expense_from_db(expense, group_name):
    with get_conn() as conn:
        conn.execute('''
            DELETE FROM expenses
            WHERE group_name=? AND description=? AND amount=? AND paid_by=? AND date=?
        ''', (group_name, expense.description, expense.amount, expense.paid_by, expense.date))

def load_expenses_from_db(group):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT description, amount, paid_by, split, date FROM expenses WHERE group_name=?",
            (group.name,)
        )
        rows = cur.fetchall()
        for r in rows:
            group.expenses.append(Expense(r[0], r[1], r[2], eval(r[3]), r[4]))
