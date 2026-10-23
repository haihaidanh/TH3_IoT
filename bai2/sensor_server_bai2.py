# -*- coding: utf-8 -*-
"""
Bai 2 - Sensor CoAP Server (mo phong cam bien nhiet do + do am).

Tai nguyen : coap://localhost:5683/iot/lab/sensor01/data
             (mo rong: sensor02, sensor03 cung chay tren server nay)
Phuong thuc: GET -> tra ve JSON gia tri cam bien moi nhat
Du lieu tu dong sinh ngau nhien moi 3 giay.

Chay: python sensor_server_bai2.py [--host ::] [--port 5683] [--interval 3]
"""
import argparse
import asyncio
import json
import random
import sys
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code, Message

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

CF_JSON = 50  # Content-Format cua application/json (RFC 7252 / IANA)
DEVICES = ["sensor01", "sensor02", "sensor03"]


class SensorResource(resource.Resource):
    """Tai nguyen /iot/lab/<device_id>/data."""

    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.data = {}
        self.refresh()  # co du lieu ngay tu dau

    def refresh(self):
        """Sinh gia tri moi trong khoang hop ly."""
        self.data = {
            "device_id": self.device_id,
            "temperature": round(random.uniform(20.0, 40.0), 1),  # do C
            "humidity": round(random.uniform(30.0, 90.0), 1),     # %
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    async def render_get(self, request):
        payload = json.dumps(self.data)
        print("[%s] GET /iot/lab/%s/data -> %s"
              % (datetime.now().strftime("%H:%M:%S"), self.device_id, payload))
        return Message(
            code=Code.CONTENT,
            payload=payload.encode("utf-8"),
            content_format=CF_JSON,
        )


async def updater(sensors, interval):
    """Cap nhat du lieu tat ca cam bien sau moi `interval` giay."""
    while True:
        await asyncio.sleep(interval)
        for s in sensors:
            s.refresh()


async def main(host, port, interval):
    root = resource.Site()
    root.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root.get_resources_as_linkheader),
    )
    sensors = []
    for dev in DEVICES:
        s = SensorResource(dev)
        sensors.append(s)
        root.add_resource(["iot", "lab", dev, "data"], s)

    await aiocoap.Context.create_server_context(root, bind=(host, port))
    task = asyncio.create_task(updater(sensors, interval))  # giu tham chieu
    print("Sensor CoAP Server started on port %d" % port)
    for dev in DEVICES:
        print("Resource: /iot/lab/%s/data  (GET, JSON)" % dev)
    print("Cap nhat du lieu moi %.0f giay. Nhan Ctrl+C de dung." % interval)
    print()
    try:
        await asyncio.get_running_loop().create_future()
    finally:
        task.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 2 - Sensor CoAP Server")
    parser.add_argument("--host", default="::")
    parser.add_argument("--port", type=int, default=5683)
    parser.add_argument("--interval", type=float, default=3.0, help="chu ky cap nhat (giay)")
    args = parser.parse_args()
    try:
        asyncio.run(main(args.host, args.port, args.interval))
    except KeyboardInterrupt:
        print("\nSensor CoAP Server stopped.")
