from .CodeOverview import CodeOverview
from ...cli import Cli


class CallSummary:
    def __init__(self, file_name: str, line_number: int):
        self.code = CodeOverview(file_name, line_number)

    def filtered_filename(self, path_element: str = None):
        if not path_element:
            return self.file_name

        path_elements = self.file_name.split("/")

        if not path_element in path_elements[:-1]:
            return self.file_name

        path_elements = [".."] + path_elements[path_elements.index(path_element) :]
        return "/".join(path_elements)

    def print(self, path_filter: str = None, overview: bool = False):
        print(
            Cli.String.format(
                string=self.filtered_filename(path_filter),
                prefix=Cli.String.level(
                    "file: " if not self.is_raised else "Raise in: ",
                    "DEBUG" if not self.is_raised else "ERROR",
                ),
                start_spaces=7,
            )
            + Cli.String.format(
                string=str(self.code.line_number),
                prefix=Cli.String.level("line: ", "DEBUG"),
                start_spaces=1,
            )
        )

        if overview:
            self.code.print()

    @property
    def file_name(self):
        return self.code.file_name

    @property
    def line_number(self):
        return self.code.line_number

    @property
    def is_raised(self):
        return "raise" in self.code.code_line

    @property
    def is_exclude(self):
        return "# @errorHandling exclude" in self.code.code_line
