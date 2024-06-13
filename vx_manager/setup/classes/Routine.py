from .RoutineTask import RoutineTask
from ...logger import Logger


class Routine:
    def __init__(self, purpose: str, tasks: list[RoutineTask]):
        self.purpose = purpose
        self.tasks = tasks

    def run(self):
        print()
        Logger.log(self.purpose)

        def undo():
            for task in reversed(self.tasks):
                if task.is_done:
                    task.undo()

            Logger.log(self.purpose, "WARNING", "FAILED")
            return False

        for task in self.tasks:
            if not task.exec():
                return undo()

        Logger.log(self.purpose, suffix="DONE")
        return True
