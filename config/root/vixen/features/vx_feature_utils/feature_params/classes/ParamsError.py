import json
from pydantic import ValidationError
from typing import TypedDict, Any


class ParamsErrorDetails(TypedDict):
    loc: tuple[str]
    value: Any


class ParamsError(Exception):
    def __init__(self, title: str, message: str, details: ParamsErrorDetails):
        v_loc = details.get("loc")
        loc = f" [loc]: {', '.join(v_loc)}" if v_loc else ""

        v_value = details.get("value")
        value = f" [value]: {str(v_value)}" if v_value else ""

        super().__init__(f"{title} ({message}){loc}{value}")


class ParamsValidationError(ParamsError):
    def __init__(self, title: str, validation_error: ValidationError):
        error_json = json.loads(validation_error.json())[0]
        message = error_json["msg"]
        details = ParamsErrorDetails(loc=error_json["loc"], value=error_json["input"])

        super().__init__(title, message, details)
