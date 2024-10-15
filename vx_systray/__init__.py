from .SysTrayObserver import SysTrayObserver


def run_systray_server():
    from .tray_socket import TraySocket

    TraySocket.start_server()
