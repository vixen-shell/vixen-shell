from vx_path import VxPath
from ..classes import Routine, RoutineTask, Commands


def setup_config(library_path: str):
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
        ],
    ).run()
