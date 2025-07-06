class BaseUser:
    def __init__(self, name):
        self._name = name  # Encapsulated attribute

    def get_name(self):
        return self._name

    def __str__(self):
        return self._name
