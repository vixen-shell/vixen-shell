import os
from ..classes import Routine, RoutineTask, Commands


def setup_config():
    return Routine(
        purpose="Setup Vixen Shell features",
        tasks=[
            # ---------------------------------------------- - - -
            # Root config
            #
            RoutineTask(
                purpose="Create root modules folder",
                command=Commands.folder_create("/usr/share/vixen/features"),
                undo_command=Commands.folder_remove(f"/usr/share/vixen"),
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
