# -*- coding: utf-8 -*-
"""
Bai 2 - Monitoring CoAP Client.

GET dinh ky (mac dinh 3 giay) toi coap://localhost:5683/iot/lab/<device>/data,
phan tich JSON, hien thi va canh bao. Dung bang Ctrl+C.

Chay: python monitor_client_bai2.py [--host localhost] [--port 5683]
                                    [--device sensor01] [--interval 3]
                                    [--csv log.csv] [--timeout 5]
"""
import argparse
import asyncio
import csv
import json
import os
import sys
import time
from datetime import datetime

import aiocoap
from aiocoap import Code, Message

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TEMP_LIMIT = 35.0   # do C
HUMI_LIMIT = 40.0   # %


def append_csv(path, row):
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["time", "device_id", "temperature", "humidity"])
        w.writerow(row)


async def main(args):
    uri = "coap://%s:%d/iot/lab/%s/data" % (args.host, args.port, args.device)
    protocol = await aiocoap.Context.create_client_context()
    total = ok = 0
    sum_ms = 0.0
    print("Monitoring: " + uri)
    print("Nhan Ctrl+C de dung.")
    print("-" * 30)
    try:
        while True:
            started = time.monotonic()
            now = datetime.now().strftime("%H:%M:%S")
            total += 1
            try:
                req = Message(code=Code.GET, uri=uri)
                resp = await asyncio.wait_for(
                    protocol.request(req).response, timeout=args.timeout
                )
                elapsed_ms = (time.monotonic() - started) * 1000
                if not resp.code.is_successful():
                    print("[%s] Server tra ve loi: %s" % (now, resp.code))
                else:
                    data = json.loads(resp.payload.decode("utf-8"))
                    dev = data["device_id"]
                    temp = float(data["temperature"])
                    humi = float(data["humidity"])
                    ok += 1
                    sum_ms += elapsed_ms

                    print("[%s] Received sensor data" % now)
                    print("Device: %s" % dev)
                    print("Temperature: %.1f C" % temp)
                    print("Humidity: %.1f %%" % humi)
                    warned = False
                    if temp > TEMP_LIMIT:
                        print("CANH BAO: Nhiet do cao")
                        warned = True
                    if humi < HUMI_LIMIT:
                        print("CANH BAO: Do am thap")
                        warned = True
                    if not warned:
                        print("Trang thai: Binh thuong")
                    if args.csv:
                        append_csv(args.csv, [now, dev, temp, humi])
            except asyncio.TimeoutError:
                print("[%s] Loi: Server khong phan hoi (timeout)" % now)
            except (json.JSONDecodeError, KeyError, ValueError, UnicodeDecodeError) as exc:
                print("[%s] Loi: du lieu JSON khong hop le (%r)" % (now, exc))
            except (aiocoap.error.Error, OSError) as exc:
                print("[%s] Loi ket noi: %r" % (now, exc))
            print("-" * 30)

            await asyncio.sleep(max(0.0, args.interval - (time.monotonic() - started)))
    finally:
        print("\nDung giam sat.")
        print("So lan GET: %d | thanh cong: %d" % (total, ok))
        if ok:
            print("Thoi gian phan hoi trung binh: %.1f ms" % (sum_ms / ok))
        await protocol.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 2 - Monitoring CoAP Client")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5683)
    parser.add_argument("--device", default="sensor01", help="sensor01 | sensor02 | sensor03")
    parser.add_argument("--interval", type=float, default=3.0, help="chu ky GET (giay)")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--csv", default=None, help="ghi du lieu ra file CSV")
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        pass
