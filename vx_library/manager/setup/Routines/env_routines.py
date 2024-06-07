import os
from ..classes import Routine, RoutineTask, Commands

# ---------------------------------------------- - - -
# Constants

VX_ENV = "/opt/vixen-env"


def setup_environment(library_path: str):
    return Routine(
        purpose="Setup Vixen Shell environment",
        tasks=[
            # ---------------------------------------------- - - -
            # Create Environment
            #
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
                purpose="Install Vixen Shell dependencies",
                command=Commands.env_dependencies(
                    VX_ENV, f"{library_path}/requirements.txt"
                ),
            ),
            # ---------------------------------------------- - - -
            # Backup Package List
            #
            RoutineTask(
                purpose="Create shared Vixen folder",
                command=Commands.folder_create("/usr/share/vixen"),
                undo_command=Commands.folder_remove(f"/usr/share/vixen"),
            ),
            RoutineTask(
                purpose="Freeze environment dependencies",
                command=Commands.env_freeze(
                    VX_ENV, "/usr/share/vixen/vixen_requirements.txt"
                ),
            ),
            # ---------------------------------------------- - - -
            # Install Vixen Shell Libraries
            #
            RoutineTask(
                purpose="Install Vixen Shell libraries",
                command=Commands.env_install(VX_ENV, library_path),
            ),
            RoutineTask(
                purpose="Remove build folders",
                command=Commands.folder_remove_build(library_path),
            ),
            # ---------------------------------------------- - - -
            # Install Vxm
            #
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
    download_path = "/tmp/vx_update/vixen-shell-main"

    return Routine(
        purpose="Update Vixen Shell environment",
        tasks=[
            # ---------------------------------------------- - - -
            # Backup current setup
            #
            RoutineTask(
                purpose="Init current environment backup",
                command=Commands.folder_create("/tmp/vx_update"),
                undo_command=Commands.folder_remove("/tmp/vx_update"),
            ),
            RoutineTask(
                purpose="Backup current environment",
                command=Commands.folder_copy(VX_ENV, "/tmp/vx_update"),
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
                command=Commands.file_copy("/usr/bin/vxm", "/tmp/vx_update/vxm", True),
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
                command=Commands.git_get_archive("/tmp/vx_update", "vixen-shell"),
                undo_command=Commands.folder_remove(download_path),
            ),
            # ---------------------------------------------- - - -
            # Clean current setup
            #
            RoutineTask(
                purpose="Clean current environment",
                command=Commands.folder_remove(VX_ENV),
                undo_command=Commands.folder_copy("/tmp/vx_update/vixen-env", "/opt"),
            ),
            # ---------------------------------------------- - - -
            # Update Environment
            #
            RoutineTask(
                purpose="Update environment",
                command=Commands.env_create(VX_ENV),
                undo_command=Commands.folder_remove(VX_ENV),
            ),
            RoutineTask(
                purpose="Install environment dependencies",
                command=Commands.env_dependencies(
                    VX_ENV, f"{download_path}/requirements.txt"
                ),
            ),
            # ---------------------------------------------- - - -
            # Backup Package List
            #
            RoutineTask(
                purpose="Freeze environment dependencies",
                command=Commands.env_freeze(
                    VX_ENV, "/usr/share/vixen/vixen_requirements.txt"
                ),
            ),
            # ---------------------------------------------- - - -
            # Restore Feature Requirements
            #
            RoutineTask(
                purpose="Restore feature dependencies",
                command=Commands.env_dependencies(
                    VX_ENV, "/usr/share/vixen/feature_requirements.txt"
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        "/usr/share/vixen/feature_requirements.txt", False
                    ),
                    "message": "Feature requirements not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Update Feature Requirements
            #
            RoutineTask(
                purpose="List feature dependencies",
                command=Commands.env_freeze(
                    VX_ENV, "/tmp/vx_update/tmp_vx_requirements.txt"
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        "/usr/share/vixen/feature_requirements.txt", False
                    ),
                    "message": "Feature requirements not found",
                },
            ),
            RoutineTask(
                purpose="Update feature requirements",
                command=Commands.env_freeze_added(
                    "/tmp/vx_update/tmp_vx_requirements.txt",
                    "/usr/share/vixen/feature_requirements.txt",
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        "/usr/share/vixen/feature_requirements.txt", False
                    ),
                    "message": "Feature requirements not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Install Vixen Shell Libraries
            #
            RoutineTask(
                purpose="Install Vixen Shell libraries",
                command=Commands.env_install(VX_ENV, download_path),
            ),
            # ---------------------------------------------- - - -
            # Install Vxm
            #
            RoutineTask(
                purpose="Install Vixen Manager executable",
                command=Commands.file_copy(
                    f"{download_path}/vxm", "/usr/bin/vxm", True
                ),
                undo_command=Commands.file_copy(
                    "/tmp/vx_update/vxm", "/usr/bin/vxm", True
                ),
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
                command=Commands.folder_remove("/tmp/vx_update"),
            ),
        ],
    ).run()


def install_environment_package(package_name: str):
    return Routine(
        purpose="Install environment python package",
        tasks=[
            # ---------------------------------------------- - - -
            # Install Package
            #
            RoutineTask(
                purpose=f"Install '{package_name}'",
                command=Commands.env_install(VX_ENV, package_name),
                undo_command=Commands.env_remove(VX_ENV, package_name),
                show_output=True,
            ),
            # ---------------------------------------------- - - -
            # Update Feature Requirements
            #
            RoutineTask(
                purpose="List new feature dependencies",
                command=Commands.env_freeze(VX_ENV, "/tmp/tmp_vx_requirements.txt"),
                undo_command=Commands.file_remove("/tmp/tmp_vx_requirements.txt"),
            ),
            RoutineTask(
                purpose="Update feature requirements",
                command=Commands.env_freeze_added(
                    "/tmp/tmp_vx_requirements.txt",
                    "/usr/share/vixen/feature_requirements.txt",
                ),
            ),
            # ---------------------------------------------- - - -
            # Clean tmp
            #
            RoutineTask(
                purpose="Clean up temporary files",
                command=Commands.file_remove("/tmp/tmp_vx_requirements.txt"),
            ),
        ],
    ).run()


def uninstall_environment_package(package_name: str):
    return Routine(
        purpose="Uninstall environment python package",
        tasks=[
            # ---------------------------------------------- - - -
            # Remove Package
            #
            RoutineTask(
                purpose=f"Uninstall '{package_name}'",
                command=Commands.env_remove(VX_ENV, package_name),
                undo_command=Commands.env_install(VX_ENV, package_name),
                show_output=True,
            ),
            # ---------------------------------------------- - - -
            # Update Feature Requirements
            #
            RoutineTask(
                purpose="List new feature dependencies",
                command=Commands.env_freeze(VX_ENV, "/tmp/tmp_vx_requirements.txt"),
                undo_command=Commands.file_remove("/tmp/tmp_vx_requirements.txt"),
            ),
            RoutineTask(
                purpose="Update feature requirements",
                command=Commands.env_freeze_added(
                    "/tmp/tmp_vx_requirements.txt",
                    "/usr/share/vixen/feature_requirements.txt",
                ),
            ),
            # ---------------------------------------------- - - -
            # Clean tmp
            #
            RoutineTask(
                purpose="Clean up temporary files",
                command=Commands.file_remove("/tmp/tmp_vx_requirements.txt"),
            ),
        ],
    ).run()


def remove_all():
    return Routine(
        purpose="Remove Vixen Shell",
        tasks=[
            RoutineTask(
                purpose="Remove root modules",
                command=Commands.folder_remove("/usr/share/vixen"),
                skip_on={
                    "callback": Commands.Checkers.folder("/usr/share/vixen", False),
                    "message": "Root modules folder not found",
                },
            ),
            RoutineTask(
                purpose="Remove user config",
                command=Commands.folder_remove(f"/home/{os.getlogin()}/.config/vixen"),
                skip_on={
                    "callback": Commands.Checkers.folder(
                        f"/home/{os.getlogin()}/.config/vixen", False
                    ),
                    "message": "User config folder not found",
                },
            ),
            RoutineTask(
                purpose="Remove Vixen Manager executable",
                command=Commands.file_remove("/usr/bin/vxm"),
                skip_on={
                    "callback": Commands.Checkers.file("/usr/bin/vxm", False),
                    "message": "Executable not found",
                },
            ),
            RoutineTask(
                purpose="Remove Vixen Shell front-end",
                command=Commands.folder_remove("/var/opt/vx-front-main"),
                skip_on={
                    "callback": Commands.Checkers.folder(
                        "/var/opt/vx-front-main", False
                    ),
                    "message": "Vixen Shell front-end not found",
                },
            ),
            RoutineTask(
                purpose="Remove Vixen Shell environment",
                command=Commands.folder_remove(VX_ENV),
                skip_on={
                    "callback": Commands.Checkers.folder(VX_ENV, False),
                    "message": "Vixen Shell environment not found",
                },
            ),
        ],
    ).run()
