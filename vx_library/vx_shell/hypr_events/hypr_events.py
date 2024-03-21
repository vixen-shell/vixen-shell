import os
from typing import List

HYPR_SOCKET_PATH = "/tmp/hypr/{}/.socket2.sock".format(
    os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
)

data_map = {
    "workspace": ["workspace_name"],
    "focusedmon": ["monitor_name", "workspace_name"],
    "activewindow": ["window_class", "window_title"],
    "activewindowv2": ["window_address"],
    "fullscreen": ["enter_fullscreen"],
    "monitorremoved": ["monitor_name"],
    "monitoradded": ["monitor_name"],
    "createworkspace": ["workspace_name"],
    "destroyworkspace": ["workspace_name"],
    "moveworkspace": ["workspace_name", "monitor_name"],
    "activelayout": ["keyboard_name", "layout_name"],
    "openwindow": ["window_address", "workspace_name", "window_class", "window_title"],
    "closewindow": ["window_address"],
    "movewindow": ["window_address", "workspace_name"],
    "openlayer": ["namespace"],
    "closelayer": ["namespace"],
    "submap": ["submap_name"],
    "changefloatingmode": ["window_address", "floating"],
    "urgent": ["window_address"],
    "minimize": ["window_address", "minimized"],
    "screencast": ["state", "owner"],
    "windowtitle": ["window_address"],
}


class HyprSocketDataHandler:
    def __init__(self, data_bytes: bytes) -> None:
        id, data = self._extract_data(data_bytes)
        self._id = id
        self._data = self._name_data(data)

    def _extract_data(self, data_bytes: bytes) -> tuple[str, List[str]]:
        data_line = data_bytes.decode("utf-8")
        data_line = data_line.rstrip("\n")
        split_line = data_line.split(">>")

        return (split_line[0], split_line[1].split(",") if len(split_line) > 1 else [])

    def _name_data(self, data: List[str]) -> dict | List[str]:
        def name_data():
            named_data = {}
            for key in data_map:
                if key == self._id:
                    for index, value in enumerate(data_map[key]):
                        named_data[value] = data[index]
                    return named_data
            return data

        try:
            return name_data()
        except Exception:
            return data

    @property
    def to_json(self):
        return {"id": self._id, "data": self._data}
