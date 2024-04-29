import os
from .utils import sudo_is_used, read_json
from .logger import Logger
from ..cli import Cli


class SetupManager:
    @staticmethod
    def run(library_path: str):
        from .setup import vx_setup

        if not sudo_is_used():
            Logger.log("This command must be used with 'sudo'", "WARNING")
            return

        Logger.log("You are about to install Vixen Shell. Confirm your choice.")

        if Cli.Input.get_confirm():
            vx_setup(library_path)

    @staticmethod
    def remove():
        from .setup import vx_remove
        from ..shell import Shell

        if not sudo_is_used():
            Logger.log("This damn command must be used with 'sudo'", "WARNING")
            return

        if Shell.is_open():
            Logger.log(
                "Vixen Shell is running. Close it and try this damn command again.",
                "WARNING",
            )
            return

        Logger.log("Are you sure you want to remove Vixen Shell?", "WARNING")

        if Cli.Input.get_confirm():
            vx_remove()
        else:
            Logger.log("You made the right choice.")

    @staticmethod
    def create_feature(parent_dir: str):
        from .setup import vx_new_feature
        from ..shell import Shell

        if sudo_is_used():
            Logger.log("Cannot use this command with 'sudo'", "WARNING")
            return

        if not Shell.is_open():
            Logger.log("Vixen Shell is not running", "WARNING")
            return

        Logger.log("You are about to create a new development project", "WARNING")

        feature_names = Shell.feature_names()

        folder_list = [
            folder_name
            for folder_name in os.listdir(parent_dir)
            if os.path.isdir(os.path.join(parent_dir, folder_name))
        ]

        Logger.log("Please enter the name of the new feature")

        project_name = Cli.Input.get_answer(
            [
                Cli.Input.Filter(
                    type="exclude",
                    values=feature_names,
                    reason="A feature with this name already exists in Vixen Shell",
                ),
                Cli.Input.Filter(
                    type="exclude",
                    values=folder_list,
                    reason="A folder with this name already exists in the current folder",
                ),
            ]
        )

        if project_name:
            Logger.log(f"Are you sure you want to create '{project_name}' project?")

            if Cli.Input.get_confirm():
                if vx_new_feature(parent_dir, project_name):
                    print()
                    Logger.log("The project was created successfully")
                    Logger.log(
                        "Type 'yarn dev' in the project folder to launch the dev server"
                    )
            else:
                Logger.log("Operation avorted", "WARNING")

    @staticmethod
    def add_feature(dev_dir: str):
        from .setup import vx_add_feature
        from ..shell import Shell

        if not sudo_is_used():
            Logger.log("This command must be used with 'sudo'", "WARNING")
            return

        if not Shell.is_open():
            Logger.log("Vixen Shell is not running", "WARNING")
            return

        package = read_json(f"{dev_dir}/package.json")
        if not package:
            Logger.log(
                f"Unable to found 'package.json' file in '{dev_dir}' directory", "ERROR"
            )
            return

        feature_name: str = package.get("name")
        if not feature_name:
            Logger.log(
                "Unable to found 'name' property in 'package.json' file", "ERROR"
            )
            return

        feature_name = feature_name.replace("vx-feature-", "")
        feature_names = Shell.feature_names()

        if feature_name in feature_names:
            Logger.log(
                f"A feature called '{feature_name}' already exists in Vixen Shell",
                "ERROR",
            )
            return

        Logger.log(
            f"You to add '{feature_name}' feature to Vixen Shell. Do you want it?",
            "WARNING",
        )

        if Cli.Input.get_confirm():
            if vx_add_feature(dev_dir, feature_name):
                # Restart Front Server !!!
                # Reload Features !!!

                print()
                Logger.log(f"'{feature_name}' feature added successfully")
        else:
            Logger.log("Operation avorted", "WARNING")

    @staticmethod
    def remove_feature():
        from .setup import vx_remove_feature
        from ..shell import Shell

        if not sudo_is_used():
            Logger.log("This command must be used with 'sudo'", "WARNING")
            return

        if not Shell.is_open():
            Logger.log("Vixen Shell is not running", "WARNING")
            return

        feature_names = Shell.feature_names()

        Logger.log("Please type the name of the feature you want to remove")

        feature_name = Cli.Input.get_answer(
            [
                Cli.Input.Filter(
                    type="include",
                    values=feature_names,
                    reason="You must type the name of an existing feature in Vixen Shell",
                )
            ]
        )

        if feature_name:
            Logger.log(
                f"Are you sure you want to remove '{feature_name}' feature?", "WARNING"
            )

            if Cli.Input.get_confirm():
                # Close feature if is open

                if vx_remove_feature(feature_name):
                    # Restart Front Server !!!
                    # Reload Features !!!

                    print()
                    Logger.log(f"'{feature_name}' feature removed successfully")
            else:
                Logger.log("Operation avorted", "WARNING")
