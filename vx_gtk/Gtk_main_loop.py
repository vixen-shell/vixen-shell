import asyncio
from typing import Optional
from vx_logger import Logger
from .Gtk_imports import Gtk, GLib


class GtkMainLoop:
    _task: Optional[asyncio.Task] = None

    @staticmethod
    def start():
        if GtkMainLoop._task is None or GtkMainLoop._task.done():
            GtkMainLoop._task = asyncio.create_task(asyncio.to_thread(Gtk.main))
            Logger.log("Gtk main loop is started")

    @staticmethod
    async def stop():
        if GtkMainLoop._task is not None and not GtkMainLoop._task.done():
            GLib.idle_add(Gtk.main_quit)
            await GtkMainLoop._task
            Logger.log("Gtk main loop is stopped")

            GtkMainLoop._task = None
