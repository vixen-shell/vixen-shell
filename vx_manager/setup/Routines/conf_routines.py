import os
from ..classes import Routine, RoutineTask, Commands


def setup_config(library_path: str):
    return Routine(
        purpose="Setup Vixen Shell features",
        tasks=[
            # ---------------------------------------------- - - -
            # Root config
            #
            RoutineTask(
                purpose="Create root modules folder",
                command=Commands.folder_copy(
                    f"{library_path}/extras/root/features", "/usr/share/vixen"
                ),
                undo_command=Commands.folder_remove(f"/usr/share/vixen/features"),
            ),
            # ---------------------------------------------- - - -
            # User config
            #
            RoutineTask(
                purpose="Create user config folder",
                command=Commands.user(
                    Commands.folder_create(
                        f"/home/{os.getlogin()}/.config/vixen/features"
                    )
                ),
                undo_command=Commands.folder_remove(
                    f"/home/{os.getlogin()}/.config/vixen"
                ),
            ),
        ],
    ).run()
