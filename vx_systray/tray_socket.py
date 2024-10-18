import os, socket, sys, signal
from vx_gtk import Gtk
from .sys_tray import Tray, init_tray


class TraySocket:
    socket_path = "/tmp/vx_systray_socket"
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket = None

    @staticmethod
    def start_server():
        TraySocket.__process()

    @staticmethod
    def __init_server():
        if os.path.exists(TraySocket.socket_path):
            os.remove(TraySocket.socket_path)

        TraySocket.server_socket.bind(TraySocket.socket_path)

    @staticmethod
    def __wait_connection():
        TraySocket.server_socket.listen(1)

    @staticmethod
    def __accept_connection():
        TraySocket.socket, _ = TraySocket.server_socket.accept()

    @staticmethod
    def __close_server():
        if TraySocket.socket:
            TraySocket.socket.close()

        TraySocket.server_socket.close()

    @staticmethod
    def __process():
        def handle_sigint(signum, frame):
            TraySocket.__close_server()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_sigint)

        TraySocket.__init_server()
        TraySocket.__wait_connection()
        TraySocket.__accept_connection()

        init_tray([Tray(TraySocket.socket)])
        Gtk.main()

        TraySocket.__close_server()
