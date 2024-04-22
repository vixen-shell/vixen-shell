import linecache
from typing import Dict

from ...cli import Cli


class CodeOverview:
    def __init__(self, file_name: str, line_number: int, amplitude: int = 3):
        self.amplitude = amplitude
        self.line_number = line_number
        self.file_name = file_name
        self.overview = self.get_overview()

    def get_overview(self) -> Dict[int, str]:
        lines = [""] + linecache.getlines(self.file_name)
        lines = lines[self.first_line_number : self.last_line_number + 1]

        overview: Dict[int, str] = {}
        for line_number, line in enumerate(lines):
            overview[line_number + self.first_line_number] = line.rstrip()

        return overview

    def print(self):
        def formatted_line(number: int):
            return Cli.String.format(
                string=(
                    Cli.String.level(" > ", "WARNING")
                    if number == self.line_number
                    else "   "
                )
                + Cli.String.level("| ", "DEBUG")
                + (
                    Cli.String.level(self.overview[number], "WARNING")
                    if number == self.line_number
                    else self.overview[number]
                ),
                prefix=Cli.String.level(str(number), "DEBUG"),
                start_spaces=10 - len(str(number)),
                line_break=True,
            )

        overview = "\n"

        for number in self.overview:
            overview += formatted_line(number)

        print(overview)

    @property
    def first_line_number(self) -> int:
        number = self.line_number - self.amplitude
        return number if number >= 1 else 1

    @property
    def last_line_number(self) -> int:
        number = self.line_number + self.amplitude
        maximum = len(linecache.getlines(self.file_name))
        return number if number <= maximum else maximum

    @property
    def code_line(self) -> str:
        return self.overview[self.line_number]
