import os
from .Setup import Setup, SetupTask, Commands

# ---------------------------------------------- - - -
# Constants

VX_ENV = "/opt/vixen-env"

VX_FRONT_ARCHIVE_URL = (
    "https://github.com/vixen-shell/vx-front/archive/refs/heads/main.zip"
)


# ---------------------------------------------- - - -
# Install Vixen Shell


def vx_setup(library_path: str):
    Setup(
        purpose="Setup Vixen Shell",
        tasks=[
            # ---------------------------------------------- - - -
            # Vixen Shell Core
            #
            SetupTask(
                purpose="Create Vixen environment",
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
            SetupTask(
                purpose="Install dependencies",
                command=Commands.env_dependencies(VX_ENV, library_path),
            ),
            SetupTask(
                purpose="Install Vixen Shell library",
                command=Commands.env_install(VX_ENV, library_path),
            ),
            SetupTask(
                purpose="Remove build folders",
                command=Commands.folder_remove_build(library_path),
            ),
            SetupTask(
                purpose="Install Vixen Manager executable",
                command=Commands.file_copy(f"{library_path}/vxm", "/usr/bin/vxm", True),
                undo_command=Commands.file_remove("/usr/bin/vxm"),
            ),
            SetupTask(
                purpose="Patch Vixen Manager executable",
                command=Commands.env_path_executable(VX_ENV, "/usr/bin/vxm"),
            ),
            # ---------------------------------------------- - - -
            # Vixen front-end
            #
            SetupTask(
                purpose="Download Vixen Shell front-end",
                command=Commands.git_get_archive(VX_FRONT_ARCHIVE_URL, "/var/opt"),
                undo_command=Commands.folder_remove("/var/opt/vx-front-main"),
            ),
            SetupTask(
                purpose="Install Vixen Shell front-end dependencies",
                command=Commands.yarn_install("/var/opt/vx-front-main"),
            ),
            SetupTask(
                purpose="Build Vixen Shell front-end",
                command=Commands.yarn_build("/var/opt/vx-front-main"),
            ),
            # ---------------------------------------------- - - -
            # Root config
            #
            SetupTask(
                purpose="Setup root config",
                command=Commands.folder_copy(
                    f"{library_path}/config/root/vixen",
                    f"/usr/share",
                ),
                undo_command=Commands.folder_remove(f"/usr/share/vixen"),
            ),
            # ---------------------------------------------- - - -
            # User config
            #
            SetupTask(
                purpose="Setup user config",
                command=Commands.user(
                    Commands.folder_copy(
                        f"{library_path}/config/user/vixen",
                        f"/home/{os.getlogin()}/.config",
                    )
                ),
                undo_command=Commands.folder_remove(
                    f"/home/{os.getlogin()}/.config/vixen"
                ),
            ),
        ],
    ).run()


# ---------------------------------------------- - - -
# Uninstall Vixen Shell


def vx_remove():
    Setup(
        purpose="Remove Vixen Shell",
        tasks=[
            SetupTask(
                purpose="Remove root config",
                command=Commands.folder_remove(f"/usr/share/vixen"),
            ),
            SetupTask(
                purpose="Remove user config",
                command=Commands.folder_remove(f"/home/{os.getlogin()}/.config/vixen"),
            ),
            SetupTask(
                purpose="Remove Vixen Manager executable",
                command=Commands.file_remove("/usr/bin/vxm"),
            ),
            SetupTask(
                purpose="Remove Vixen Shell front-end",
                command=Commands.folder_remove("/var/opt/vx-front-main"),
            ),
            SetupTask(
                purpose="Remove Vixen Shell environment",
                command=Commands.folder_remove(VX_ENV),
            ),
        ],
    ).run()
