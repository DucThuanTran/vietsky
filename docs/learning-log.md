# VietSky – Sổ tay kiến thức

## Ngày 1 – 17/11 · Dòng dữ liệu thật đầu tiên

### 1. Tư duy pipeline
- Pipeline = chuỗi chặng, mỗi chặng **đọc đầu ra của chặng trước**. Hôm nay: Extract (API → dict) → Landing/raw (dict → file JSON) → Visualization (file JSON → biểu đồ).
- **Raw lưu nguyên bản, không sửa** → lưu vết (lineage), chạy lại khi đổi logic (reprocess), không mất dữ liệu khi API đổi/sập.
- **Raw ≠ Staging**: raw là file gốc; staging là bảng trong Postgres (ngày 3).
- **Partition theo ngày chạy** `date=<RUN_DATE>`, không theo ngày dữ liệu → không ghi đè bản cũ (dự báo hôm nay ≠ số đo ngày mai).
- Chạy nhiều lần/ngày vẫn bị đè → thực tế thêm giờ chạy hoặc `run_id`. Dự án chạy 1 lần/ngày nên tạm đủ.
- 💼 Pipeline lỗi → câu hỏi đầu tiên: **lỗi ở chặng nào?**

### 2. Mã HTTP và cách xử lý
| Mã | Ý nghĩa | Xử lý |
|---|---|---|
| 200 | OK | Vẫn kiểm tra nội dung |
| 400 | Request sai (tham số, định dạng) | **Không retry**, đọc `reason`, sửa code |
| 429 | Gọi quá nhiều (rate limit) | **Chờ** rồi retry, theo `Retry-After` nếu có |
| 5xx | Server lỗi | Retry vài lần, chờ tăng dần (backoff), hết lượt → dừng + log |

- **4xx = lỗi phía mình, 5xx = lỗi phía họ.**
- Mọi request ra mạng phải có `timeout` (giây: `timeout=30`).
- Lỗi thì **raise** (`raise_for_status()`), không `return None` im lặng.

### 3. Kiểm tra 3 tầng khi gọi API
1. **Mạng**: kết nối được không? (Timeout, ConnectionError)
2. **HTTP**: status code?
3. **Nội dung**: có key cần thiết? list rỗng? các list dài bằng nhau? số dòng đúng kỳ vọng? (7 ngày × 24 = 168)

### 4. Tự khoanh vùng lỗi
- **Xem, đừng đoán**: `print(response.url)` xem request thật; `data.keys()` xem cấu trúc JSON.
- Ví dụ 400: 4xx → nghi tham số → soi URL → `2026-011-01` sai định dạng.
- Đối chiếu con số: số dòng thực tế vs kỳ vọng; path in ra vs path trong code.
- Sửa từng lỗi một, chạy lại sau mỗi lần sửa.

### 5. Python
- Tham số hàm nhận giá trị **lúc gọi**: `data = load_raw(...)` → `plot_temperature(data, ...)`.
- Mỗi hàm một việc: fetch / save / load / plot.
- `requests.get(url, params=dict, timeout=30)` tự ghép và mã hóa URL.
- `Path(...).parent.mkdir(parents=True, exist_ok=True)`; đường dẫn tương đối tính theo thư mục đang chạy.
- Tách biến tránh lặp: `hourly = data["hourly"]`.

### 6. JSON vs CSV
- `json.load(f)` → **dict lồng**, truy cập từng tầng `data["hourly"]["time"]`.
- `csv.DictReader` → list dict (mỗi dict 1 dòng); `pd.read_csv` → DataFrame.
- JSON Open-Meteo dạng cột (các list song song) → `pd.DataFrame(data["hourly"])` thành bảng.
- `px.line` cần cài `pandas` + `numpy`.

### 7. Múi giờ
- Open-Meteo mặc định GMT; đặt `Asia/Ho_Chi_Minh` (+7).
- Sanity check: đỉnh nóng phải ở trưa/đầu chiều giờ địa phương.

### 8. Git và đặt tên
- `.gitignore`: `data/`, `.env`, `.venv/`, `.idea/`, `.DS_Store`.
- `git status -sb` thấy `ahead N` = còn N commit chưa push.
- Commit message mô tả đúng việc, không ghi `update`.
- Đổi tên file đã track: `git mv`.
- Tên file: chữ thường, không dấu, không cách.

## Ngày 2 – 18/11 · Dữ liệu tham chiếu 34 tỉnh thành

### 1. Dữ liệu tham chiếu (reference / master data)
- Dữ liệu ít thay đổi, làm "danh bạ" cho dữ liệu khác: mã tỉnh, tên, vùng, tọa độ.
- Sai ở đây là **lỗi im lặng**: code chạy, biểu đồ đẹp, nhưng dữ liệu cả tỉnh sai từ gốc và lan xuống mọi bảng sau. Lỗi 500 thì "ồn", dễ thấy.
- Lưu vết bằng cột `search_name` (lấy từ đâu) và `note` (sửa tay vì sao).
- Dữ liệu ngoài (GeoNames) có thể **chưa cập nhật** thực tế (sáp nhập 01/7/2025) → không tin mù quáng.
- Ngày 8 trở thành bảng chiều `dim_location`, `province_code` là khóa.

### 2. Kiểm tra chất lượng: 3 chiều cơ bản
| Chiều | Câu hỏi | Kiểm tra |
|---|---|---|
| Completeness (đầy đủ) | Đủ 34 tỉnh? | Đếm dòng |
| Uniqueness (duy nhất) | Có trùng? | `set` các tên đã thấy |
| Validity (hợp lệ) | Tọa độ trong VN? | Là số và nằm trong khung lat 8–24, lon 102–110 |
- Hàm check **không sửa dữ liệu**, chỉ trả danh sách lỗi.
- **Cố tình làm hỏng dữ liệu** để chứng minh validator bắt được lỗi. Validator luôn báo đạt = cảm giác an toàn giả.
- Khung chữ nhật vẫn có thể lọt tọa độ của Lào/Campuchia → giới hạn của kiểm tra đơn giản.

### 3. Thiết kế vòng lặp extract
- **Config-driven**: đọc danh sách tỉnh từ CSV, không cài cứng.
- **Validate trước, extract sau (fail fast)**: lỗi đầu vào ảnh hưởng mọi tỉnh → dừng ngay, không tốn 34 lần gọi API.
- **`try/except` trong vòng `for`** (cô lập lỗi): 1 tỉnh lỗi → log ERROR, chạy tiếp; cuối có danh sách `failed` để chạy lại đúng tỉnh đó.
- **`sys.exit(1)`** khi có lỗi: công cụ điều phối (cron, Airflow) chỉ nhìn mã thoát (0 = thành công, khác 0 = thất bại) để quyết định chạy tiếp hay dừng.
- Nguyên tắc: chạy hết phần chạy được, rồi báo cáo trung thực.
- `time.sleep` giữa các lần gọi để tránh 429.
- Tên file theo `province_code` (cố định, không dấu, không trùng).

### 4. Khoanh vùng lỗi hôm nay
- API **lặng lẽ bỏ qua** tham số sai tên (`country_code` vs `countryCode`) → chỉ phát hiện khi nhìn dữ liệu trả về. Tài liệu (kể cả kế hoạch) cũng có thể sai.
- Kết quả "tìm thấy" chưa chắc đúng → đối chiếu với thực tế.
- Thụt lề sai làm logic chạy sai mà không báo lỗi → lần theo từng dòng xem nằm trong hay ngoài vòng lặp.
- Hai lần chạy cùng lúc ghi đè cùng file → cần `run_id` (ngày 5, 11).

### 5. Logging
- `logger = logging.getLogger(__name__)`; `logging.basicConfig(filename=..., level=..., format=...)`; tạo thư mục log trước.
- Level: INFO (bình thường), WARNING (bất thường nhưng chạy được), ERROR (thất bại).
- Viết `logger.info("%s: %d dòng", name, n)`, không dùng f-string.
- Log có thời gian và lưu ra file → người vận hành đọc lại sau.

### 6. Geocoding
- `feature_code`: PPLC thủ đô, PPLA tỉnh lỵ, PPLA2 trung tâm cấp 2, PPL điểm dân cư, ADM1 cả vùng hành chính.
- Tên không dấu/tiếng Anh (`Hanoi`) thường cho kết quả tốt hơn tên có dấu.
- Không có kết quả thì key `results` không tồn tại → `data.get("results", [])`.

### 7. Python và Git
- `csv.DictReader` → list dict, mọi giá trị là **chuỗi**; `float("")` → `ValueError`.
- `from extract import ...` chạy được khi chạy `python src/vietsky/x.py`; khối `__main__` không chạy khi bị import.
- `.gitignore` thêm `logs/`, `__pycache__/`; cuối file luôn có dòng trống.
- `config/provinces.csv` được commit (cấu hình), `data/` thì không.

## Ngày 3 – 19/11 · Database và tầng Staging

### 1. Staging layer và OLTP / OLAP
- Pipeline: Extract → Raw (file JSON) → **Staging (bảng Postgres)** → Mart (ngày 8).
- Staging = raw **đổi định dạng thành bảng**, chưa sửa nghiệp vụ. Giữ tên cột gần nguồn.
- **OLTP**: database ứng dụng, đọc/ghi từng dòng (đặt vé). **OLAP**: phân tích, quét nhiều dòng để tổng hợp (nhiệt TB theo vùng) → việc của DE.
- JSON API dạng **cột** (các list song song) → SQL cần dạng **dòng** (1 giờ × 1 tỉnh = 1 dòng) → `zip(..., strict=True)` (lệch độ dài thì báo lỗi, không cắt âm thầm).

### 2. Thiết kế bảng
- **DDL** (`CREATE`, `DROP`) định nghĩa cấu trúc; **DML** (`INSERT`, `SELECT`) thao tác dữ liệu.
- `location_id` kiểu `TEXT` để giữ số 0 đầu (`"01"`).
- Kiểu dữ liệu đúng = Postgres kiểm tra hộ: `NUMERIC(8,5)` tọa độ, `DOUBLE PRECISION` số đo, `TIMESTAMPTZ` thời gian.
- **Primary key ghép** `(location_id, ts_utc)`: một tỉnh, một thời điểm, một dòng.
- **Foreign key** `REFERENCES dim_location` → phải nạp bảng cha trước; `DROP` bảng con trước.
- `CHECK`, `NOT NULL` = đưa kiểm tra validity xuống database, chặn dữ liệu sai từ cửa.
- `loaded_at DEFAULT now()` → lưu vết lúc nạp.

### 3. Idempotent load
| Có PK | Có ON CONFLICT | Chạy lần 2 |
|---|---|---|
| ❌ | ❌ | Trùng gấp đôi (13 056 dòng) |
| ✅ | ❌ | Lỗi `UniqueViolation`, rollback, pipeline đỏ |
| ✅ | ✅ | Bỏ qua dòng trùng, vẫn 6528 → **idempotent** |
- Idempotent = chạy lại bao nhiêu lần kết quả vẫn như chạy 1 lần → an toàn để retry.
- `with psycopg.connect() as conn`: xong thì commit, lỗi thì **rollback cả transaction**.
- Bảng chiều nên **upsert** (`DO UPDATE SET ... = EXCLUDED....`) để cập nhật khi CSV đổi (ngày 8).

### 4. Múi giờ: lỗi im lặng
- API trả giờ địa phương **không kèm offset** (`2026-11-11T00:00`). Nạp thẳng → Postgres hiểu là UTC → lệch 7 tiếng, không báo lỗi.
- Sửa: gắn offset từ `utc_offset_seconds` (không cài cứng), lưu `TIMESTAMPTZ` (UTC).
- Kiểm tra: 00:00 VN phải thành `17:00+00` hôm trước.
- Truy vấn theo ngày VN: `(ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh')::date`.

### 5. Docker
- Container dùng xong bỏ (stateless); dữ liệu sống trong **named volume** (stateful). `down` giữ volume, `down -v` xóa volume.
- Tên volume ở service phải khớp khai báo `volumes:` cuối file.
- `ports: "5433:5432"` = cổng máy : cổng container. Cổng 5432 trên máy đã bị Postgres Homebrew chiếm.
- Mật khẩu trong file biến môi trường (bị ignore), không ghi vào compose (bị commit, nằm mãi trong lịch sử git).

### 6. Python + Postgres
- `psycopg`: `cur.execute(sql, params)` với `%s`, **không** f-string → chống SQL injection.
- `executemany` nạp cả list tuple một lần.
- `os.environ["X"]` (fail fast, đã sửa trong `load.py`) tốt hơn `.get("X")` (trả `None` im lặng).
- `load_dotenv()` nạp file biến môi trường vào `os.environ`.

### 7. SQL
- `ORDER BY ... NULLS LAST`; subquery trong `WHERE` (`= (SELECT MIN(...))`).
- `GROUP BY` lọc trước bằng `WHERE`, lọc sau gộp bằng `HAVING`.
- `LEFT JOIN` từ bảng chiều để bắt cả tỉnh có **0 dòng** (`JOIN` thường bỏ sót).
- `COUNT(*) FILTER (WHERE ...)` đếm nhiều điều kiện trong 1 lần quét.
- `ROUND(x::numeric, 1)`: `ROUND` 2 tham số cần kiểu `numeric`.
