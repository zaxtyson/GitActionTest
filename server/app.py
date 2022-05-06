from sanic import Sanic
from sanic.request import Request
from sanic.response import text
from sanic.log import logger
import os
from updater import IndexUpdater

app = Sanic("RepoUpdater")

upload_token = "token hello"


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

        logger.info(request.headers)
        update_file_name = "update.tar.gz"
        update_file_size = request.headers.get("Content-Length", 0)

        logger.info(
            f"Receiving {update_file_name}, Content-Length: {update_file_size}")
        with open(update_file_name, 'wb') as f:
            while True:
                chunk = await request.stream.read()
                if not chunk:
                    break
                f.write(chunk)

        logger.info(
            f"Received {update_file_name}, size: {os.path.getsize(update_file_name)} bytes")
        updater = IndexUpdater()
        updater.update_index(os.path.join(os.getcwd(), update_file_name))
        os.remove(update_file_name)
        return text("ok")
    except Exception as e:
        logger.error(e)
        return text("error: {}".format(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
