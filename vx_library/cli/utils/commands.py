import subprocess


def exec(command: str, stdout: bool = False, stderr: bool = True) -> bool:
    process = subprocess.run(
        command,
        stdout=None if stdout else subprocess.PIPE,
        stderr=None if stderr else subprocess.PIPE,
        shell=True,
    )

    if process.returncode != 0:
        return False

    return True
