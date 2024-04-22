import os, time, subprocess, multiprocessing


def get_vite_process(dev_dir: str):
    def vite_process():
        process = subprocess.Popen(f"{dev_dir}/node_modules/.bin/vite", shell=True)
        process.wait()

    if not os.path.exists(f"{dev_dir}/node_modules"):
        raise Exception("Node modules not found")

    class ProcessReference:
        def __init__(self):
            self.process = multiprocessing.Process(target=vite_process)

        def start(self):
            self.process.start()
            time.sleep(1)

        def join(self):
            try:
                self.process.join()
            except KeyboardInterrupt:
                self.process.terminate()

    return ProcessReference()


def sudo_is_used() -> bool:
    return os.geteuid() == 0
