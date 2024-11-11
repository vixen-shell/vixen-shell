import os, sys
from argparse import Namespace, ArgumentParser
from typing import Literal, TypedDict, List
from .parsers import shell_parser, feature_parser, frame_parser, task_parser
from ..SetupManager import SetupManager as Setup
from ..ShellManager import ShellManager as Shell


class ExitError(TypedDict):
    parser: ArgumentParser
    message: str


def exit(error: ExitError = None):
    if not error:
        sys.exit(0)
    else:
        error["parser"].print_usage()
        print(f"{' '.join(sys.argv)}: error: {error['message']}")
        sys.exit(1)


class ShellHandler:
    action: Literal["open", "close"]
    no_dmabuf: bool

    @staticmethod
    def init(args: Namespace):
        ShellHandler.action = args.action
        ShellHandler.no_dmabuf = args.no_dmabuf

    @staticmethod
    def handle():
        action = ShellHandler.action
        no_dmabuf = ShellHandler.no_dmabuf

        if not action or action == "open":
            os.environ["GDK_BACKEND"] = "wayland"
            os.environ["WEBKIT_DISABLE_COMPOSITING_MODE"] = "0"

            if no_dmabuf:
                print("DMABUF Renderer disabled\n")
                os.environ["WEBKIT_DISABLE_DMABUF_RENDERER"] = "1"

            Shell.open()

        if action == "close":
            if no_dmabuf:
                exit(
                    {
                        "message": "No need to use the --no-dmabuf option in this context",
                        "parser": shell_parser,
                    }
                )

            Shell.close()

        exit()


class SetupHandler:
    action: Literal["update", "remove"]

    @staticmethod
    def init(args: Namespace):
        SetupHandler.action = args.action

    @staticmethod
    def handle():
        action = SetupHandler.action

        if action == "update":
            Setup.update()

        if action == "remove":
            Setup.remove()

        exit()


class FrameHandler:
    feature_name: str
    frame_name: str

    list: bool
    toggle: bool
    open: bool
    close: bool

    @staticmethod
    def init(args: Namespace):
        FrameHandler.feature_name = args.feature_name
        FrameHandler.frame_name = args.frame_name

        FrameHandler.list = args.list
        FrameHandler.toggle = args.toggle
        FrameHandler.open = args.open
        FrameHandler.close = args.close

    @staticmethod
    def _handle_options():
        if FrameHandler.list:
            Shell.feature_frame_ids(FrameHandler.feature_name)
        else:
            exit({"message": "Missing options", "parser": frame_parser})

        exit()

    @staticmethod
    def _handle_frame():
        if FrameHandler.list:
            exit(
                {
                    "message": f"Cannot use --list option in this context: remove name '{FrameHandler.frame_name}'",
                    "parser": frame_parser,
                }
            )

        elif FrameHandler.toggle:
            Shell.toggle_feature_frame(
                FrameHandler.feature_name, FrameHandler.frame_name
            )

        elif FrameHandler.open:
            Shell.open_feature_frame(FrameHandler.feature_name, FrameHandler.frame_name)

        elif FrameHandler.close:
            Shell.close_feature_frame(
                FrameHandler.feature_name, FrameHandler.frame_name
            )

        else:
            exit({"message": "Missing options", "parser": frame_parser})

        exit()

    @staticmethod
    def handle():
        frame_name = FrameHandler.frame_name

        if not frame_name:
            FrameHandler._handle_options()
        else:
            FrameHandler._handle_frame()


class TaskHandler:
    feature_name: str
    task_name: str

    args: List[str | int | float | None]
    list: bool

    @staticmethod
    def init(args: Namespace):
        TaskHandler.feature_name = args.feature_name
        TaskHandler.task_name = args.task_name

        TaskHandler.args = args.args
        TaskHandler.list = args.list

    @staticmethod
    def _handle_options():
        def check_args():
            if TaskHandler.args:
                exit(
                    {
                        "message": "No need to use the --args option in this context",
                        "parser": task_parser,
                    }
                )

        if TaskHandler.list:
            check_args()
            Shell.feature_task_names(TaskHandler.feature_name)
        else:
            exit({"message": "Missing options", "parser": task_parser})

        exit()

    @staticmethod
    def _handle_task():
        if TaskHandler.list:
            exit(
                {
                    "message": f"Cannot use --list option in this context: remove name '{TaskHandler.task_name}'",
                    "parser": task_parser,
                }
            )

        Shell.run_feature_task(
            TaskHandler.feature_name, TaskHandler.task_name, TaskHandler.args
        )

        exit()

    @staticmethod
    def handle():
        task_name = TaskHandler.task_name

        if not task_name:
            TaskHandler._handle_options()
        else:
            TaskHandler._handle_task()


class StateHandler:
    feature_name: str

    start: bool
    stop: bool

    @staticmethod
    def init(args: Namespace):
        StateHandler.feature_name = args.feature_name

        StateHandler.start = args.start
        StateHandler.stop = args.stop

    @staticmethod
    def handle():
        if StateHandler.start:
            Shell.start_feature(StateHandler.feature_name)

        if StateHandler.stop:
            Shell.stop_feature(StateHandler.feature_name)

        exit()


class FeatureHandler:
    args: Namespace
    feature_name: str
    feature_cmd: Literal["frame", "task"]

    path: str
    list: bool
    new: bool
    add: bool
    extra: str
    remove: bool
    dev: bool

    @staticmethod
    def init(args: Namespace):
        FeatureHandler.args = args
        FeatureHandler.feature_name = args.feature_name
        FeatureHandler.feature_cmd = args.feature_cmd

        FeatureHandler.path = args.path
        FeatureHandler.list = args.list
        FeatureHandler.new = args.new
        FeatureHandler.add = args.add
        FeatureHandler.extra = args.extra
        FeatureHandler.remove = args.remove
        FeatureHandler.dev = args.dev

    @staticmethod
    def _handle_path():
        return os.getcwd() if not FeatureHandler.path else FeatureHandler.path

    @staticmethod
    def _check_path():
        if FeatureHandler.path:
            exit(
                {
                    "message": "No need to use the --path option in this context",
                    "parser": feature_parser,
                }
            )

    @staticmethod
    def _handle_options():
        if FeatureHandler.list:
            FeatureHandler._check_path()
            Shell.feature_names()

        elif FeatureHandler.new:
            FeatureHandler._check_path()
            Setup.create_feature(FeatureHandler._handle_path())

        elif FeatureHandler.add:
            Setup.add_feature(FeatureHandler._handle_path())

        elif FeatureHandler.extra:
            FeatureHandler._check_path()
            Setup.add_extra_feature(FeatureHandler.extra)

        elif FeatureHandler.remove:
            FeatureHandler._check_path()
            Setup.remove_feature()

        elif FeatureHandler.dev:
            Shell.dev(FeatureHandler._handle_path())

        else:
            exit({"message": "Missing options", "parser": feature_parser})

        exit()

    @staticmethod
    def _handle_state():
        StateHandler.init(FeatureHandler.args)
        StateHandler.handle()

    @staticmethod
    def _handle_frame():
        FrameHandler.init(FeatureHandler.args)
        FrameHandler.handle()

    @staticmethod
    def _handle_task():
        TaskHandler.init(FeatureHandler.args)
        TaskHandler.handle()

    @staticmethod
    def handle():
        feature_name = FeatureHandler.feature_name

        if not feature_name:
            FeatureHandler._handle_options()
        else:
            if FeatureHandler.feature_cmd == "state":
                FeatureHandler._handle_state()

            if FeatureHandler.feature_cmd == "frame":
                FeatureHandler._handle_frame()

            if FeatureHandler.feature_cmd == "task":
                FeatureHandler._handle_task()


def handle_root_args(args):
    if args.root_cmd == "shell":
        ShellHandler.init(args)
        ShellHandler.handle()

    if args.root_cmd == "setup":
        SetupHandler.init(args)
        SetupHandler.handle()

    if args.root_cmd == "feature":
        FeatureHandler.init(args)
        FeatureHandler.handle()
