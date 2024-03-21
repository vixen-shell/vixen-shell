import asyncio
from ..log import Logger


class UnixSocket:
    def __init__(self, socket_path: str) -> None:
        self._socket_path: str = socket_path
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._is_connected: bool = False

    async def open_connection(self) -> bool:
        try:
            if not self._is_connected:
                self._reader, self._writer = await asyncio.open_unix_connection(
                    self._socket_path
                )
                self._is_connected = True
            return True
        except Exception as e:
            Logger.log("ERROR", f"Unable to access unix socket '{self._socket_path}'")
            return False

    async def close_connection(self) -> None:
        if self._is_connected:
            if self._writer:
                self._writer.close()
                await self._writer.wait_closed()
                self._writer = None

            if self._reader:
                self._reader.feed_eof()
                self._reader = None

            self._is_connected = False

    @property
    def reader(self):
        return self._reader

    @property
    def writer(self):
        return self._writer
