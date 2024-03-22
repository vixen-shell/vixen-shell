import os
from .Setup import Setup, SetupTask, Commands

# ---------------------------------------------- - - -
# Constants

VX_ENV_DIR = "/opt/vixen-env"
VX_LIB_NAME = "vx_library"
VXM_EXEC_NAME = "vxm"
VXM_EXEC_DEST = "/usr/bin"
VXM_EXEC_PATH = f"{VXM_EXEC_DEST}/{VXM_EXEC_NAME}"
VAR_OPT = "/var/opt"
VX_FRONT_DIR = f"{VAR_OPT}/vx-front-main"
VX_USER_CONFIG_SOURCE = f"{VX_FRONT_DIR}/user_config/vixen"
VX_USER_CONFIG_DEST = f"/home/{os.getlogin()}/.config"

# Git
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
                command=Commands.env_create(VX_ENV_DIR),
                undo_command=Commands.folder_remove(VX_ENV_DIR),
                requirements=[
                    {
                        "purpose": "Check an existing environment folder",
                        "callback": Commands.Checkers.folder(VX_ENV_DIR, False),
                        "failure_message": f"Environment folder already exists",
                    }
                ],
            ),
            SetupTask(
                purpose="Install dependencies",
                command=Commands.env_dependencies(VX_ENV_DIR, library_path),
            ),
            SetupTask(
                purpose="Install Vixen Shell library",
                command=Commands.env_install(VX_ENV_DIR, library_path),
            ),
            SetupTask(
                purpose="Remove build folders",
                command=Commands.folder_remove_build(library_path),
            ),
            SetupTask(
                purpose="Install Vixen Manager executable",
                command=Commands.file_copy(
                    f"{library_path}/{VXM_EXEC_NAME}", VXM_EXEC_DEST, True
                ),
                undo_command=Commands.file_remove(VXM_EXEC_PATH),
            ),
            SetupTask(
                purpose="Patch Vixen Manager executable",
                command=Commands.env_path_executable(VX_ENV_DIR, VXM_EXEC_PATH),
            ),
            # ---------------------------------------------- - - -
            # Vixen front-end
            #
            SetupTask(
                purpose="Download Vixen Shell front-end",
                command=Commands.git_get_archive(VX_FRONT_ARCHIVE_URL, VAR_OPT),
                undo_command=Commands.folder_remove(VX_FRONT_DIR),
            ),
            SetupTask(
                purpose="Install Vixen Shell front-end dependencies",
                command=Commands.yarn_install(VX_FRONT_DIR),
            ),
            SetupTask(
                purpose="Build Vixen Shell front-end",
                command=Commands.yarn_build(VX_FRONT_DIR),
            ),
            # ---------------------------------------------- - - -
            # User config
            #
            SetupTask(
                purpose="Setup user config",
                command=Commands.user(
                    Commands.folder_copy(VX_USER_CONFIG_SOURCE, VX_USER_CONFIG_DEST)
                ),
                undo_command=Commands.folder_remove(f"{VX_USER_CONFIG_DEST}/vixen"),
                requirements=[
                    {
                        "purpose": "Check an existing user config folder",
                        "callback": Commands.Checkers.folder(
                            f"{VX_USER_CONFIG_DEST}/vixen", False
                        ),
                        "failure_message": "User config folder already exists",
                        "issue": {
                            "purpose": "Remove existing user config folder",
                            "command": Commands.folder_remove(
                                f"{VX_USER_CONFIG_DEST}/vixen"
                            ),
                        },
                    }
                ],
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
                purpose="Remove user config",
                command=Commands.folder_remove(f"{VX_USER_CONFIG_DEST}/vixen"),
            ),
            SetupTask(
                purpose="Remove Vixen Manager executable",
                command=Commands.file_remove(VXM_EXEC_PATH),
            ),
            SetupTask(
                purpose="Remove Vixen Shell front-end",
                command=Commands.folder_remove(VX_FRONT_DIR),
            ),
            SetupTask(
                purpose="Remove Vixen Shell environment",
                command=Commands.folder_remove(VX_ENV_DIR),
            ),
        ],
    ).run()
