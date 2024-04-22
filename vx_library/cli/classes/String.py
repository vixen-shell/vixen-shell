from ..utils.levels import Level, LEVEL_COLORS


class String:
    @staticmethod
    def spaces(number: int = 0):
        return (" " * number) if number > 0 else ""

    @staticmethod
    def level(string: str, level: Level = None):
        if not level:
            return string

        return f"{LEVEL_COLORS[level]}{string}{LEVEL_COLORS['DEFAULT']}"

    @staticmethod
    def format(
        string: str,
        prefix: str = None,
        suffix: str = None,
        spaces: int = 1,
        start_spaces: int = 0,
        line_break: bool = False,
    ) -> str:
        prefix = prefix + String.spaces(spaces) if prefix else ""
        suffix = String.spaces(spaces) + suffix if suffix else ""

        string = prefix + string + suffix

        return String.spaces(start_spaces) + string + ("\n" if line_break else "")
