from models.expense_base import AbstractExpense
from datetime import datetime

class Expense(AbstractExpense):
    def __init__(self, description, amount, paid_by, split, date=None):
        self._description = description
        self._amount = float(amount)
        self._paid_by = paid_by
        self._split = split
        self._date = date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "description": self._description,
            "amount": self._amount,
            "paid_by": self._paid_by,
            "split": self._split,
            "date": self._date
        }

    def __str__(self):
        return f"{self._date} - {self._paid_by} paid ₹{self._amount:.2f} for '{self._description}' (split: {self._split})"

    @property
    def description(self):
        return self._description

    @property
    def amount(self):
        return self._amount

    @property
    def paid_by(self):
        return self._paid_by

    @property
    def split(self):
        return self._split

    @property
    def date(self):
        return self._date
