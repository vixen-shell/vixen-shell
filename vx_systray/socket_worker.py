import sys, tempfile, os, subprocess
from pathlib import Path


def get_worker_content():
    vx_env_exec = "/opt/vixen-env/bin/python"
    current_env_exec = Path(sys.executable)
    additional_sys_path = None

    if current_env_exec.as_posix() != vx_env_exec:
        additional_sys_path = current_env_exec.parent.parent.parent.as_posix()

    return f"""#!{current_env_exec}

{f'''import sys
 
sys.path.append("{additional_sys_path}")
''' if additional_sys_path else ''}
if __name__ == "__main__":
    from vx_systray import run_systray_server
    run_systray_server()
    """


def start_worker():
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as worker:
        worker.write(get_worker_content())
        worker.flush()
        os.chmod(worker.name, 0o755)

    process = subprocess.Popen([worker.name])
    return worker.name, process
