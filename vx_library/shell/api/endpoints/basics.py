from ..api import api
from ...servers import ApiServer, FrontServer


@api.get("/ping", description="Test API availability")
async def ping():
    return "Vixen Shell API (1.0.0)"


@api.get("/shutdown", description="Close API")
async def close():
    ApiServer.server.should_exit = True
    return
