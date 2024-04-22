import os
from .utils import sudo_is_used, get_vite_process
from .setup import vx_remove, vx_new_feature
from .log import Logger
from ..shell import Shell


class vxm:
    @staticmethod
    def remove():
        if not sudo_is_used():
            Logger.log("WARNING", "This damn command must be used with 'sudo'")
            return

        if Shell.is_open():
            Logger.log(
                "WARNING",
                "Vixen Shell is running. Close it and try the damn command again.",
            )
            return

        response = Logger.validate(
            "WARNING", "Are you sure you want to remove Vixen Shell?"
        )

        if response == "yes":
            vx_remove()

        if response == "no":
            Logger.log("INFO", "You made the right choice.")

    @staticmethod
    def shell_open():
        try:
            Shell.open()
        except Exception as exception:
            Logger.log("WARNING", exception)

    @staticmethod
    def shell_close():
        try:
            Shell.close()
            Logger.log("INFO", "Exit Vixen Shell successfull")
        except Exception as exception:
            Logger.log("WARNING", exception)

    @staticmethod
    def dev_run(dev_dir: str):
        try:
            vite_process = get_vite_process(dev_dir)
            dev_feature = Shell.init_dev_feature(dev_dir)
        except Exception as exception:
            Logger.log("ERROR", exception)
            return

        vite_process.start()

        try:
            dev_feature.start()
            print(f"  \033[92m➜\033[0m  Vixen: start feature '{dev_feature.name}'")
        except Exception as exception:
            f"  \033[91m➜\033[0m  Vixen: {exception}"

        vite_process.join()

        try:
            Shell.stop_dev_feature()
        except Exception as exception:
            Logger.log("WARNING", exception)

    @staticmethod
    def create_feature(parent_dir: str):
        if sudo_is_used():
            Logger.log("WARNING", "Cannot use this command with 'sudo'")
            return

        if Shell.is_open():
            Logger.log(
                "WARNING",
                "You are about to create a new development project",
            )

            name_list = Shell.feature_names()

            folder_list = [
                folder_name
                for folder_name in os.listdir(parent_dir)
                if os.path.isdir(os.path.join(parent_dir, folder_name))
            ]

            feature_name = Logger.question(
                level="INFO",
                question="Please enter the name of the new feature",
                exclude_answers=[
                    {
                        "answers": name_list,
                        "reason": "A feature with this name already exists in Vixen Shell",
                    },
                    {
                        "answers": folder_list,
                        "reason": "A folder with this name already exists in the current folder",
                    },
                ],
            )

            if feature_name:
                response = Logger.validate(
                    "WARNING",
                    f"Are you sure you want to create '{feature_name}' project?",
                )

                if response == "yes":
                    if vx_new_feature(parent_dir, feature_name):
                        print(
                            "\nThe project was created successfully.\nType 'yarn dev' in the project folder to launch the dev server."
                        )

                if response == "no":
                    Logger.log("WARNING", "Operation avorted")
        else:
            Logger.log("WARNING", "Vixen Shell is not running")
