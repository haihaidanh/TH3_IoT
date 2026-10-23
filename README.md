# CoAP_Lab - Lập trình Python với giao thức CoAP

Bài thực hành buổi 3: xây dựng CoAP Server và CoAP Client bằng Python (thư viện `aiocoap`) để mô phỏng các bài toán giám sát và điều khiển thiết bị IoT.

---

## Mục lục

- [Thông tin sinh viên thực hiện](#thông-tin-sinh-viên-thực-hiện)
- [1. Cấu trúc thư mục](#1-cấu-trúc-thư-mục)
- [2. Môi trường và cài đặt](#2-môi-trường-và-cài-đặt)
- [3. Địa chỉ, cổng và URI tài nguyên](#3-địa-chỉ-cổng-và-uri-tài-nguyên)
- [4. Cách chạy từng chương trình](#4-cách-chạy-từng-chương-trình)
  - [Bài 1 - Gửi và nhận thông điệp CoAP cơ bản](#bài-1---gửi-và-nhận-thông-điệp-coap-cơ-bản)
  - [Bài 2 - Mô phỏng cảm biến nhiệt độ và độ ẩm](#bài-2---mô-phỏng-cảm-biến-nhiệt-độ-và-độ-ẩm)
  - [Bài 3 - Đèn thông minh với CoAP Observe](#bài-3---đèn-thông-minh-với-coap-observe)
- [5. Mô tả cách thực hiện](#5-mô-tả-cách-thực-hiện)
  - [Bài 1](#bài-1)
  - [Bài 2](#bài-2)
  - [Bài 3](#bài-3)
- [6. Kết quả đạt được](#6-kết-quả-đạt-được)
  - [Bài 1](#bài-1-1)
  - [Bài 2](#bài-2-1)
  - [Bài 3](#bài-3-1)
- [7. Log minh chứng](#7-log-minh-chứng)
  - [Bài 1](#bài-1-2)
  - [Bài 2](#bài-2-2)
  - [Bài 3](#bài-3-2)
- [8. Xử lý sự cố thường gặp](#8-xử-lý-sự-cố-thường-gặp)

---

## Thông tin sinh viên thực hiện

| STT | Họ và tên | Mã sinh viên | Lớp |
|:---:|---|:---:|:---:|
| 1 | Nguyễn Danh Hải | B23DCCN274 | D23CQCN08-B |
| 2 | Nguyễn Quang Huy | B23DCCN400 | D23CQCN08-B |

---

## 1. Cấu trúc thư mục

```text
CoAP_Lab/
|
|-- bai1/
|   |-- coap_server_bai1.py
|   |-- coap_client_bai1.py
|
|-- bai2/
|   |-- sensor_server_bai2.py
|   |-- monitor_client_bai2.py
|
|-- bai3/
|   |-- light_server_bai3.py
|   |-- light_controller_bai3.py
|   |-- light_monitor_bai3.py
|
|-- requirements.txt
|-- README.md
```

## 2. Môi trường và cài đặt

- Python 3.9 trở lên (khuyến nghị 3.10+).
- Thư viện: `aiocoap` (xem `requirements.txt`).
- Không cần MQTT Broker hay RabbitMQ.

Cài đặt:

```bash
# (Tùy chọn) tạo môi trường ảo
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# Cài thư viện
pip install -r requirements.txt
```

Kiểm tra cài đặt thành công:

```bash
python -c "import aiocoap; print(aiocoap.__version__)"
```

## 3. Địa chỉ, cổng và URI tài nguyên

CoAP chạy trên UDP, cổng mặc định là **5683**. Mặc định Server lắng nghe trên mọi địa chỉ (`::`), Client kết nối tới `localhost`.

| Bài | URI | Phương thức |
|---|---|---|
| 1 | `coap://localhost:5683/iot/lab/message` | GET, POST |
| 2 | `coap://localhost:5683/iot/lab/sensor01/data` | GET |
| 3 | `coap://localhost:5683/iot/lab/light01/status` | GET, PUT, Observe |

Chạy Server và Client trên hai máy khác nhau: dùng tham số `--host <IP máy Server>` ở phía Client và cho phép UDP cổng 5683 qua tường lửa của máy Server.

Tham số chung của các chương trình:

| Tham số | Áp dụng cho | Ý nghĩa |
|---|---|---|
| `--host` | Server: địa chỉ bind (mặc định `::`). Client: địa chỉ Server (mặc định `localhost`) | |
| `--port` | Tất cả | Cổng UDP (mặc định 5683) |
| `--timeout` | Client | Thời gian chờ phản hồi, đơn vị giây (mặc định 5) |

## 4. Cách chạy từng chương trình

Mỗi bài cần mở nhiều cửa sổ terminal. **Luôn chạy Server trước**, sau đó chạy Client. Mỗi bài dùng cổng 5683 nên chỉ chạy Server của **một bài tại một thời điểm** (dừng Server bằng `Ctrl+C` trước khi sang bài khác).

### Bài 1 - Gửi và nhận thông điệp CoAP cơ bản

Terminal 1 - Server:

```bash
cd bai1
python coap_server_bai1.py
```

Terminal 2 - Client:

```bash
cd bai1
python coap_client_bai1.py
```

Tùy chọn mở rộng của Client:

```bash
python coap_client_bai1.py --count 3      # gửi 3 thông điệp POST liên tiếp, rồi GET lại
python coap_client_bai1.py --test-404     # truy cập tài nguyên không tồn tại (nhận 4.04)
```

### Bài 2 - Mô phỏng cảm biến nhiệt độ và độ ẩm

Terminal 1 - Sensor Server (dữ liệu cập nhật mỗi 3 giây):

```bash
cd bai2
python sensor_server_bai2.py
```

Terminal 2 - Monitoring Client (GET mỗi 3 giây, dừng bằng `Ctrl+C`):

```bash
cd bai2
python monitor_client_bai2.py
```

Tùy chọn mở rộng:

```bash
python monitor_client_bai2.py --device sensor02    # chọn cảm biến sensor01 / sensor02 / sensor03
python monitor_client_bai2.py --csv data.csv       # ghi dữ liệu nhận được ra file CSV
```

Khi dừng bằng `Ctrl+C`, Client in tổng số lần GET và thời gian phản hồi trung bình.

### Bài 3 - Đèn thông minh với CoAP Observe

Cần 3 terminal, chạy theo thứ tự:

```bash
# Terminal 1 - Smart Light Server
cd bai3
python light_server_bai3.py

# Terminal 2 - Monitoring Client (đăng ký Observe)
cd bai3
python light_monitor_bai3.py

# Terminal 3 - Controller Client (nhập lệnh)
cd bai3
python light_controller_bai3.py
```

Các lệnh của Controller:

| Lệnh | Tác dụng |
|---|---|
| `ON` | Gửi PUT bật đèn |
| `OFF` | Gửi PUT tắt đèn |
| `STATUS` | Gửi GET lấy trạng thái hiện tại |
| `BAD` | Kiểm thử: gửi lệnh không hợp lệ, Server trả mã `4.00 Bad Request` |
| `EXIT` | Thoát chương trình |

Tùy chọn mở rộng: `python light_server_bai3.py --log light_log.txt` để ghi nhật ký thay đổi trạng thái ra file.

## 5. Mô tả cách thực hiện

### Bài 1

- Server định nghĩa `MessageResource` tại `/iot/lab/message`.
- `GET` trả về `Xin chao tu CoAP Server`, mã `2.05 Content`.
- `POST` nhận thông điệp, in nội dung và thời điểm nhận, trả về `Server da nhan thong diep`, mã `2.04 Changed`. Payload rỗng bị từ chối bằng `4.00 Bad Request`.
- Client gửi GET rồi POST với nội dung `Xin chao tu CoAP Client - B23DCCN274, B23DCCN400 - Nguyen Danh Hai, Nguyen Quang Huy`.

### Bài 2

- Server tạo tài nguyên `/iot/lab/<device>/data`, một tác vụ nền sinh nhiệt độ (20 - 40 °C) và độ ẩm (30 - 90 %) ngẫu nhiên mỗi 3 giây.
- Phản hồi GET là JSON `{"device_id", "temperature", "humidity", "timestamp"}` với Content-Format `application/json` (mã 50).
- Client GET mỗi 3 giây, phân tích JSON, in mã thiết bị, nhiệt độ, độ ẩm, thời điểm nhận. Cảnh báo `CANH BAO: Nhiet do cao` khi nhiệt độ > 35 và `CANH BAO: Do am thap` khi độ ẩm < 40; nếu không có cảnh báo thì in `Trang thai: Binh thuong`.
- Khi Server không phản hồi, Client báo timeout và tiếp tục vòng giám sát.

### Bài 3

- Server dùng `ObservableResource` của `aiocoap` cho `/iot/lab/light01/status`; trạng thái ban đầu `OFF`.
- `PUT` nhận JSON `{"device_id": "light01", "command": "ON|OFF"}`. Lệnh hợp lệ làm đổi trạng thái thì Server gọi `updated_state()` để thông báo tới mọi Client đang Observe. Nếu lệnh trùng trạng thái hiện tại thì không gửi thông báo.
- Lệnh sai hoặc payload không phải JSON hợp lệ trả `4.00 Bad Request`; sai `device_id` trả `4.04 Not Found`.
- Monitoring Client gửi GET kèm tùy chọn Observe để đăng ký, nhận trạng thái ban đầu rồi chờ Server chủ động đẩy thông báo. Chương trình **không** dùng vòng lặp GET định kỳ.
- Có thể chạy nhiều Monitoring Client cùng lúc, tất cả đều nhận thông báo.

## 6. Kết quả đạt được

### Bài 1

- [x] Khởi tạo và chạy được CoAP Server trên cổng 5683.
- [x] Client gửi GET và POST, hiển thị mã phản hồi và payload.
- [x] Server xử lý riêng từng phương thức, hiển thị nội dung và thời điểm nhận POST.
- [x] Mở rộng: gửi nhiều POST liên tiếp, GET trả về thông điệp POST gần nhất, xử lý URI không tồn tại (4.04), xử lý timeout khi Server không chạy.

### Bài 2

- [x] Server cung cấp dữ liệu cảm biến qua URI, cập nhật mỗi 3 giây.
- [x] Payload JSON, Content-Format `application/json`.
- [x] Client GET định kỳ, phân tích JSON, cảnh báo đúng điều kiện, dừng bằng `Ctrl+C`.
- [x] Xử lý timeout và dữ liệu JSON lỗi.
- [x] Mở rộng: trường `timestamp`, ba cảm biến `sensor01` - `sensor03`, chọn thiết bị bằng `--device`, ghi CSV bằng `--csv`, thống kê số lần GET và thời gian phản hồi trung bình.

### Bài 3

- [x] Server quản lý tài nguyên đèn `light01`, hỗ trợ GET, PUT, Observe.
- [x] Controller gửi ON / OFF / STATUS, hiển thị mã phản hồi.
- [x] Monitoring Client đăng ký Observe và nhận thông báo tự động khi trạng thái thay đổi.
- [x] Kiểm tra lệnh không hợp lệ, nhiều Monitoring Client cùng Observe, ghi nhật ký ra file (`--log`).

## 7. Log minh chứng

### Bài 1

Client:

```text
Sending GET request...
URI: coap://127.0.0.1:5683/iot/lab/message

Response:
Code: 2.05 Content
Sending GET request...
URI: coap://127.0.0.1:5683/iot/lab/message

Response:
Code: 2.05 Content
Payload: Xin chao tu CoAP Server

Sending POST request... (1/1)
Payload: Xin chao tu CoAP Client - B23DCCN274, B23DCCN400 - Nguyen Danh Hai, Nguyen Quang Huy

Response:
Code: 2.04 Changed
Payload: Server da nhan thong diep
```

Server:

```text
CoAP Server started on port 5683
Resource: /iot/lab/message  (GET, POST)
Nhan Ctrl+C de dung server.

GET request received: /iot/lab/message

POST request received:
Payload: Xin chao tu CoAP Client - B23DCCN274, B23DCCN400 - Nguyen Danh Hai, Nguyen Quang Huy

GET request received: /iot/lab/message

POST request received:
Payload: Xin chao tu CoAP Client - B23DCCN274, B23DCCN400 - Nguyen Danh Hai, Nguyen Quang Huy
Time: 22:57:52


CoAP Server stopped.
```

### Bài 2

Server:

```text
Sensor CoAP Server started on port 5683
Resource: /iot/lab/sensor01/data  (GET, JSON)
Resource: /iot/lab/sensor02/data  (GET, JSON)
Resource: /iot/lab/sensor03/data  (GET, JSON)
Cap nhat du lieu moi 3 giay. Nhan Ctrl+C de dung.



[23:24:08] GET /iot/lab/sensor02/data -> {"device_id": "sensor02", "temperature": 20.1, "humidity": 77.9, "timestamp": "2026-10-23 23:24:07"}
[23:24:11] GET /iot/lab/sensor02/data -> {"device_id": "sensor02", "temperature": 30.5, "humidity": 60.4, "timestamp": "2026-10-23 23:24:10"}
[23:24:14] GET /iot/lab/sensor02/data -> {"device_id": "sensor02", "temperature": 25.2, "humidity": 88.3, "timestamp": "2026-10-23 23:24:13"}
[23:24:17] GET /iot/lab/sensor02/data -> {"device_id": "sensor02", "temperature": 31.8, "humidity": 45.2, "timestamp": "2026-10-23 23:24:16"}
[23:24:20] GET /iot/lab/sensor02/data -> {"device_id": "sensor02", "temperature": 30.7, "humidity": 85.5, "timestamp": "2026-10-23 23:24:19"}
[23:24:23] GET /iot/lab/sensor02/data -> {"device_id": "sensor02", "temperature": 38.8, "humidity": 55.9, "timestamp": "2026-10-23 23:24:22"}


Sensor CoAP Server stopped.
```

Monitoring Client:

```text
Monitoring: coap://127.0.0.1:5683/iot/lab/sensor02/data
Nhan Ctrl+C de dung.
------------------------------
[23:24:08] Received sensor data
Device: sensor02
Temperature: 20.1 C
Humidity: 77.9 %
Trang thai: Binh thuong
------------------------------
[23:24:11] Received sensor data
Device: sensor02
Temperature: 30.5 C
Humidity: 60.4 %
Trang thai: Binh thuong
------------------------------
[23:24:14] Received sensor data
Device: sensor02
Temperature: 25.2 C
Humidity: 88.3 %
Trang thai: Binh thuong
------------------------------
[23:24:17] Received sensor data
Device: sensor02
Temperature: 31.8 C
Humidity: 45.2 %
Trang thai: Binh thuong
------------------------------
Trang thai: Binh thuong
------------------------------
[23:24:20] Received sensor data
Device: sensor02
Temperature: 30.7 C
Humidity: 85.5 %
Trang thai: Binh thuong
------------------------------
[23:24:23] Received sensor data
Device: sensor02
Trang thai: Binh thuong
------------------------------
[23:24:20] Received sensor data
Device: sensor02
Temperature: 30.7 C
Humidity: 85.5 %
Trang thai: Binh thuong
------------------------------
[23:24:23] Received sensor data
Trang thai: Binh thuong
------------------------------
[23:24:20] Received sensor data
Device: sensor02
Temperature: 30.7 C
Humidity: 85.5 %
Trang thai: Binh thuong
------------------------------
Trang thai: Binh thuong
------------------------------
[23:24:20] Received sensor data
Device: sensor02
Temperature: 30.7 C
Trang thai: Binh thuong
------------------------------
[23:24:20] Received sensor data
Trang thai: Binh thuong
------------------------------
------------------------------
[23:24:20] Received sensor data
[23:24:20] Received sensor data
Device: sensor02
Device: sensor02
Temperature: 30.7 C
Humidity: 85.5 %
Trang thai: Binh thuong
Temperature: 30.7 C
Humidity: 85.5 %
Trang thai: Binh thuong
Humidity: 85.5 %
Trang thai: Binh thuong
------------------------------
[23:24:23] Received sensor data
------------------------------
[23:24:23] Received sensor data
Device: sensor02
Temperature: 38.8 C
Temperature: 38.8 C
Humidity: 55.9 %
CANH BAO: Nhiet do cao
------------------------------

Dung giam sat.
So lan GET: 6 | thanh cong: 6
Thoi gian phan hoi trung binh: 2.0 ms
```

### Bài 3

Smart Light Server:

```text
CoAP Smart Light Server started...
Resource: /iot/lab/light01/status  (GET, PUT, Observe)
Trang thai ban dau: OFF. Nhan Ctrl+C de dung.

New Observe registration received (observers: 1)
PUT request received:
Device: light01
Command: ON
Light state changed: OFF -> ON
Notify observers: ON

PUT request received:
Device: light01
Command: OFF
Light state changed: ON -> OFF
Notify observers: OFF
```

Monitoring Client:

```text
Registering CoAP Observe...
URI: coap://127.0.0.1:5683/iot/lab/light01/status
Observe registration successful

[00:00:35] Initial State
Device: light01
Status: OFF

[00:01:37] State Updated
Device: light01
Status: ON

[00:01:47] State Updated
Device: light01
Status: OFF
```

Controller Client:

```text
Nhap lenh (ON/OFF/STATUS/EXIT): abc
Lenh khong hop le. Chi chap nhan: ON, OFF, STATUS, EXIT

Nhap lenh (ON/OFF/STATUS/EXIT): on
Sending PUT request...
Response Code: 2.04 Changed
Da bat den light01

Nhap lenh (ON/OFF/STATUS/EXIT): status
Sending GET request...
Response:
{"device_id": "light01", "status": "ON"}

Nhap lenh (ON/OFF/STATUS/EXIT): off
Sending PUT request...
Response Code: 2.04 Changed
Da tat den light01

Nhap lenh (ON/OFF/STATUS/EXIT): status
Sending GET request...
Response:
{"device_id": "light01", "status": "OFF"}

Nhap lenh (ON/OFF/STATUS/EXIT): exit
Thoat chuong trinh.
```

## 8. Xử lý sự cố thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `ModuleNotFoundError: No module named 'aiocoap'` | Chạy `pip install -r requirements.txt` (đúng môi trường Python đang dùng). |
| Client báo timeout | Kiểm tra Server đã chạy chưa, đúng `--host` / `--port` chưa, tường lửa có chặn UDP 5683 không. |
| `OSError: address already in use` | Đang có Server khác dùng cổng 5683. Dừng Server cũ (`Ctrl+C`) rồi chạy lại. |
| Chạy hai máy khác nhau không kết nối được | Dùng IP của máy Server, mở UDP 5683 trên tường lửa. |

Toàn bộ nội dung hiển thị của chương trình dùng ký tự không dấu (ASCII) giống đề bài nên không bị lỗi font trên Command Prompt / PowerShell.
