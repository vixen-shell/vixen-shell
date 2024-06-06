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
                purpose="Setup root config",
                command=Commands.folder_create("/usr/share/vixen/features"),
                undo_command=Commands.folder_remove(f"/usr/share/vixen"),
            ),
            # ---------------------------------------------- - - -
            # User config
            #
            RoutineTask(
                purpose="Setup user config",
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
