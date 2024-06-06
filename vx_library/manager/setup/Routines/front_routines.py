from ..classes import Commands, Routine, RoutineTask


def setup_front():
    return Routine(
        purpose="Setup Vixen Shell front-end",
        tasks=[
            RoutineTask(
                purpose="Download Vixen Shell front-end",
                command=Commands.git_get_archive("/var/opt", "vx-front"),
                undo_command=Commands.folder_remove("/var/opt/vx-front-main"),
                requirements=[
                    {
                        "purpose": "Check an existing front-end folder",
                        "callback": Commands.Checkers.folder(
                            "/var/opt/vx-front-main", False
                        ),
                        "failure_message": f"Front-end folder already exists",
                    }
                ],
            ),
            RoutineTask(
                purpose="Install Vixen Shell front-end dependencies",
                command=Commands.yarn_install("/var/opt/vx-front-main"),
            ),
            RoutineTask(
                purpose="Build Vixen Shell front-end",
                command=Commands.yarn_build("/var/opt/vx-front-main"),
            ),
        ],
    ).run()


def update_front():
    return Routine(
        purpose="Setup Vixen Shell",
        tasks=[
            # ---------------------------------------------- - - -
            # Backup current setup
            #
            RoutineTask(
                purpose="Backup current front-end",
                command=Commands.folder_copy("/var/opt/vx-front-main", "/tmp"),
                undo_command=Commands.folder_remove("/tmp/vx-front-main"),
                requirements=[
                    {
                        "purpose": "Check an existing front-end folder",
                        "callback": Commands.Checkers.folder(
                            "/var/opt/vx-front-main", True
                        ),
                        "failure_message": f"Front-end folder not found",
                    }
                ],
            ),
            # ---------------------------------------------- - - -
            # Clean current setup
            #
            RoutineTask(
                purpose="Clean current front-end",
                command=Commands.folder_remove("/var/opt/vx-front-main"),
                undo_command=Commands.folder_copy("/tmp/vx-front-main", "/var/opt"),
            ),
            # ---------------------------------------------- - - -
            # Updates
            #
            RoutineTask(
                purpose="Download Vixen Shell front-end",
                command=Commands.git_get_archive("/var/opt", "vx-front"),
                undo_command=Commands.folder_remove("/var/opt/vx-front-main"),
            ),
            RoutineTask(
                purpose="Install Vixen Shell front-end dependencies",
                command=Commands.yarn_install("/var/opt/vx-front-main"),
            ),
            RoutineTask(
                purpose="Build Vixen Shell front-end",
                command=Commands.yarn_build("/var/opt/vx-front-main"),
            ),
            # ---------------------------------------------- - - -
            # Clean tmp
            #
            RoutineTask(
                purpose="Clean up temporary files",
                command=Commands.folder_remove("/tmp/vx-front-main"),
            ),
        ],
    ).run()
