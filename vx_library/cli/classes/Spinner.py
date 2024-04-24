import sys, time, threading


class Spinner:
    def __init__(self):
        self.is_running = False
        self.thread = threading.Thread(target=self.spinner)

    def spinner(self):
        self.is_running = True
        n_point: int = 0

        def remove_point(n_point: int) -> int:
            sys.stdout.write("\b" * n_point)
            sys.stdout.write(" " * n_point)
            sys.stdout.write("\b" * n_point)
            sys.stdout.flush()
            return 0

        def add_point(n_point: int) -> int:
            sys.stdout.write(".")
            sys.stdout.flush()
            return n_point + 1

        def handle_point(n_point: int) -> int:
            if self.is_running and n_point < 3:
                n_point = add_point(n_point)
            else:
                n_point = remove_point(n_point)

            return n_point

        while True:
            if not self.is_running:
                remove_point(n_point)
                break
            else:
                time.sleep(0.5)
                n_point = handle_point(n_point)

    def cursor(self, visible: bool):
        if not visible:
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()
        else:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def run(self):
        if not self.is_running:
            self.cursor(False)
            self.thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            sys.stdout.write("\r")
            sys.stdout.flush()
            self.cursor(True)
            self.thread.join()
