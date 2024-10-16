from .SysTrayObserver import SysTrayObserver, SysTrayState


def run_systray_server():
    from .tray_socket import TraySocket

    TraySocket.start_server()
