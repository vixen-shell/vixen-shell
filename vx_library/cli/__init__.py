class Cli:
    from .utils import Level
    from .classes import Input
    from .classes import String
    from .classes import Spinner

    @staticmethod
    def exec(command: str, stdout: bool = False, stderr: bool = True) -> bool:
        from .utils import exec

        return exec(command, stdout, stderr)
