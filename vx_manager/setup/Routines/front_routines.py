import grp
from vx_path import VxPath
from ..classes import Commands, Routine, RoutineTask


def setup_front():
    def group_exists_callback(group_name):
        def group_exists():
            try:
                grp.getgrnam(group_name)
                return True
            except KeyError:
                return False

        return group_exists

    return Routine(
        purpose="Setup Vixen Shell front-end",
        tasks=[
            RoutineTask(
                purpose="Download Vixen Shell front-end",
                command=Commands.git_get_archive(VxPath.FRONT_PARENT, "vx-front"),
                undo_command=Commands.folder_remove(VxPath.FRONT),
                requirements=[
                    {
                        "purpose": "Check an existing front-end folder",
                        "callback": Commands.Checkers.folder(VxPath.FRONT, False),
                        "failure_message": f"Front-end folder already exists",
                    }
                ],
            ),
            RoutineTask(
                purpose="Install Vixen Shell front-end dependencies",
                command=Commands.yarn_install(VxPath.FRONT),
            ),
            RoutineTask(
                purpose="Build Vixen Shell front-end",
                command=Commands.yarn_build(VxPath.FRONT),
            ),
            RoutineTask(
                purpose="Create the development system group",
                command=Commands.create_vixen_system_group(),
                skip_on={
                    "callback": group_exists_callback("vx_devs"),
                    "message": "Development system group already exists",
                },
            ),
            RoutineTask(
                purpose="Allow development system group",
                command=Commands.front_modules_permissions(
                    f"{VxPath.FRONT}/node_modules"
                ),
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
                command=Commands.folder_copy(VxPath.FRONT, "/tmp"),
                undo_command=Commands.folder_remove(f"/tmp/{VxPath.front_name}"),
                requirements=[
                    {
                        "purpose": "Check an existing front-end folder",
                        "callback": Commands.Checkers.folder(VxPath.FRONT, True),
                        "failure_message": f"Front-end folder not found",
                    }
                ],
            ),
            # ---------------------------------------------- - - -
            # Clean current setup
            #
            RoutineTask(
                purpose="Clean current front-end",
                command=Commands.folder_remove(VxPath.FRONT),
                undo_command=Commands.folder_copy(
                    f"/tmp/{VxPath.front_name}", VxPath.FRONT_PARENT
                ),
            ),
            # ---------------------------------------------- - - -
            # Updates
            #
            RoutineTask(
                purpose="Download Vixen Shell front-end",
                command=Commands.git_get_archive(VxPath.FRONT_PARENT, "vx-front"),
                undo_command=Commands.folder_remove(VxPath.FRONT),
            ),
            RoutineTask(
                purpose="Install Vixen Shell front-end dependencies",
                command=Commands.yarn_install(VxPath.FRONT),
            ),
            # ---------------------------------------------- - - -
            # Restore feature front-ends
            #
            RoutineTask(
                purpose="Restore feature front-ends",
                command=Commands.folder_copy(
                    f"/tmp/{VxPath.front_name}/src/features",
                    VxPath.FRONT_SOURCES,
                    True,
                ),
            ),
            # ---------------------------------------------- - - -
            # Build front-end
            #
            RoutineTask(
                purpose="Build Vixen Shell front-end",
                command=Commands.yarn_build(VxPath.FRONT),
            ),
            # ---------------------------------------------- - - -
            # Clean tmp
            #
            RoutineTask(
                purpose="Clean up temporary files",
                command=Commands.folder_remove(f"/tmp/{VxPath.front_name}"),
            ),
        ],
    ).run()
