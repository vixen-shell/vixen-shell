import os, requests, time, subprocess, multiprocessing
from .setup import vx_remove, vx_new_feature
from .log import Logger
from ..vx_shell import run_api

Logger.init()


def sudo_is_used() -> bool:
    return os.geteuid() == 0


def api_is_running() -> bool:
    try:
        response = requests.get("http://localhost:6481/ping")

        if response.status_code == 200:
            return True
        else:
            return False

    except requests.RequestException:
        return False


def close_api() -> bool:
    try:
        response = requests.get("http://localhost:6481/shutdown")

        if response.status_code == 200:
            return True
        else:
            return False

    except requests.RequestException:
        return False


def init_dev_mode(dev_dir: str) -> str | None:
    try:
        response = requests.post("http://localhost:6481/feature/dev/init", json=dev_dir)

        if response.status_code == 200:
            feature_name = response.json()["name"]
            return feature_name
        else:
            Logger.log("ERROR", response.json()["message"])
            return

    except requests.RequestException as error:
        Logger.log("ERROR", error.strerror)
        return


def start_feature(feature_name: str) -> bool:
    try:
        response = requests.get(f"http://localhost:6481/feature/{feature_name}/start")

        if response.status_code == 200:
            print(
                f"  \033[92m➜\033[0m  Vixen: start feature '{response.json()['name']}'"
            )
            return True
        else:
            print(f"  \033[91m➜\033[0m  Vixen: {response.json()['message']}")
            return False

    except requests.RequestException as error:
        print(f"  \033[91m➜\033[0m  Vixen: {error.strerror}")
        return False


def stop_dev_mode() -> bool:
    try:
        response = requests.get("http://localhost:6481/feature/dev/stop")

        if response.status_code == 200:
            return True
        else:
            Logger.log("ERROR", response.json()["message"])
            return False

    except requests.RequestException as error:
        Logger.log("ERROR", error.strerror)
        return False


def get_feature_names() -> list | None:
    try:
        response = requests.get("http://localhost:6481/features/names")

        if response.status_code == 200:
            data = response.json()
            return data["names"]
        else:
            Logger.log("ERROR", "Unable to get names of existing features")
            return

    except requests.RequestException as error:
        Logger.log("ERROR", error.strerror)
        return False


class vxm:
    @staticmethod
    def remove():
        if not sudo_is_used():
            Logger.log("WARNING", "This command must be used with 'sudo'")
            return

        response = Logger.validate(
            "WARNING", "Are you sure you want to remove Vixen Shell?"
        )

        if response == "yes":
            if api_is_running():
                vxm.shell_close()
            vx_remove()

        if response == "no":
            Logger.log("INFO", "You made the right choice.")

    @staticmethod
    def shell_open():
        if not api_is_running():
            run_api()
        else:
            Logger.log("WARNING", "Vixen Shell Api is already running")

    @staticmethod
    def shell_close():
        if api_is_running():
            if close_api():
                Logger.log("INFO", "Exit Vixen Shell successfull")
            else:
                Logger.log("ERROR", "Unable to exit Vixen Shell")
        else:
            Logger.log("WARNING", "Vixen Shell Api is not running")

    @staticmethod
    def dev_mode(dev_dir: str):
        def vite_process():
            process = subprocess.Popen("./node_modules/.bin/vite", shell=True)
            process.wait()

        vite = multiprocessing.Process(target=vite_process)

        if not os.path.exists(f"{dev_dir}/node_modules"):
            Logger.log(
                "WARNING",
                "The development project dependencies are not installed",
            )
            Logger.log("ERROR", "Node modules not found")
            return

        if not api_is_running():
            Logger.log("WARNING", "Vixen Shell Api is not running")
            return

        feature_name = init_dev_mode(dev_dir)

        if feature_name:
            vite.start()
            time.sleep(0.5)

            start_feature(feature_name)

            try:
                vite.join()
            except KeyboardInterrupt:
                vite.terminate()

            stop_dev_mode()

    @staticmethod
    def create_feature(parent_dir: str):
        if sudo_is_used():
            Logger.log("WARNING", "Cannot use this command with 'sudo'")
            return

        if api_is_running():
            Logger.log(
                "WARNING",
                "You are about to create a new development project",
            )

            name_list = get_feature_names()
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
            Logger.log("WARNING", "Vixen Shell Api is not running")
