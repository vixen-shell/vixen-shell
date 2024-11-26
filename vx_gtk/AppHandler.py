import psutil
from difflib import SequenceMatcher
from .Gtk_imports import Gio


def get_process_infos_by_pid(pid: int) -> list[str]:
    process = psutil.Process(pid)

    command_list = process.cmdline()
    command_list[0] = command_list[0].split("/")[-1]
    command_line = " ".join(command_list)

    return [process.exe(), process.name(), command_line]


class AppSummary:
    def __init__(self, app_info: Gio.DesktopAppInfo) -> None:
        self.id = app_info.get_id()

        self.name = app_info.get_name()
        self.display_name = app_info.get_display_name() or None
        self.generic_name = app_info.get_generic_name() or None
        self.initial_class = app_info.get_startup_wm_class() or None

        self.commandline = app_info.get_commandline() or None
        self.executable = app_info.get_executable() or None

        icon = app_info.get_icon() or None
        self.icon = icon.to_string() if icon else None

        self.description = app_info.get_description() or None
        self.keywords = app_info.get_keywords() or []
        self.categories = app_info.get_categories() or None
        self.supported_types = app_info.get_supported_types() or []
        self.supports_uris = app_info.supports_uris() or False
        self.supports_files = app_info.supports_files() or False
        self.should_show = app_info.should_show() or False
        self.actions = app_info.list_actions() or None


class AppHandler:
    @staticmethod
    def get_ids() -> list[str]:
        return [app_info.get_id() for app_info in Gio.AppInfo.get_all()]

    @staticmethod
    def get(app_id: str) -> Gio.DesktopAppInfo:
        return Gio.DesktopAppInfo.new(app_id)

    @staticmethod
    def find_id(matching_elements: list[str] = [], pid: int = None) -> str:
        def compute_similarity(string1: str, string2: str) -> float:
            if not string1 or not string2:
                return 0.0

            return SequenceMatcher(None, string1, string2).ratio()

        if pid:
            matching_elements.extend(get_process_infos_by_pid(pid))

        app_id: str = None
        closest_ratio = 0.0

        for app_info in Gio.AppInfo.get_all():
            app = AppSummary(app_info)
            similarities = []

            for elem in matching_elements:
                similarities.append(compute_similarity(elem, app.id))
                similarities.append(compute_similarity(elem, app.name))
                similarities.append(compute_similarity(elem, app.display_name))
                similarities.append(compute_similarity(elem, app.generic_name))
                similarities.append(compute_similarity(elem, app.initial_class))
                similarities.append(compute_similarity(elem, app.commandline))
                similarities.append(compute_similarity(elem, app.executable))
                similarities.append(compute_similarity(elem, app.description))

            valid_similarities = [sim for sim in similarities if sim > 0]
            if valid_similarities:
                overall_similarity = sum(valid_similarities) / len(valid_similarities)
            else:
                overall_similarity = 0.0

            if overall_similarity > closest_ratio:
                app_id = app_info.get_id()
                closest_ratio = overall_similarity

        return app_id

    @staticmethod
    def launch(app_id: str) -> bool:
        app: Gio.DesktopAppInfo = Gio.DesktopAppInfo.new(app_id)
        return app.launch()

    @staticmethod
    def launch_action(app_id: str, action_name: str) -> bool:
        app: Gio.DesktopAppInfo = Gio.DesktopAppInfo.new(app_id)
        return app.launch_action(action_name)
