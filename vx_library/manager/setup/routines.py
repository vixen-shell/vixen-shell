import os
from .Setup import Setup, SetupTask, Commands

# ---------------------------------------------- - - -
# Constants

VX_ENV = "/opt/vixen-env"

VX_FRONT_ARCHIVE_URL = (
    "https://github.com/vixen-shell/vx-front/archive/refs/heads/main.zip"
)
VX_FEATURE_TEMPLATE_URL = (
    "https://github.com/vixen-shell/vx-feature-template/archive/refs/heads/main.zip"
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


# ---------------------------------------------- - - -
# Create new feature


def vx_new_feature(path: str, project_name: str):
    return Setup(
        purpose="Create new feature",
        tasks=[
            SetupTask(
                purpose="Download feature template",
                command=Commands.git_get_archive(VX_FEATURE_TEMPLATE_URL, "/tmp"),
            ),
            SetupTask(
                purpose="Setup project folder",
                command=Commands.rename(
                    "/tmp/vx-feature-template-main", f"/tmp/{project_name}"
                ),
                undo_command=Commands.folder_remove(f"/tmp/{project_name}"),
            ),
            SetupTask(
                purpose="Patch package file",
                command=Commands.json_patch_feature_name_property(
                    f"/tmp/{project_name}/package.json", f"vx-feature-{project_name}"
                ),
            ),
            SetupTask(
                purpose="Setup feature source",
                command=Commands.rename(
                    f"/tmp/{project_name}/src/feature",
                    f"/tmp/{project_name}/src/{project_name}",
                ),
            ),
            SetupTask(
                purpose="Setup root config file",
                command=Commands.rename(
                    f"/tmp/{project_name}/config/root/feature.json",
                    f"/tmp/{project_name}/config/root/{project_name}.json",
                ),
            ),
            SetupTask(
                purpose="Patch root config file",
                command=Commands.json_patch_feature_name_property(
                    f"/tmp/{project_name}/config/root/{project_name}.json", project_name
                ),
            ),
            SetupTask(
                purpose="Setup user config file",
                command=Commands.rename(
                    f"/tmp/{project_name}/config/user/feature.json",
                    f"/tmp/{project_name}/config/user/{project_name}.json",
                ),
            ),
            SetupTask(
                purpose="Install project dependencies",
                command=Commands.yarn_install(f"/tmp/{project_name}"),
            ),
            SetupTask(
                purpose="Finalize feature project",
                command=Commands.folder_copy(f"/tmp/{project_name}", path),
                undo_command=Commands.folder_remove(f"{path}/{project_name}"),
            ),
            SetupTask(
                purpose="Clean temporary files",
                command=Commands.folder_remove(f"/tmp/{project_name}"),
            ),
        ],
    ).run()
