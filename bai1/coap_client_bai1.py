# -*- coding: utf-8 -*-
"""
Bai 1 - CoAP Client co ban.

Thuc hien: GET /iot/lab/message  ->  POST thong diep sinh vien.

Chay: python coap_client_bai1.py [--host localhost] [--port 5683]
                                 [--count 1] [--test-404] [--timeout 5]
"""
import argparse
import asyncio
import sys

import aiocoap
from aiocoap import Code, Message

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

STUDENT_ID = "B23DCCN274"
STUDENT_NAME = "Nguyen Danh Hai"
POST_TEXT = "Xin chao tu CoAP Client - %s - %s" % (STUDENT_ID, STUDENT_NAME)


async def send(protocol, code, uri, payload=None, timeout=5.0):
    """Gui 1 request, tra ve response hoac None neu loi/timeout."""
    msg = Message(code=code, uri=uri, payload=payload or b"")
    try:
        return await asyncio.wait_for(protocol.request(msg).response, timeout=timeout)
    except asyncio.TimeoutError:
        print("Loi: het thoi gian cho (timeout) - Server khong phan hoi.")
    except (aiocoap.error.Error, OSError) as exc:
        print("Loi ket noi: %r" % (exc,))
    return None


def show(response):
    print("Response:")
    print("Code: %s" % response.code)
    print("Payload: %s" % response.payload.decode("utf-8", errors="replace"))
    print()


async def main(args):
    uri = "coap://%s:%d/iot/lab/message" % (args.host, args.port)
    protocol = await aiocoap.Context.create_client_context()
    try:
        # --- GET ---
        print("Sending GET request...")
        print("URI: " + uri)
        print()
        response = await send(protocol, Code.GET, uri, timeout=args.timeout)
        if response is None:
            return
        show(response)

        # --- POST (co the gui nhieu lan) ---
        for i in range(args.count):
            print("Sending POST request... (%d/%d)" % (i + 1, args.count))
            print("Payload: " + POST_TEXT)
            print()
            response = await send(
                protocol, Code.POST, uri, POST_TEXT.encode("utf-8"), args.timeout
            )
            if response is None:
                return
            show(response)

        # --- Mo rong: GET lai de thay thong diep POST gan nhat ---
        if args.count > 1:
            print("Sending GET request (kiem tra thong diep gan nhat)...")
            print()
            response = await send(protocol, Code.GET, uri, timeout=args.timeout)
            if response is not None:
                show(response)

        # --- Mo rong: truy cap tai nguyen khong ton tai ---
        if args.test_404:
            bad_uri = "coap://%s:%d/iot/lab/khong_ton_tai" % (args.host, args.port)
            print("Sending GET request toi tai nguyen khong ton tai...")
            print("URI: " + bad_uri)
            print()
            response = await send(protocol, Code.GET, bad_uri, timeout=args.timeout)
            if response is not None:
                show(response)
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 1 - CoAP Client")
    parser.add_argument("--host", default="localhost", help="dia chi Server")
    parser.add_argument("--port", type=int, default=5683, help="cong Server")
    parser.add_argument("--count", type=int, default=1, help="so lan gui POST lien tiep")
    parser.add_argument("--test-404", action="store_true", help="thu truy cap URI khong ton tai")
    parser.add_argument("--timeout", type=float, default=5.0, help="timeout (giay)")
    asyncio.run(main(parser.parse_args()))
