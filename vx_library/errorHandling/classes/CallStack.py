from types import TracebackType
from typing import List

from .CallSummary import CallSummary


class CallStack:
    def __init__(self, exc_traceback: TracebackType):
        self.calls: List[CallSummary] = []
        self.raised_call: CallSummary = None
        self.init_stack(exc_traceback)

    def init_stack(self, frame: TracebackType):
        while frame is not None:
            call = CallSummary(frame.tb_frame.f_code.co_filename, frame.tb_lineno)

            if call.is_raised:
                self.raised_call = call
            elif call.is_exclude:
                pass
            else:
                self.calls.append(call)

            frame = frame.tb_next

    def filtered_calls(self, path_filter: str = None) -> List[CallSummary]:
        if not path_filter:
            return self.calls

        last_call = self.calls[-1]
        calls = [call for call in self.calls if path_filter in call.file_name]

        if len(calls) == 0 or calls[-1] != last_call:
            calls.append(last_call)

        return calls

    def print(self, path_filter: str = None):
        calls = self.filtered_calls(path_filter)

        for i in range(1, len(calls) + 1):
            calls[-i].print(path_filter, True if i == 1 else False)

        if self.raised_call:
            self.raised_call.print(path_filter, False)

        print()
