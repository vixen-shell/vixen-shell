import os
from .classes import Commands, Routine, RoutineTask

# ---------------------------------------------- - - -
# Constants

VX_ENV = "/opt/vixen-env"


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


def vx_new_feature(path: str, project_name: str, front_end: bool):
    front_purpose = f" ({'no ' if not front_end else ''}front-end)"
    tmp_project_dir = f"/tmp/vx_feature_{project_name}"

    return Routine(
        purpose="Create feature project development: " + project_name + front_purpose,
        tasks=[
            # ---------------------------------------------- - - -
            # Project Folder
            #
            RoutineTask(
                purpose="Download feature template",
                command=Commands.git_get_archive(
                    "/tmp",
                    (
                        "vx-feature-template"
                        if front_end
                        else "vx-feature-no-front-template"
                    ),
                ),
            ),
            RoutineTask(
                purpose="Setup project folder",
                command=Commands.rename(
                    (
                        "/tmp/vx-feature-template-main"
                        if front_end
                        else "/tmp/vx-feature-no-front-template-main"
                    ),
                    tmp_project_dir,
                ),
                undo_command=Commands.folder_remove(tmp_project_dir),
            ),
            # ---------------------------------------------- - - -
            # Project Config
            #
            RoutineTask(
                purpose="Setup root config module",
                command=Commands.rename(
                    f"{tmp_project_dir}/config/root/feature",
                    f"{tmp_project_dir}/config/root/{project_name}",
                ),
            ),
            RoutineTask(
                purpose="Setup user config file",
                command=Commands.rename(
                    f"{tmp_project_dir}/config/user/feature.json",
                    f"{tmp_project_dir}/config/user/{project_name}.json",
                ),
            ),
            # ---------------------------------------------- - - -
            # Front-end Sources
            #
            RoutineTask(
                purpose="Update project name in 'package.json' file",
                command=Commands.json_patch_feature_name_property(
                    f"{tmp_project_dir}/package.json", f"vx-feature-{project_name}"
                ),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
            RoutineTask(
                purpose="Setup feature sources",
                command=Commands.rename(
                    f"{tmp_project_dir}/src/feature",
                    f"{tmp_project_dir}/src/{project_name}",
                ),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
            RoutineTask(
                purpose="Install project dependencies",
                command=Commands.yarn_install(tmp_project_dir),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
            # ---------------------------------------------- - - -
            # Finalize Project
            #
            RoutineTask(
                purpose="Finalize feature project",
                command=Commands.folder_copy(tmp_project_dir, path),
                undo_command=Commands.folder_remove(
                    f"{path}/vx-feature-{project_name}"
                ),
            ),
            RoutineTask(
                purpose="Clean temporary files",
                command=Commands.folder_remove(tmp_project_dir),
            ),
        ],
    ).run()


# ---------------------------------------------- - - -
# Add feature


def vx_add_feature(dev_dir: str, feature_name: str):
    front_end = os.path.exists(f"{dev_dir}/package.json") and os.path.exists(
        f"{dev_dir}/src/{feature_name}"
    )

    return Routine(
        purpose=f"Add feature '{feature_name}' to Vixen Shell",
        tasks=[
            # ---------------------------------------------- - - -
            # Feature Config
            #
            RoutineTask(
                purpose="Setup root config module",
                command=Commands.folder_copy(
                    f"{dev_dir}/config/root/{feature_name}",
                    "/usr/share/vixen/features",
                ),
                undo_command=Commands.folder_remove(
                    f"/usr/share/vixen/features/{feature_name}"
                ),
                requirements=[
                    {
                        "purpose": "Check an existing root config module",
                        "callback": Commands.Checkers.folder(
                            f"{dev_dir}/config/root/{feature_name}", True
                        ),
                        "failure_message": "Root config module not found",
                    }
                ],
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
                skip_on={
                    "callback": Commands.Checkers.file(
                        f"{dev_dir}/config/user/{feature_name}.json", False
                    ),
                    "message": "User config file not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Feature Front-end Sources
            #
            RoutineTask(
                purpose="Setup feature front-end sources",
                command=Commands.folder_copy(
                    f"{dev_dir}/src/{feature_name}", "/var/opt/vx-front-main/src"
                ),
                undo_command=Commands.folder_remove(
                    f"/var/opt/vx-front-main/src/{feature_name}"
                ),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
            RoutineTask(
                purpose="Rebuild Vixen Shell front-end",
                command=Commands.yarn_build("/var/opt/vx-front-main"),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
        ],
    ).run()


# ---------------------------------------------- - - -
# Remove feature


def vx_remove_feature(feature_name: str):
    front_end = os.path.exists(f"/var/opt/vx-front-main/src/{feature_name}")

    return Routine(
        purpose=f"Remove feature '{feature_name}'",
        tasks=[
            # ---------------------------------------------- - - -
            # Feature Config
            #
            RoutineTask(
                purpose="Remove root config module",
                command=Commands.folder_remove(
                    f"/usr/share/vixen/features/{feature_name}"
                ),
            ),
            RoutineTask(
                purpose="Remove user config file",
                command=Commands.file_remove(
                    f"/home/{os.getlogin()}/.config/vixen/features/{feature_name}.json"
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        f"/home/{os.getlogin()}/.config/vixen/features/{feature_name}.json",
                        False,
                    ),
                    "message": "User config file not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Feature Front-end Sources
            #
            RoutineTask(
                purpose="Remove feature front-end sources",
                command=Commands.folder_remove(
                    f"/var/opt/vx-front-main/src/{feature_name}"
                ),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
            RoutineTask(
                purpose="Rebuild Vixen Shell front-end",
                command=Commands.yarn_build("/var/opt/vx-front-main"),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
        ],
    ).run()
