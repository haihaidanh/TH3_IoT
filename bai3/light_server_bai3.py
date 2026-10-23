# -*- coding: utf-8 -*-
"""
Bai 3 - Smart Light CoAP Server (GET / PUT / Observe).

Tai nguyen : coap://localhost:5683/iot/lab/light01/status
Trang thai ban dau: OFF
  GET     -> {"device_id": "light01", "status": "ON|OFF"}
  PUT     -> {"device_id": "light01", "command": "ON|OFF"}
  Observe -> tu dong thong bao cho cac Client dang theo doi khi trang thai doi

Chay: python light_server_bai3.py [--host ::] [--port 5683] [--log light_log.txt]
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code, Message

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

CF_JSON = 50  # application/json
DEVICE_ID = "light01"


class LightStatusResource(resource.ObservableResource):
    """Tai nguyen co the Observe: /iot/lab/light01/status."""

    def __init__(self, log_path=None):
        super().__init__()
        self.status = "OFF"
        self.observer_count = 0
        self.log_path = log_path

    # ---- tien ich ----
    def _status_payload(self):
        return json.dumps({"device_id": DEVICE_ID, "status": self.status}).encode("utf-8")

    def _write_log(self, text):
        if not self.log_path:
            return
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write("[%s] %s\n" % (stamp, text))

    # ---- Observe: duoc aiocoap goi khi so Client dang ky thay doi ----
    def update_observation_count(self, newcount):
        if newcount > self.observer_count:
            print("New Observe registration received (observers: %d)" % newcount)
        elif newcount < self.observer_count:
            print("Observe registration cancelled (observers: %d)" % newcount)
        self.observer_count = newcount

    # ---- GET ----
    async def render_get(self, request):
        return Message(code=Code.CONTENT, payload=self._status_payload(),
                       content_format=CF_JSON)

    # ---- PUT ----
    async def render_put(self, request):
        print("PUT request received:")
        try:
            body = json.loads(request.payload.decode("utf-8"))
            device = body["device_id"]
            command = str(body["command"]).strip().upper()
        except (ValueError, KeyError, TypeError, UnicodeDecodeError):
            print("Payload khong hop le -> 4.00 Bad Request\n")
            return Message(code=Code.BAD_REQUEST, payload=b"Payload JSON khong hop le")

        print("Device: %s" % device)
        print("Command: %s" % command)

        if device != DEVICE_ID:
            print("Sai device_id -> 4.04 Not Found\n")
            return Message(code=Code.NOT_FOUND, payload=b"Khong tim thay thiet bi")
        if command not in ("ON", "OFF"):
            print("Lenh khong hop le -> 4.00 Bad Request\n")
            return Message(code=Code.BAD_REQUEST, payload=b"Lenh khong hop le (chi ON/OFF)")

        old = self.status
        if command == old:
            print("Light state unchanged: %s\n" % old)
            word = "bat" if old == "ON" else "tat"
            return Message(code=Code.CHANGED,
                           payload=("Den %s da duoc %s tu truoc" % (DEVICE_ID, word)).encode("utf-8"))

        self.status = command
        print("Light state changed: %s -> %s" % (old, command))
        self._write_log("%s: %s -> %s" % (DEVICE_ID, old, command))
        print("Notify observers: %s\n" % command)
        self.updated_state()  # gui thong bao toi moi Client dang Observe

        word = "bat" if command == "ON" else "tat"
        return Message(code=Code.CHANGED,
                       payload=("Da %s den %s" % (word, DEVICE_ID)).encode("utf-8"))


async def main(host, port, log_path):
    root = resource.Site()
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader),
    )
    root.add_resource(["iot", "lab", DEVICE_ID, "status"], LightStatusResource(log_path))

    await aiocoap.Context.create_server_context(root, bind=(host, port))
    print("CoAP Smart Light Server started...")
    print("Resource: /iot/lab/%s/status  (GET, PUT, Observe)" % DEVICE_ID)
    print("Trang thai ban dau: OFF. Nhan Ctrl+C de dung.")
    print()
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 3 - Smart Light CoAP Server")
    parser.add_argument("--host", default="::")
    parser.add_argument("--port", type=int, default=5683)
    parser.add_argument("--log", default=None, help="ghi nhat ky thay doi trang thai ra file")
    args = parser.parse_args()
    try:
        asyncio.run(main(args.host, args.port, args.log))
    except KeyboardInterrupt:
        print("\nSmart Light Server stopped.")
