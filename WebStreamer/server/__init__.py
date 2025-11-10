# Taken from megadlbot_oss <https://github.com/eyaadh/megadlbot_oss/blob/master/mega/webserver/__init__.py>
# Thanks to Eyaadh <https://github.com/eyaadh>
# This file is a part of TG-
# Coding : Jyothis Jayanth [@EverythingSuckz]

from aiohttp import web
from .stream_routes import routes as stream_routes
from .auth_routes import routes as auth_routes


def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(stream_routes)
    web_app.add_routes(auth_routes)
    return web_app
