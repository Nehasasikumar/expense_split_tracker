from datetime import datetime

class Expense:
    def __init__(self, description, amount, paid_by, split, date=None):
        """
        Initializes an expense instance.

        :param description: A brief description of the expense.
        :param amount: Total amount spent.
        :param paid_by: Name of the person who paid.
        :param split: Dictionary showing how much each member owes.
        :param date: Optional. Date of the expense in string format.
        """
        self.description = description
        self.amount = float(amount)
        self.paid_by = paid_by
        self.split = split  # Example: {'Alice': 40.0, 'Bob': 60.0}
        self.date = date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        """
        Returns a dictionary representation of the expense (for JSON/db use).
        """
        return {
            "description": self.description,
            "amount": self.amount,
            "paid_by": self.paid_by,
            "split": self.split,
            "date": self.date
        }

    @staticmethod
    def from_dict(data):
        """
        Creates an Expense object from a dictionary.

        :param data: Dictionary containing keys: description, amount, paid_by, split, date.
        :return: Expense instance.
        """
        return Expense(
            description=data["description"],
            amount=data["amount"],
            paid_by=data["paid_by"],
            split=data["split"],
            date=data.get("date")
        )

    def __str__(self):
        """
        String representation of the expense (for print/debugging).
        """
        return f"{self.date} - {self.paid_by} paid ₹{self.amount} for '{self.description}' (split: {self.split})"
