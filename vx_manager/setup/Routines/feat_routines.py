import os
from glob import glob
from vx_path import VxPath
from ..classes import Commands, Routine, RoutineTask
from ...utils import write_json, read_json

# ---------------------------------------------- - - -
# Create new feature


def vx_new_feature(path: str, project_name: str, front_end: bool):
    front_purpose = f" ({'no ' if not front_end else ''}front-end)"
    tmp_project_dir = f"/tmp/vx-feature-{project_name[:-8]}"

    def create_vscode_settings() -> bool:
        try:
            write_json(
                f"{tmp_project_dir}/.vscode/settings.json",
                {
                    "python.analysis.extraPaths": glob(
                        f"{VxPath.ENV}/lib/python*/site-packages"
                    )
                    + [VxPath.ROOT_FEATURE_MODULES],
                    "python.autoComplete.extraPaths": glob(
                        f"{VxPath.ENV}/lib/python*/site-packages"
                    )
                    + [VxPath.ROOT_FEATURE_MODULES],
                },
            )
            return True
        except:
            return False

    return Routine(
        purpose="Create feature project development: "
        + project_name[:-8]
        + front_purpose,
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
                    f"{tmp_project_dir}/root/feature",
                    f"{tmp_project_dir}/root/{project_name}",
                ),
            ),
            RoutineTask(
                purpose="Setup user config file",
                command=Commands.rename(
                    f"{tmp_project_dir}/user/feature.json",
                    f"{tmp_project_dir}/user/{project_name}.json",
                ),
            ),
            # ---------------------------------------------- - - -
            # VsCode Settings
            #
            RoutineTask(
                purpose="Create vscode settings folder",
                command=Commands.folder_create(f"{tmp_project_dir}/.vscode"),
            ),
            RoutineTask(
                purpose="Setup vscode settings",
                command=create_vscode_settings,
            ),
            # ---------------------------------------------- - - -
            # Front-end Sources
            #
            RoutineTask(
                purpose="Update project name in 'package.json' file",
                command=Commands.json_patch_feature_name_property(
                    f"{tmp_project_dir}/package.json", f"vx-feature-{project_name[:-8]}"
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
                    f"{path}/vx-feature-{project_name[:-8]}"
                ),
            ),
            # Clean temporary files
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

    desktop_entry_filenames: list[str] = []
    desktop_entry_tasks: list[RoutineTask] = []

    def create_desktop_entries_register():
        try:
            write_json(
                f"{VxPath.ROOT_FEATURE_MODULES}/{feature_name}/apps.json",
                desktop_entry_filenames,
            )
            return True
        except:
            return False

    if os.path.exists(f"{dev_dir}/apps") and os.path.isdir(f"{dev_dir}/apps"):
        desktop_entry_filenames = [
            file for file in os.listdir(f"{dev_dir}/apps") if file.endswith(".desktop")
        ]

        desktop_entry_tasks = [
            RoutineTask(
                purpose=f"Create '{filename}' desktop entry",
                command=Commands.file_copy(
                    f"{dev_dir}/apps/{filename}",
                    VxPath.DESKTOP_ENTRIES,
                ),
                undo_command=Commands.file_remove(
                    f"{VxPath.DESKTOP_ENTRIES}/{filename}"
                ),
            )
            for filename in desktop_entry_filenames
        ]

        if desktop_entry_tasks:
            desktop_entry_tasks += [
                RoutineTask(
                    purpose="Create desktop entries register",
                    command=create_desktop_entries_register,
                )
            ]

    return Routine(
        purpose=f"Add feature '{feature_name[:-8]}' to Vixen Shell",
        tasks=[
            # ---------------------------------------------- - - -
            # Feature Config
            #
            RoutineTask(
                purpose="Setup root config module",
                command=Commands.folder_copy(
                    f"{dev_dir}/root/{feature_name}",
                    VxPath.ROOT_FEATURE_MODULES,
                ),
                undo_command=Commands.folder_remove(
                    f"{VxPath.ROOT_FEATURE_MODULES}/{feature_name}"
                ),
                requirements=[
                    {
                        "purpose": "Check an existing root config module",
                        "callback": Commands.Checkers.folder(
                            f"{dev_dir}/root/{feature_name}", True
                        ),
                        "failure_message": "Root config module not found",
                    }
                ],
            ),
            RoutineTask(
                purpose="Setup user config file",
                command=Commands.file_copy(
                    f"{dev_dir}/user/{feature_name}.json",
                    VxPath.USER_FEATURE_PARAMS,
                ),
                undo_command=Commands.file_remove(
                    f"{VxPath.USER_FEATURE_PARAMS}/{feature_name}.json"
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        f"{dev_dir}/user/{feature_name}.json", False
                    ),
                    "message": "User config file not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Feature Dependencies
            #
            RoutineTask(
                purpose="Init feature dependencies",
                command=Commands.folder_create(f"/usr/share/vixen/{feature_name}.libs"),
                undo_command=Commands.folder_remove(
                    f"/usr/share/vixen/{feature_name}.libs"
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        f"{dev_dir}/requirements.txt", False
                    ),
                    "message": "Requirements not found",
                },
            ),
            RoutineTask(
                purpose="Install feature dependencies",
                command=Commands.env_dependencies(
                    VxPath.ENV,
                    f"{dev_dir}/requirements.txt",
                    f"/usr/share/vixen/{feature_name}.libs",
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        f"{dev_dir}/requirements.txt", False
                    ),
                    "message": "Requirements not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Feature Front-end Sources
            #
            RoutineTask(
                purpose="Setup feature front-end sources",
                command=Commands.folder_copy(
                    f"{dev_dir}/src/{feature_name}",
                    VxPath.FRONT_FEATURES,
                ),
                undo_command=Commands.folder_remove(
                    f"{VxPath.FRONT_FEATURES}/{feature_name}"
                ),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
            RoutineTask(
                purpose="Rebuild Vixen Shell front-end",
                command=Commands.yarn_build(VxPath.FRONT),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
        ]
        + desktop_entry_tasks,
    ).run()


def vx_add_extra_feature(feature_name: str):
    tmp_feature_dir = f"/tmp/vx-feature-{feature_name[:-8]}-main"

    if not Routine(
        purpose=f"Download extra feature '{feature_name[:-8]}'",
        tasks=[
            RoutineTask(
                purpose="Download feature",
                command=Commands.git_get_archive(
                    "/tmp", f"vx-feature-{feature_name[:-8]}"
                ),
            ),
        ],
    ).run():
        return False

    add_result = vx_add_feature(tmp_feature_dir, feature_name)

    return (
        Routine(
            purpose=f"Clean temporary files",
            tasks=[
                RoutineTask(
                    purpose="Clean files",
                    command=Commands.folder_remove(tmp_feature_dir),
                ),
            ],
        ).run()
        and add_result
    )


# ---------------------------------------------- - - -
# Remove feature


def vx_remove_feature(feature_name: str):
    front_end = os.path.exists(f"{VxPath.FRONT_FEATURES}/{feature_name}")

    desktop_entry_tasks: list[RoutineTask] = []

    if os.path.exists(f"{VxPath.ROOT_FEATURE_MODULES}/{feature_name}/apps.json"):
        desktop_entry_filenames = read_json(
            f"{VxPath.ROOT_FEATURE_MODULES}/{feature_name}/apps.json"
        )

        desktop_entry_tasks = [
            RoutineTask(
                purpose=f"Remove '{filename}' desktop entry",
                command=Commands.file_remove(f"{VxPath.DESKTOP_ENTRIES}/{filename}"),
            )
            for filename in desktop_entry_filenames
        ]

    return Routine(
        purpose=f"Remove feature '{feature_name[:-8]}'",
        tasks=[
            # ---------------------------------------------- - - -
            # Feature Config
            #
            RoutineTask(
                purpose="Remove root config module",
                command=Commands.folder_remove(
                    f"{VxPath.ROOT_FEATURE_MODULES}/{feature_name}"
                ),
            ),
            RoutineTask(
                purpose="Remove user config file",
                command=Commands.file_remove(
                    f"{VxPath.USER_FEATURE_PARAMS}/{feature_name}.json"
                ),
                skip_on={
                    "callback": Commands.Checkers.file(
                        f"{VxPath.USER_FEATURE_PARAMS}/{feature_name}.json",
                        False,
                    ),
                    "message": "User config file not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Feature Dependencies
            #
            RoutineTask(
                purpose="Remove feature dependencies",
                command=Commands.folder_remove(f"/usr/share/vixen/{feature_name}.libs"),
                skip_on={
                    "callback": Commands.Checkers.folder(
                        f"/usr/share/vixen/{feature_name}.libs", False
                    ),
                    "message": "Dependencies not found",
                },
            ),
            # ---------------------------------------------- - - -
            # Feature Front-end Sources
            #
            RoutineTask(
                purpose="Remove feature front-end sources",
                command=Commands.folder_remove(
                    f"{VxPath.FRONT_FEATURES}/{feature_name}"
                ),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
            RoutineTask(
                purpose="Rebuild Vixen Shell front-end",
                command=Commands.yarn_build(VxPath.FRONT),
                skip_on={"callback": lambda: not front_end, "message": "No front-end"},
            ),
        ]
        + desktop_entry_tasks,
    ).run()
