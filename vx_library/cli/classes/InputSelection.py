from typing import Literal

InputFilterType = Literal["exclude", "include"]


class InputFilterError(Exception):
    def __init__(self, value: str, type: InputFilterType, message: str = None):
        self.message = message or f"'{value}' is not a valid input"
        self.value = value
        self.type = type
        super().__init__(self.message)


class InputFilter:
    def __init__(
        self, type: InputFilterType, values: list[str] = [], reason: str = None
    ):
        self.type: InputFilterType = type
        self.values: list[str] = values
        self.reason: str = reason

    def check(self, value: str):
        if self.type == "include":
            if not value in self.values:
                raise InputFilterError(value, self.type, self.reason)

        if self.type == "exclude":
            if value in self.values:
                raise InputFilterError(value, self.type, self.reason)
