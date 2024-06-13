import os
from .utils import use_sudo, get_dev_feature_name
from .logger import Logger
from vx_cli import Cli


class SetupManager:
    # ---------------------------------------------- - - -
    # VIXEN SHELL
    #

    @staticmethod
    @use_sudo(True)
    def run(library_path: str):
        from .setup import setup

        Logger.log("You are about to install Vixen Shell. Confirm your choice.")

        if Cli.Input.get_confirm():
            setup(library_path)

    @staticmethod
    @use_sudo(True)
    def remove():
        from .setup import remove_all
        from .requests import ShellRequests

        if ShellRequests.ping():
            Logger.log(
                "Vixen Shell is running. Close it and try this damn command again.",
                "WARNING",
            )
            return

        Logger.log("Are you sure you want to remove Vixen Shell?", "WARNING")

        if Cli.Input.get_confirm():
            remove_all()
        else:
            Logger.log("You made the right choice.")

    @staticmethod
    @use_sudo(True)
    def update():
        from .setup import update
        from .requests import ShellRequests

        if ShellRequests.ping():
            Logger.log(
                "Vixen Shell is running. Close it and try again.",
                "WARNING",
            )
            return

        Logger.log("Are you sure you want to update Vixen Shell?", "WARNING")

        if Cli.Input.get_confirm():
            update()

    # ---------------------------------------------- - - -
    # ENVIRONMENT
    #

    @staticmethod
    @use_sudo(True)
    def install_package(package_name: str):
        from .setup import install_environment_package

        Logger.log(
            f"Are you sure you want to install '{package_name}' to Vixen Shell environment?",
            "WARNING",
        )

        if Cli.Input.get_confirm():
            install_environment_package(package_name)

    @staticmethod
    @use_sudo(True)
    def uninstall_package(package_name: str):
        from .setup import uninstall_environment_package

        Logger.log(
            f"Are you sure you want to uninstall '{package_name}' to Vixen Shell environment?",
            "WARNING",
        )

        if Cli.Input.get_confirm():
            uninstall_environment_package(package_name)

    # ---------------------------------------------- - - -
    # FEATURES
    #

    @staticmethod
    @use_sudo(False)
    def create_feature(parent_dir: str):
        from .setup import vx_new_feature
        from .requests import ShellRequests

        feature_names = ShellRequests.feature_names()
        if feature_names == None:
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
            front_end = True
            Logger.log("Would you like to include a front-end base in your project?")

            if not Cli.Input.get_confirm():
                front_end = False

            Logger.log(f"Are you sure you want to create '{project_name}' project?")

            if Cli.Input.get_confirm():
                if vx_new_feature(parent_dir, project_name, front_end):
                    print()
                    Logger.log("The project was created successfully")
                    Logger.log(
                        f"Type 'vxm --dev run' in the project folder to launch and try your project"
                    )
            else:
                Logger.log("Operation avorted", "WARNING")

    @staticmethod
    @use_sudo(True)
    def add_feature(dev_dir: str):
        from .setup import vx_add_feature
        from .requests import ShellRequests

        feature_names = ShellRequests.feature_names()
        if feature_names == None:
            return

        feature_name = get_dev_feature_name(dev_dir)
        if not feature_name:
            Logger.log(
                "No features to add (root feature module not found)",
                "ERROR",
            )
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
    def add_extra_feature(feature_name: str):
        from .setup import vx_add_extra_feature
        from .requests import ShellRequests

        feature_names = ShellRequests.feature_names()
        if feature_names == None:
            return

        if feature_name in feature_names:
            Logger.log(
                f"A feature called '{feature_name}' already exists in Vixen Shell",
                "ERROR",
            )
            return

        Logger.log(
            f"You are about to add '{feature_name}' extra feature to Vixen Shell. Do you want it?",
            "WARNING",
        )

        if Cli.Input.get_confirm():
            if vx_add_extra_feature(feature_name):
                ShellRequests.load_feature(feature_name)

                print()
                Logger.log(f"'{feature_name}' extra feature added successfully")
        else:
            Logger.log("Operation avorted", "WARNING")

    @staticmethod
    @use_sudo(True)
    def remove_feature():
        from .setup import vx_remove_feature
        from .requests import ShellRequests

        feature_names = ShellRequests.feature_names()
        if feature_names == None:
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
