import os
from .utils import use_sudo, get_dev_feature_name
from .logger import Logger
from ..cli import Cli


class SetupManager:
    @staticmethod
    @use_sudo(True)
    def run(library_path: str):
        from .setup import vx_setup

        Logger.log("You are about to install Vixen Shell. Confirm your choice.")

        if Cli.Input.get_confirm():
            vx_setup(library_path)

    @staticmethod
    @use_sudo(True)
    def remove():
        from .setup import vx_remove
        from .requests import ShellRequests

        if ShellRequests.ping():
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
    @use_sudo(False)
    def create_feature(parent_dir: str):
        from .setup import vx_new_feature
        from .requests import ShellRequests

        feature_names = ShellRequests.feature_names()
        if not feature_names:
            return

        Logger.log("You are about to create a new development project", "WARNING")

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
    @use_sudo(True)
    def add_feature(dev_dir: str):
        from .setup import vx_add_feature
        from .requests import ShellRequests

        feature_names = ShellRequests.feature_names()
        if not feature_names:
            return

        feature_name = get_dev_feature_name(dev_dir)
        if not feature_name:
            return

        if feature_name in feature_names:
            Logger.log(
                f"A feature called '{feature_name}' already exists in Vixen Shell",
                "ERROR",
            )
            return

        Logger.log(
            f"You are about to add '{feature_name}' feature to Vixen Shell. Do you want it?",
            "WARNING",
        )

        if Cli.Input.get_confirm():
            if vx_add_feature(dev_dir, feature_name):
                ShellRequests.load_feature(feature_name)

                print()
                Logger.log(f"'{feature_name}' feature added successfully")
        else:
            Logger.log("Operation avorted", "WARNING")

    @staticmethod
    @use_sudo(True)
    def remove_feature():
        from .setup import vx_remove_feature
        from .requests import ShellRequests

        feature_names = ShellRequests.feature_names()
        if not feature_names:
            return

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
                ShellRequests.unload_feature(feature_name)

                if vx_remove_feature(feature_name):
                    print()
                    Logger.log(f"'{feature_name}' feature removed successfully")
            else:
                Logger.log("Operation avorted", "WARNING")
