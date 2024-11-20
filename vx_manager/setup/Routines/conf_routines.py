import os
from glob import glob
from vx_path import VxPath
from ..classes import Routine, RoutineTask, Commands
from ...utils import write_json


def setup_config(library_path: str):
    desktop_entry_filenames: list[str] = []
    desktop_entry_tasks: list[RoutineTask] = []

    def create_desktop_entries_register():
        try:
            write_json(
                f"{VxPath.ROOT_FEATURE_MODULES}/basics_feature/apps.json",
                desktop_entry_filenames,
            )
            return True
        except:
            return False

    desktop_entry_filenames = [
        file
        for file in os.listdir(f"{library_path}/extras/apps")
        if file.endswith(".desktop")
    ]

    desktop_entry_tasks = [
        RoutineTask(
            purpose=f"Create '{filename}' desktop entry",
            command=Commands.file_copy(
                f"{library_path}/extras/apps/{filename}",
                VxPath.DESKTOP_ENTRIES,
            ),
            undo_command=Commands.file_remove(f"{VxPath.DESKTOP_ENTRIES}/{filename}"),
        )
        for filename in desktop_entry_filenames
    ] + [
        RoutineTask(
            purpose="Create desktop entries register",
            command=create_desktop_entries_register,
        )
    ]

    def user_config_file_tasks():
        config_file_paths = glob(f"{library_path}/extras/user/*.json")

        return [
            RoutineTask(
                purpose=f"Setup '{os.path.basename(file_path)}' user config file",
                command=Commands.file_copy(
                    file_path,
                    VxPath.USER_FEATURE_PARAMS,
                ),
                undo_command=Commands.file_remove(
                    f"{VxPath.USER_FEATURE_PARAMS}/{os.path.basename(file_path)}"
                ),
            )
            for file_path in config_file_paths
        ]

    return Routine(
        purpose="Setup Vixen Shell features",
        tasks=[
            # ---------------------------------------------- - - -
            # Phosphor icons
            #
            RoutineTask(
                purpose="Create Phosphor icons folder",
                command=Commands.folder_copy(
                    f"{library_path}/extras/phosphor", VxPath.ROOT_CONFIG
                ),
                undo_command=Commands.folder_remove(VxPath.ROOT_PHOSPHOR_ICONS),
            ),
            # ---------------------------------------------- - - -
            # Root config
            #
            RoutineTask(
                purpose="Create root modules folder",
                command=Commands.folder_copy(
                    f"{library_path}/extras/root/features", VxPath.ROOT_CONFIG
                ),
                undo_command=Commands.folder_remove(VxPath.ROOT_FEATURE_MODULES),
            ),
            # ---------------------------------------------- - - -
            # User config
            #
            RoutineTask(
                purpose="Create user config folder",
                command=Commands.user(
                    Commands.folder_create(VxPath.USER_FEATURE_PARAMS)
                ),
                undo_command=Commands.folder_remove(VxPath.USER_CONFIG),
            ),
        ]
        + user_config_file_tasks()
        + desktop_entry_tasks,
    ).run()
