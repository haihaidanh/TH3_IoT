import argparse
import asyncio
import sys
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code, Message

# aiocoap can SelectorEventLoop tren Windows
if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

WELCOME = "Xin chao tu CoAP Server"


class MessageResource(resource.Resource):
    """Tai nguyen /iot/lab/message."""

    def __init__(self):
        super().__init__()
        self.last_message = None  # mo rong: luu thong diep POST gan nhat

    async def render_get(self, request):
        print("GET request received: /iot/lab/message")
        print()
        payload = WELCOME
        if self.last_message:
            payload += " | Thong diep gan nhat: " + self.last_message
        return Message(code=Code.CONTENT, payload=payload.encode("utf-8"))

    async def render_post(self, request):
        text = request.payload.decode("utf-8", errors="replace").strip()
        if not text:
            print("POST request received: payload rong -> 4.00 Bad Request")
            print()
            return Message(code=Code.BAD_REQUEST, payload=b"Payload rong")

        self.last_message = text
        now = datetime.now().strftime("%H:%M:%S")
        print("POST request received:")
        print("Payload: " + text)
        print("Time: " + now)
        print()
        return Message(code=Code.CHANGED, payload=b"Server da nhan thong diep")


async def main(host, port):
    root = resource.Site()
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader),
    )
    root.add_resource(["iot", "lab", "message"], MessageResource())

    server = await aiocoap.Context.create_server_context(root, bind=(host, port))
    print("CoAP Server started on port %d" % port)
    print("Resource: /iot/lab/message  (GET, POST)")
    print("Nhan Ctrl+C de dung server.")
    print()
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await server.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 1 - CoAP Server")
    default_host = "127.0.0.1" if sys.platform == "win32" else "::"
    parser.add_argument("--host", default=default_host, help="dia chi bind (mac dinh 127.0.0.1 tren Windows, :: tren Linux)")
    parser.add_argument("--port", type=int, default=5683, help="cong UDP (mac dinh 5683)")
    args = parser.parse_args()
    try:
        asyncio.run(main(args.host, args.port))
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nCoAP Server stopped.")
