from .InputHandler import InputHandler
from .InputSelection import InputFilter, InputFilterError


class Input:
    from .InputSelection import InputFilter as Filter

    @staticmethod
    def get_confirm() -> bool:
        responses = {"yes": True, "no": False}

        input_filters = [
            InputFilter(
                "include", list(responses.keys()), "Please answer with 'yes' or 'no'"
            )
        ]

        input = InputHandler("(yes/no or [ctrl + C]): ", input_filters)

        try:
            while True:
                try:
                    return responses.get(input())
                except InputFilterError as error:
                    print(error.message)
                except ValueError:
                    pass
        except KeyboardInterrupt:
            print()
            return False

    @staticmethod
    def get_answer(
        input_filters: list[InputFilter] = [],
        prompt: str = "(type or [ctrl + C]): ",
        suffix: str = None,
    ) -> str | None:
        input = InputHandler(prompt, input_filters)

        try:
            while True:
                try:
                    return input(suffix=suffix)
                except InputFilterError as error:
                    print(error.message)
                except ValueError:
                    pass
        except KeyboardInterrupt:
            print()
            return
