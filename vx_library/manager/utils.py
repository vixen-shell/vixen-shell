import os, time, subprocess, multiprocessing, json


def get_vite_process(dev_dir: str):
    def vite_process():
        process = subprocess.Popen(f"{dev_dir}/node_modules/.bin/vite", shell=True)
        process.wait()

    if not os.path.exists(f"{dev_dir}/node_modules"):
        raise Exception("Node modules not found")

    class ProcessReference:
        def __init__(self):
            self.process = multiprocessing.Process(target=vite_process)

        @property
        def is_alive(self) -> bool:
            return self.process.is_alive()

        def start(self):
            self.process.start()
            time.sleep(1)

        def join(self):
            try:
                self.process.join()
            except KeyboardInterrupt:
                self.process.terminate()

        def terminate(self):
            self.process.terminate()

    return ProcessReference()


def sudo_is_used() -> bool:
    return os.geteuid() == 0


def read_json(file_path: str) -> dict | None:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
