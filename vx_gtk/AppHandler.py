import psutil
from difflib import SequenceMatcher
from .Gtk_imports import Gio, GLib


def get_process_infos_by_pid(pid: int) -> list[str]:
    process = psutil.Process(pid)

    command_list = process.cmdline()
    command_list[0] = command_list[0].split("/")[-1]
    command_line = " ".join(command_list)

    return [process.exe(), process.name(), command_line]


class Application:
    def __init__(self, app_info: Gio.DesktopAppInfo) -> None:
        self.id = app_info.get_id()

        self.name = app_info.get_name() or None
        self.display_name = app_info.get_display_name() or None
        self.generic_name = app_info.get_generic_name() or None
        self.startup_wm_class = app_info.get_startup_wm_class() or None

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

        self.__launch = lambda: app_info.launch()
        self.__launch_action = lambda action_name: app_info.launch_action(action_name)

    def launch(self) -> bool:
        return self.__launch()

    def launch_action(self, action_name: str) -> bool:
        return self.__launch_action(action_name)


class AppDict(dict[str, Application]):
    def __init__(self):
        super().__init__(self._load_applications())

        self._monitors = [
            self._create_monitor(Gio.File.new_for_path("/usr/share/applications/")),
            self._create_monitor(
                Gio.File.new_for_path(GLib.get_user_data_dir() + "/applications/")
            ),
        ]

    def _create_monitor(self, path: Gio.File) -> Gio.FileMonitor:
        monitor = path.monitor_directory(Gio.FileMonitorFlags.NONE, None)
        monitor.connect("changed", self._on_entry_changed)
        return monitor

    def _load_applications(self) -> dict[str, Application]:
        return {
            app_info.get_id(): Application(app_info)
            for app_info in Gio.AppInfo.get_all()
        }

    def _update_applications(self):
        self.clear()
        self.update(self._load_applications())

    def _on_entry_changed(
        self,
        monitor: Gio.FileMonitor,
        file: Gio.File,
        other_file: Gio.File,
        event_type: Gio.FileMonitorEvent,
    ):
        if event_type in {
            Gio.FileMonitorEvent.CREATED,
            Gio.FileMonitorEvent.DELETED,
            Gio.FileMonitorEvent.CHANGED,
        }:
            self._update_applications()

    def find(self, matching_elements: list[str] = [], pid: int = None) -> Application:
        def compute_similarity(string1: str, string2: str) -> float:
            if not string1 or not string2:
                return 0.0

            return SequenceMatcher(None, string1, string2).ratio()

        if pid:
            matching_elements.extend(get_process_infos_by_pid(pid))

        closest_app: Application = None
        closest_ratio = 0.0

        for app in self.values():
            similarities = []

            for elem in matching_elements:
                similarities.append(compute_similarity(elem, app.id))
                similarities.append(compute_similarity(elem, app.name))
                similarities.append(compute_similarity(elem, app.display_name))
                similarities.append(compute_similarity(elem, app.generic_name))
                similarities.append(compute_similarity(elem, app.startup_wm_class))
                similarities.append(compute_similarity(elem, app.commandline))
                similarities.append(compute_similarity(elem, app.executable))
                similarities.append(compute_similarity(elem, app.description))

            valid_similarities = [sim for sim in similarities if sim > 0]
            if valid_similarities:
                overall_similarity = sum(valid_similarities) / len(valid_similarities)
            else:
                overall_similarity = 0.0

            if overall_similarity > closest_ratio:
                closest_app = app
                closest_ratio = overall_similarity

        return closest_app


class Applications:
    __app_dict = AppDict()

    @staticmethod
    def items():
        return Applications.__app_dict.items()

    @staticmethod
    def keys():
        return Applications.__app_dict.keys()

    @staticmethod
    def values():
        return Applications.__app_dict.values()

    @staticmethod
    def get(id: str):
        return Applications.__app_dict.get(id)

    @staticmethod
    def find(matching_elements: list[str] = [], pid: int = None) -> Application:
        return Applications.__app_dict.find(matching_elements, pid)
