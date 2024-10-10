import argparse

root_parser = argparse.ArgumentParser(description="Vixen Manager")
root_subparsers = root_parser.add_subparsers(dest="root_cmd", title="Root commands")

# --------------------------------- - - -
# SHELL PARSER
# --------------------------------- - - -
shell_parser = root_subparsers.add_parser("shell", help="Shell controls")
shell_parser.add_argument(
    "action", nargs="?", type=str, choices=["open", "close"], help="Shell controls"
)
shell_parser.add_argument(
    "--no-dmabuf", action="store_true", help="Disable DMABUF renderer"
)

# --------------------------------- - - -
# SETUP PARSER
# --------------------------------- - - -
setup_parser = root_subparsers.add_parser("setup", help="Setup controls")
setup_parser.add_argument(
    "action", type=str, choices=["update", "remove"], help="Setup controls"
)

# --------------------------------- - - -
# FEATURE PARSER
# --------------------------------- - - -
feature_parser = root_subparsers.add_parser("feature", help="Feature controls")
feature_parser.add_argument(
    "feature_name", nargs="?", type=str, metavar="NAME", help="The name of the feature"
)
feature_parser.add_argument(
    "--path",
    type=str,
    metavar="PATH",
    help="Set a path for the --add and --dev options",
)

feature_exclusive = feature_parser.add_mutually_exclusive_group()
feature_exclusive.add_argument(
    "--list", action="store_true", help="List all available features"
)
feature_exclusive.add_argument(
    "--new", action="store_true", help="Create a new feature"
)
feature_exclusive.add_argument(
    "--add", action="store_true", help="Add a feature to Vixen Shell"
)
feature_exclusive.add_argument(
    "--extra", type=str, metavar="NAME", help="Add an extra feature to Vixen Shell"
)
feature_exclusive.add_argument(
    "--remove", action="store_true", help="Remove a feature to Vixen Shell"
)
feature_exclusive.add_argument(
    "--dev", action="store_true", help="Run development server"
)

# --------------------------------- - - -
# --------------------------------- - - -
feature_subparser = feature_parser.add_subparsers(
    dest="feature_cmd", title="Frame commands"
)

# --------------------------------- - - -
# FRAME PARSER
# --------------------------------- - - -
frame_parser = feature_subparser.add_parser("frame", help="Feature frames controls")
frame_parser.add_argument(
    "frame_name", nargs="?", type=str, metavar="NAME", help="The name of the frame"
)

frame_exclusive = frame_parser.add_mutually_exclusive_group()
frame_exclusive.add_argument(
    "--list", action="store_true", help="List all available feature frames"
)
frame_exclusive.add_argument("--toggle", action="store_true", help="Toggle a frame")
frame_exclusive.add_argument("--open", action="store_true", help="Open a frame")
frame_exclusive.add_argument("--close", action="store_true", help="Close a frame")


# --------------------------------- - - -
# TASK PARSER
# --------------------------------- - - -
def parse_mixed_type(value):
    if value.lower() == "none":
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


task_parser = feature_subparser.add_parser("task", help="Feature task controls")
task_parser.add_argument(
    "task_name", nargs="?", type=str, metavar="NAME", help="The name of the task to run"
)
task_parser.add_argument(
    "--args",
    type=parse_mixed_type,
    nargs="+",
    help="Task arguments (str, int, float, none)",
)

task_exclusive = task_parser.add_mutually_exclusive_group()
task_exclusive.add_argument(
    "--list", action="store_true", help="List all available feature tasks"
)
