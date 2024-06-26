from typing import TypeVar, Generic, Literal

T = TypeVar("T")
Disable = Literal["disable"]


class ParamValidationException(Exception):
    def __init__(self, root_value) -> None:
        if root_value == "disable":
            message = "Disabled parameter, cannot define user value"
        else:
            if not isinstance(root_value, list):
                message = "Root definition, cannot define user value"
            else:
                message = f"Root definition, user value can be {root_value}"

        super().__init__(message)


class ParamValue(Generic[T]):
    def __init__(
        self,
        root_value: T | list[T] | Disable | None,
        user_value: T | None,
    ) -> None:
        self._root_value = root_value
        self._user_value = user_value

        self.__validate(self._user_value)

    def __validate(self, value: T | None):
        if value:
            if self._root_value is None:
                return

            if (
                self._root_value == "disable"
                or not isinstance(self._root_value, list)
                or not value in self._root_value
            ):
                raise ParamValidationException(self._root_value)

    @property
    def value(self) -> T | None:
        if self._root_value is None:
            return self._user_value

        if self._root_value == "disable":
            return None

        if isinstance(self._root_value, list):
            return self._user_value or self._root_value[0]

        return self._root_value

    @value.setter
    def value(self, value: T):
        self.__validate(value)
        self._user_value = value
