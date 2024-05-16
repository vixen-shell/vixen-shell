import os
from .classes import Commands, Routine, RoutineTask

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
    return Routine(
        purpose="Setup Vixen Shell",
        tasks=[
            # ---------------------------------------------- - - -
            # Vixen Shell Core
            #
            RoutineTask(
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
            RoutineTask(
                purpose="Install dependencies",
                command=Commands.env_dependencies(VX_ENV, library_path),
            ),
            RoutineTask(
                purpose="Install Vixen Shell library",
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
            # ---------------------------------------------- - - -
            # Vixen front-end
            #
            RoutineTask(
                purpose="Download Vixen Shell front-end",
                command=Commands.git_get_archive(VX_FRONT_ARCHIVE_URL, "/var/opt"),
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
            # Root config
            #
            RoutineTask(
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
            RoutineTask(
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
    return Routine(
        purpose="Remove Vixen Shell",
        tasks=[
            RoutineTask(
                purpose="Remove root config",
                command=Commands.folder_remove(f"/usr/share/vixen"),
            ),
            RoutineTask(
                purpose="Remove user config",
                command=Commands.folder_remove(f"/home/{os.getlogin()}/.config/vixen"),
            ),
            RoutineTask(
                purpose="Remove Vixen Manager executable",
                command=Commands.file_remove("/usr/bin/vxm"),
            ),
            RoutineTask(
                purpose="Remove Vixen Shell front-end",
                command=Commands.folder_remove("/var/opt/vx-front-main"),
            ),
            RoutineTask(
                purpose="Remove Vixen Shell environment",
                command=Commands.folder_remove(VX_ENV),
            ),
        ],
    ).run()


# ---------------------------------------------- - - -
# Create new feature


def vx_new_feature(path: str, project_name: str):
    return Routine(
        purpose="Create new feature",
        tasks=[
            RoutineTask(
                purpose="Download feature template",
                command=Commands.git_get_archive(VX_FEATURE_TEMPLATE_URL, "/tmp"),
            ),
            RoutineTask(
                purpose="Setup project folder",
                command=Commands.rename(
                    "/tmp/vx-feature-template-main", f"/tmp/{project_name}"
                ),
                undo_command=Commands.folder_remove(f"/tmp/{project_name}"),
            ),
            RoutineTask(
                purpose="Update project name in 'package.json' file",
                command=Commands.json_patch_feature_name_property(
                    f"/tmp/{project_name}/package.json", f"vx-feature-{project_name}"
                ),
            ),
            RoutineTask(
                purpose="Setup feature sources",
                command=Commands.rename(
                    f"/tmp/{project_name}/src/feature",
                    f"/tmp/{project_name}/src/{project_name}",
                ),
            ),
            RoutineTask(
                purpose="Setup root config module",
                command=Commands.rename(
                    f"/tmp/{project_name}/config/root/feature",
                    f"/tmp/{project_name}/config/root/{project_name}",
                ),
            ),
            RoutineTask(
                purpose="Setup user config file",
                command=Commands.rename(
                    f"/tmp/{project_name}/config/user/feature.json",
                    f"/tmp/{project_name}/config/user/{project_name}.json",
                ),
            ),
            RoutineTask(
                purpose="Install project dependencies",
                command=Commands.yarn_install(f"/tmp/{project_name}"),
            ),
            RoutineTask(
                purpose="Finalize feature project",
                command=Commands.folder_copy(f"/tmp/{project_name}", path),
                undo_command=Commands.folder_remove(f"{path}/{project_name}"),
            ),
            RoutineTask(
                purpose="Clean temporary files",
                command=Commands.folder_remove(f"/tmp/{project_name}"),
            ),
        ],
    ).run()


# ---------------------------------------------- - - -
# Add feature


def vx_add_feature(dev_dir: str, feature_name: str):
    return Routine(
        purpose="Add feature",
        tasks=[
            RoutineTask(
                purpose="Setup feature sources",
                command=Commands.folder_copy(
                    f"{dev_dir}/src/{feature_name}", "/var/opt/vx-front-main/src"
                ),
                undo_command=Commands.folder_remove(
                    f"/var/opt/vx-front-main/src/{feature_name}"
                ),
            ),
            RoutineTask(
                purpose="Setup root config file",
                command=Commands.file_copy(
                    f"{dev_dir}/config/root/{feature_name}.json",
                    "/usr/share/vixen/features",
                ),
                undo_command=Commands.file_remove(
                    f"/usr/share/vixen/features/{feature_name}.json"
                ),
            ),
            RoutineTask(
                purpose="Setup user config file",
                command=Commands.file_copy(
                    f"{dev_dir}/config/user/{feature_name}.json",
                    f"/home/{os.getlogin()}/.config/vixen/features",
                ),
                undo_command=Commands.file_remove(
                    f"/home/{os.getlogin()}/.config/vixen/features/{feature_name}.json"
                ),
            ),
            RoutineTask(
                purpose="Rebuild Vixen Shell front-end",
                command=Commands.yarn_build("/var/opt/vx-front-main"),
            ),
        ],
    ).run()


# ---------------------------------------------- - - -
# Remove feature


def vx_remove_feature(feature_name: str):
    return Routine(
        purpose=f"Remove feature '{feature_name}'",
        tasks=[
            RoutineTask(
                purpose="Remove feature sources",
                command=Commands.folder_remove(
                    f"/var/opt/vx-front-main/src/{feature_name}"
                ),
            ),
            RoutineTask(
                purpose="Remove root config file",
                command=Commands.file_remove(
                    f"/usr/share/vixen/features/{feature_name}.json"
                ),
            ),
            RoutineTask(
                purpose="Remove user config file",
                command=Commands.file_remove(
                    f"/home/{os.getlogin()}/.config/vixen/features/{feature_name}.json"
                ),
            ),
            RoutineTask(
                purpose="Rebuild Vixen Shell front-end",
                command=Commands.yarn_build("/var/opt/vx-front-main"),
            ),
        ],
    ).run()
