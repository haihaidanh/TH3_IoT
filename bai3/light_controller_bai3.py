import argparse
import asyncio
import json
import sys

import aiocoap
from aiocoap import Code, Message

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

CF_JSON = 50
DEVICE_ID = "light01"


async def request(protocol, code, uri, payload=None, timeout=5.0):
    msg = Message(code=code, uri=uri)
    if payload is not None:
        msg.payload = payload
        msg.opt.content_format = CF_JSON
    try:
        return await asyncio.wait_for(protocol.request(msg).response, timeout=timeout)
    except asyncio.TimeoutError:
        print("Loi: het thoi gian cho (timeout) - Server khong phan hoi.")
    except (aiocoap.error.Error, OSError) as exc:
        print("Loi ket noi: %r" % (exc,))
    return None


async def main(args):
    uri = "coap://%s:%d/iot/lab/%s/status" % (args.host, args.port, DEVICE_ID)
    protocol = await aiocoap.Context.create_client_context()
    try:
        while True:
            try:
                cmd = await asyncio.to_thread(input, "Nhap lenh (ON/OFF/STATUS/EXIT): ")
            except EOFError:
                break
            cmd = cmd.strip().upper()

            if cmd == "EXIT":
                print("Thoat chuong trinh.")
                break

            elif cmd in ("ON", "OFF", "BAD"):
                command = "BLINK" if cmd == "BAD" else cmd
                body = json.dumps({"device_id": DEVICE_ID, "command": command}).encode("utf-8")
                print("Sending PUT request...")
                resp = await request(protocol, Code.PUT, uri, body, args.timeout)
                if resp is not None:
                    print("Response Code: %s" % resp.code)
                    print(resp.payload.decode("utf-8", errors="replace"))

            elif cmd == "STATUS":
                print("Sending GET request...")
                resp = await request(protocol, Code.GET, uri, timeout=args.timeout)
                if resp is not None:
                    print("Response:")
                    print(resp.payload.decode("utf-8", errors="replace"))

            elif cmd == "":
                continue
            else:
                print("Lenh khong hop le. Chi chap nhan: ON, OFF, STATUS, EXIT")
            print()
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 3 - Light Controller Client")
    default_host = "127.0.0.1" if sys.platform == "win32" else "localhost"
    parser.add_argument("--host", default=default_host)
    parser.add_argument("--port", type=int, default=5683)
    parser.add_argument("--timeout", type=float, default=5.0)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        pass
