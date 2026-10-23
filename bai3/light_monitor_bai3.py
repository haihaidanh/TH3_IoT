import argparse
import asyncio
import json
import sys
from datetime import datetime

import aiocoap
from aiocoap import Code, Message

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

DEVICE_ID = "light01"


def show_state(title, response):
    now = datetime.now().strftime("%H:%M:%S")
    try:
        data = json.loads(response.payload.decode("utf-8"))
        device = data.get("device_id", "?")
        status = data.get("status", "?")
    except (ValueError, UnicodeDecodeError):
        device, status = "?", response.payload.decode("utf-8", errors="replace")
    print("[%s] %s" % (now, title))
    print("Device: %s" % device)
    print("Status: %s" % status)
    print()


async def main(args):
    uri = "coap://%s:%d/iot/lab/%s/status" % (args.host, args.port, DEVICE_ID)
    protocol = await aiocoap.Context.create_client_context()
    request = None
    try:
        print("Registering CoAP Observe...")
        print("URI: " + uri)
        # observe=0 -> dang ky theo doi tai nguyen (RFC 7641)
        request = protocol.request(Message(code=Code.GET, uri=uri, observe=0))
        try:
            first = await asyncio.wait_for(request.response, timeout=args.timeout)
        except asyncio.TimeoutError:
            print("Loi: Server khong phan hoi (timeout). Hay kiem tra Server dang chay.")
            return
        except (aiocoap.error.Error, OSError) as exc:
            print("Loi ket noi: %r" % (exc,))
            return

        if first.opt.observe is None:
            print("Server khong ho tro Observe tren tai nguyen nay.")
            return
        print("Observe registration successful")
        print()
        show_state("Initial State", first)

        # Moi thong bao tiep theo den tu request.observation (Server chu dong day ve)
        async for response in request.observation:
            show_state("State Updated", response)
        print("Server da ket thuc Observe.")
    except (aiocoap.error.Error, OSError) as exc:
        print("Loi trong luc theo doi: %r" % (exc,))
    finally:
        if request is not None and getattr(request, "observation", None) is not None:
            request.observation.cancel()
        print("Dung theo doi.")
        await protocol.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 3 - Light Monitoring Client")
    default_host = "127.0.0.1" if sys.platform == "win32" else "localhost"
    parser.add_argument("--host", default=default_host)
    parser.add_argument("--port", type=int, default=5683)
    parser.add_argument("--timeout", type=float, default=5.0)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        pass
