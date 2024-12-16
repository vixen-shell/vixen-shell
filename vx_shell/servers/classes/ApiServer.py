import uvicorn, signal, asyncio
from threading import Thread, Event
from fastapi import FastAPI
from vx_gtk import GtkApp
from vx_config import VxConfig
from vx_logger import Logger
from ..utils import api_logging_config


def run_asyncio_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


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

        asyncio_loop = asyncio.new_event_loop()
        Thread(target=run_asyncio_loop, args=(asyncio_loop,), daemon=True).start()
        asyncio.run_coroutine_threadsafe(ApiServer.__start_uvicorn(api), asyncio_loop)

        ApiServer.logger_is_ready.wait()
        GtkApp.run()

    @staticmethod
    def stop():
        if not ApiServer.server:
            raise ValueError(f"{ApiServer.__name__} is not running")

        ApiServer.server.should_exit = True
        ApiServer.server_is_down.wait()
        GtkApp.quit()
