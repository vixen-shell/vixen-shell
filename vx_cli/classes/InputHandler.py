from .InputSelection import InputFilter


class InputHandler:
    def __init__(self, purpose: str, filters: list[InputFilter] = []):
        self.purpose = purpose
        self.filters = filters

    def __call__(self, lower_cases: bool = True, no_spaces: bool = True):
        response = input(self.purpose)

        if lower_cases:
            response = response.lower()

        if no_spaces:
            response = response.replace(" ", "")

        for filter in self.filters:
            filter.check(response)

        return response
