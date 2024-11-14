from .InputSelection import InputFilter


class InputHandler:
    def __init__(self, purpose: str, filters: list[InputFilter] = []):
        self.purpose = purpose
        self.filters = filters

    def __call__(
        self, lower_cases: bool = True, no_spaces: bool = True, suffix: str = None
    ):
        response = input(self.purpose)

        if not response:
            raise ValueError("No entry received")

        if lower_cases:
            response = response.lower()

        if no_spaces:
            response = response.replace(" ", "")

        if suffix:
            response += suffix

        for filter in self.filters:
            filter.check(response)

        return response
