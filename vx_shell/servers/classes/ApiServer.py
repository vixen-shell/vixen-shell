import uvicorn, signal, asyncio
from typing import Coroutine
from threading import Thread, Event
from fastapi import FastAPI
from vx_gtk import GtkApp
from vx_config import VxConfig
from vx_logger import Logger
from ..utils import api_logging_config


class AsyncLoop:
    loop = asyncio.new_event_loop()
    is_running = False

    def run():
        if AsyncLoop.is_running:
            raise ValueError(f"{AsyncLoop.__name__} already running")

        def run_async_loop():
            asyncio.set_event_loop(AsyncLoop.loop)
            AsyncLoop.loop.run_forever()

        Thread(target=run_async_loop, daemon=True).start()
        AsyncLoop.is_running = True

    def run_task(task: Coroutine):
        asyncio.run_coroutine_threadsafe(task, AsyncLoop.loop)


class ApiServer:
    server: uvicorn.Server = None
    server_is_down = Event()
    logger_is_ready = Event()

    @staticmethod
    def handle_signals(signum, frame):
        ApiServer.stop()

    @staticmethod
    def __before_starting():
        signal.signal(signal.SIGTERM, ApiServer.handle_signals)
        signal.signal(signal.SIGHUP, ApiServer.handle_signals)
        signal.signal(signal.SIGINT, ApiServer.handle_signals)

    @staticmethod
    async def __start_uvicorn(api: FastAPI):
        ApiServer.server = uvicorn.Server(
            uvicorn.Config(
                api,
                host="localhost",
                port=VxConfig.API_PORT,
                log_config=api_logging_config,
                loop="asyncio",
            )
        )

        Logger.init()
        ApiServer.logger_is_ready.set()

        await ApiServer.server.serve()
        ApiServer.server_is_down.set()

    @staticmethod
    def start(api: FastAPI):
        if ApiServer.server:
            raise ValueError(f"{ApiServer.__name__} already running")

        ApiServer.__before_starting()

        AsyncLoop.run()
        AsyncLoop.run_task(ApiServer.__start_uvicorn(api))

        ApiServer.logger_is_ready.wait()
        GtkApp.run()

    @staticmethod
    def stop():
        if not ApiServer.server:
            raise ValueError(f"{ApiServer.__name__} is not running")

        ApiServer.server.should_exit = True
        ApiServer.server_is_down.wait()
        GtkApp.quit()
