class Cli:
    from ..utils.levels import Level
    from .Input import Input
    from .String import String
    from .Spinner import Spinner

    @staticmethod
    def exec(command: str, stdout: bool = False, stderr: bool = True) -> bool:
        from ..utils.commands import exec

        return exec(command, stdout, stderr)
