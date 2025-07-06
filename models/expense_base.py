from abc import ABC, abstractmethod

class AbstractExpense(ABC):
    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
