import os
from .utils import sudo_is_used
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

        name_list = Shell.feature_names()

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
                    values=name_list,
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
