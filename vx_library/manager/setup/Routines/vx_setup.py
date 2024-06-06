import os
from ..classes import Routine, RoutineTask, Commands

# ---------------------------------------------- - - -
# Constants

VX_ENV = "/opt/vixen-env"


def setup_environment(library_path: str):
    return Routine(
        purpose="Setup Vixen Shell environment",
        tasks=[
            RoutineTask(
                purpose="Create environment",
                command=Commands.env_create(VX_ENV),
                undo_command=Commands.folder_remove(VX_ENV),
                requirements=[
                    {
                        "purpose": "Check an existing environment folder",
                        "callback": Commands.Checkers.folder(VX_ENV, False),
                        "failure_message": f"Environment folder already exists",
                    }
                ],
            ),
            RoutineTask(
                purpose="Install environment dependencies",
                command=Commands.env_dependencies(VX_ENV, library_path),
            ),
            RoutineTask(
                purpose="Install Vixen Shell libraries",
                command=Commands.env_install(VX_ENV, library_path),
            ),
            RoutineTask(
                purpose="Remove build folders",
                command=Commands.folder_remove_build(library_path),
            ),
            RoutineTask(
                purpose="Install Vixen Manager executable",
                command=Commands.file_copy(f"{library_path}/vxm", "/usr/bin/vxm", True),
                undo_command=Commands.file_remove("/usr/bin/vxm"),
            ),
            RoutineTask(
                purpose="Patch Vixen Manager executable",
                command=Commands.env_path_executable(VX_ENV, "/usr/bin/vxm"),
            ),
        ],
    ).run()


def update_environment():
    download_path = "/tmp/vixen-shell-main"

    return Routine(
        purpose="Update Vixen Shell environment",
        tasks=[
            # ---------------------------------------------- - - -
            # Backup current setup
            #
            RoutineTask(
                purpose="Backup current environment",
                command=Commands.file_copy(VX_ENV, "/tmp"),
                undo_command=Commands.folder_remove("/tmp/vixen-env"),
                requirements=[
                    {
                        "purpose": "Check an existing environment folder",
                        "callback": Commands.Checkers.folder(VX_ENV, True),
                        "failure_message": f"Environment folder not found",
                    }
                ],
            ),
            RoutineTask(
                purpose="Backup Vixen Manager executable",
                command=Commands.file_copy("/usr/bin/vxm", "/tmp/vxm", True),
                undo_command=Commands.file_remove("/tmp/vxm"),
                requirements=[
                    {
                        "purpose": "Check an existing Manager executable",
                        "callback": Commands.Checkers.file("/usr/bin/vxm", True),
                        "failure_message": f"Vixen Manager executable not found",
                    }
                ],
            ),
            # ---------------------------------------------- - - -
            # Download updates
            #
            RoutineTask(
                purpose="Download Vixen environment",
                command=Commands.git_get_archive("/tmp", "vixen-shell"),
                undo_command=Commands.folder_remove(download_path),
            ),
            # ---------------------------------------------- - - -
            # Clean current setup
            #
            RoutineTask(
                purpose="Clean current environment",
                command=Commands.folder_remove(VX_ENV),
                undo_command=Commands.folder_copy("/tmp/vixen-env", "/opt"),
            ),
            # ---------------------------------------------- - - -
            # Updates
            #
            RoutineTask(
                purpose="Update environment",
                command=Commands.env_create(VX_ENV),
                undo_command=Commands.folder_remove(VX_ENV),
            ),
            RoutineTask(
                purpose="Install environment dependencies",
                command=Commands.env_dependencies(VX_ENV, download_path),
            ),
            RoutineTask(
                purpose="Install Vixen Shell libraries",
                command=Commands.env_install(VX_ENV, download_path),
            ),
            RoutineTask(
                purpose="Install Vixen Manager executable",
                command=Commands.file_copy(
                    f"{download_path}/vxm", "/usr/bin/vxm", True
                ),
                undo_command=Commands.file_copy("/tmp/vxm", "/usr/bin/vxm", True),
            ),
            RoutineTask(
                purpose="Patch Vixen Manager executable",
                command=Commands.env_path_executable(VX_ENV, "/usr/bin/vxm"),
            ),
            # ---------------------------------------------- - - -
            # Clean tmp
            #
            RoutineTask(
                purpose="Clean up temporary files",
                command=f"{Commands.folder_remove("/tmp/vixen-env")} && {Commands.file_remove("/tmp/vxm")}",
            ),
        ],
    ).run()
