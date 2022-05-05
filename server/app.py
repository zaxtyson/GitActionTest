from sanic import Sanic
from aiofiles import open as aio_open
from sanic.request import Request
from sanic.response import text
from sanic.log import logger
import os
from updater import IndexUpdater

app = Sanic("RepoUpdater")

upload_token = "token hello"
update_pkg_file = "update.tar.gz"


@app.get("/", version=1)
async def index(request: Request) -> text:
    return text("Hello, the repo updater service is running!")


@app.put("/upload", version=1, stream=True)
async def upload(request: Request) -> text:
    try:
        if request.headers.get("Authorization", "") != upload_token:
            logger.warning(
                f"Unauthorized upload request from {request.conn_info.client_ip}")
            return text("Unauthorized", status=401)

        logger.info(f"Recving {update_pkg_file} ...")
        async with aio_open(update_pkg_file, "wb") as f:
            while True:
                chunk = await request.stream.read()
                if not chunk:
                    break
                logger.info(f"Recved {len(chunk)} bytes")
                await f.write(chunk)

        logger.info(f"Received {update_pkg_file}")
        updater = IndexUpdater()
        updater.update_index(os.path.join(os.getcwd(), update_pkg_file))
        os.remove(update_pkg_file)
        return text("ok")
    except Exception as e:
        logger.error(e)
        return text("error: {}".format(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
