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

## Ngày 4 – 20/11 · Nguồn bụi mịn + SQL kiểm tra chất lượng

### 1. Profiling: biết nguồn trước khi tin nó
- **Profiling** = khám phá nguồn mới **1 lần** (lùi được bao xa, min/max, null ra sao). **Quality check** = luật cố định chạy **mỗi lần** pipeline chạy.
- 2 giới hạn khác nhau: API **cho hỏi** (Air Quality nhận từ 2013, trả 200) vs API **có số thật** (PM2.5 từ 2022-08-04, trước đó toàn `null`).
- `/forecast` chỉ nhận ~3 tháng trước → ~2 tuần tới, **cửa sổ trượt theo ngày** → dữ liệu cũ mất khỏi API → **raw là nguồn lịch sử duy nhất**, chạy hằng ngày, không xóa raw.
- 400 trả JSON `{"reason": ..., "error": true}` → đọc `reason` là biết giới hạn.
- 200 + đủ dòng vẫn có thể toàn `null` → cần check NULL, không chỉ check số dòng.

### 2. Thiết kế mở rộng nguồn
- **DRY**: `fetch_hourly` chung, mỗi nguồn 1 dòng → thêm nguồn = ~3 dòng.
- **Config-driven**: dict `SOURCES` (bảng, ánh xạ tên JSON → tên cột) → thêm nguồn = thêm cấu hình, không sửa logic.
- Lỗi 1 nguồn: **all-or-nothing** theo tỉnh (đồng bộ, mất phần tốt) vs **cô lập theo nguồn** (giữ phần tốt, `failed` theo cặp tỉnh-nguồn). Chọn có chủ đích.
- Tên bảng/cột không truyền bằng `%s` → `psycopg.sql.Identifier`.
- Chạy thử đừng ghi chung thư mục với pipeline thật (file `hcm.json` lạc → vỡ khóa ngoại).
- `DROP` + load chỉ partition mới nhất → mất lịch sử trong DB; raw còn → **backfill** (ngày 5–6).

### 3. Bộ check chất lượng (quy ước: 0 dòng = đạt)
| Check | Chiều | Mẫu SQL |
|---|---|---|
| DQ1 trùng | Uniqueness | `ROW_NUMBER() OVER (PARTITION BY khóa ORDER BY loaded_at DESC)` → `rn > 1` |
| DQ2 NULL | Completeness (cột) | `COUNT(*) FILTER (WHERE c IS NULL)` + `HAVING ... OR ...` |
| DQ3 vô lý | Validity | `x < min OR x > max` (= `NOT BETWEEN`) |
| DQ4 giờ đứt | Completeness (thời gian) | `LAG(ts) OVER (PARTITION BY thực_thể ORDER BY ts)` → `> INTERVAL '1 hour'` |
| DQ5 thiếu tỉnh | Completeness (thực thể) | `LEFT JOIN` từ bảng chuẩn, `COUNT(cột_bên_phải) <> 192` |
- Ngưỡng (0–1000, 5% NULL…) là **business rule**, hỏi nghiệp vụ, không tự đoán.

### 4. Lỗi tư duy hay gặp khi viết check
- **Viết ngược điều kiện**: lấy dòng tốt thay vì dòng lỗi (`rn = 1`, `> 0 AND < 10`, `= 1 hour`). Trước khi viết hỏi: *"dòng mình muốn thấy là dòng lỗi"*. Cách an toàn: viết điều kiện hợp lệ rồi `NOT (...)`.
- Check không bao giờ báo lỗi = cảm giác an toàn giả → **giả lập lỗi** để thử (xóa Lai Châu trong `BEGIN ... ROLLBACK`).
- `rn > 1` để **tìm** trùng; `rn = 1` để **khử** trùng (ngày 8).

### 5. Hàm cửa sổ: 2 câu hỏi
- `PARTITION BY`: mỗi nhóm độc lập là **cái gì**? (thường là thực thể: tỉnh).
- `ORDER BY`: thứ tự theo **cái gì**? (thường là thời gian sự kiện `ts_utc`, hiếm khi `loaded_at`).
- DQ1 tìm bản sao của *một dòng* → partition theo **mọi cột khóa**; DQ4 xét chuỗi của *một thực thể* → partition chỉ theo **thực thể**.
- Hàm cửa sổ tính **sau** `WHERE` → muốn lọc phải bọc CTE.
- `LAG` = dòng trước, `LEAD` = dòng sau. Dòng đầu nhóm có `LAG` = NULL → tự loại khỏi điều kiện so sánh.

### 6. SQL nền tảng
- Thứ tự xử lý: `FROM` → `WHERE` → `GROUP BY` → `HAVING` → hàm cửa sổ → `SELECT` → `ORDER BY`.
- `= NULL` luôn rỗng → dùng `IS NULL`.
- `COUNT(*)` đếm mọi dòng; `COUNT(cột)` bỏ qua NULL → dùng `COUNT(cột_bên_phải)` sau `LEFT JOIN`.
- `INNER JOIN` loại thực thể không khớp → bỏ sót tỉnh vắng mặt; đối soát luôn **`LEFT JOIN` từ bảng chuẩn**.
- `ts - ts` ra `INTERVAL`; viết `INTERVAL '1 hour'`.

## Ngày 5 – 21/11 · Pipeline v1: một lệnh chạy tất cả

### 1. ETL vs ELT
- **ETL**: biến đổi trước khi nạp. **ELT**: nạp gần nguyên bản, biến đổi bằng SQL trong kho.
- VietSky theo **ELT**: Python chỉ **đổi hình dạng** (cột → dòng, gắn múi giờ), không sửa giá trị; nghiệp vụ (trung bình 24h, AQI ngày) làm bằng SQL ở mart (ngày 8).
- Lợi ích: đổi logic → chạy lại SQL trên dữ liệu đã có, không gọi lại API.

### 2. Modularity + orchestrator
| Module | Chặng | Vào → Ra |
|---|---|---|
| `config.py` | Cấu hình | — → `SOURCES`, đường dẫn, `db_conninfo()` |
| `extract.py` | Extract + Landing | tọa độ → file raw JSON |
| `transform.py` | Transform | JSON cột → list tuple dòng |
| `load.py` | Load | list dòng → bảng staging, trả số dòng thực ghi |
| `run_log.py` | Observability | trạng thái chặng → `ops.pipeline_runs` |
| `pipelines/run_pipeline.py` | **Orchestrator** | `--date` → gọi lần lượt các chặng |
- Chỉ orchestrator biết thứ tự; module không gọi lẫn nhau → lỗi ở đâu biết ngay file nào. Ngày 11 Airflow thay vai orchestrator.
- Chia theo **nguồn**: nguồn này hỏng không chặn nguồn kia; cuối cùng `sys.exit(1)` nếu có chặng FAILED.

### 3. Configuration vs secrets
| Loại | Ví dụ | Để ở đâu |
|---|---|---|
| Secret / khác nhau giữa máy | mật khẩu, user, tên DB | file biến môi trường (không commit) |
| Công khai, giống mọi nơi | URL API, biến, tên bảng | `config.py` (commit) |
- **Single source of truth**: chuỗi biến gửi API (`api_variables`) sinh từ ánh xạ cột → extract và load không lệch nhau.
- `--date` (argparse, `type=date.fromisoformat`) thay `date.today()` cài cứng → chạy lại ngày bất kỳ → nền móng backfill.
- Đưa cấu hình công khai vào file biến môi trường → người khác quên thêm → `None` im lặng.

### 4. Pipeline metadata + đối soát
- Bảng `ops.pipeline_runs`: mỗi dòng = một **chặng** của một **nguồn** trong một **lần chạy** → PK `(run_id, stage, source)`.
- Quy tắc chọn khóa: "mỗi dòng là một ___ của một ___ trong một ___" → mỗi chỗ trống là một cột khóa.
- `run_date` (chạy cho ngày nào) ≠ `started_at` (bấm chạy lúc nào).
- Schema `ops` riêng, file DDL riêng **không `DROP`** → reset staging không mất lịch sử chạy.
- Đọc cặp số chặng load:

| rows_in | rows_out | Ý nghĩa |
|---|---|---|
| 6528 | 6528 | Dữ liệu mới |
| 6528 | 0 | Chạy lại, đã có hết → idempotent |
| 6528 | 192 | Bù được 1 tỉnh thiếu trước đó |
| 6528 | 6400 (lần đầu) | Rớt dòng → điều tra |

- `rows_out` = `cur.rowcount` (thực ghi), không phải `len(rows)` (gửi đi).

### 5. Observability
- 3 tầng: **logs** (chuyện gì xảy ra) · **metadata** (bao lâu, bao nhiêu dòng, đạt/rớt) · **data quality** (dữ liệu đúng không).
- Vòng đời chặng: INSERT `RUNNING` (commit ngay) → UPDATE `SUCCESS`/`FAILED`. Dòng **kẹt `RUNNING`** = process chết giữa chừng.
- **Dữ liệu có thể rollback, dấu vết vận hành thì không**: log commit riêng trước khi chạy chặng.
- "Thứ Bảy có chạy không?" → 1 câu SQL, ai có quyền DB cũng tự trả lời, không phụ thuộc máy/người.
- Log là **dòng trong bảng DB** (lưu vĩnh viễn), không phải `print` (mất khi đóng terminal).
- Log lộ ra 2 lần chạy song song (run_id xen kẽ) → cần khóa chặn chạy trùng.

### 6. Sự cố hôm nay: DB mất trắng
- Volume bị tạo lại → mất `dim_location` + staging. Raw còn nguyên → chạy pipeline 1 lệnh là dựng lại.
- Chứng minh thiết kế ngày 1: **raw là nguồn sự thật, DB có thể dựng lại bất cứ lúc nào**.
- `docker compose down -v` xóa volume → cẩn thận.

### 7. Python
- Import theo **package**: `from vietsky.config import ...`, chạy bằng `PYTHONPATH=src`. PyCharm: Mark `src` as Sources Root.
- Type hint trả về là **kiểu**: `-> tuple[int, int]`, không phải tên biến.
- `conn.execute(sql, (giá_trị, ...))`: tuple lấp vào các `%s` theo đúng thứ tự; hàm định nghĩa cách dùng tham số, nơi gọi cung cấp giá trị.
- `@dataclass(frozen=True)` + `@property` cho cấu hình.
- `date - timedelta(days=n)`, không trừ thẳng số nguyên.
- Giá trị chữ trong SQL phải có nháy đơn (`'weather'`), không có nháy = tên cột.
- `DO NOTHING` giữ số cũ → bản dự báo mới không được cập nhật (lỗi im lặng tiềm ẩn) → upsert ở ngày 6.

## Ngày 6 – 23/11 · Độ tin cậy + backfill lịch sử

### 1. Upsert và cách chứng minh idempotency
- `ON CONFLICT (location_id, ts_utc) DO UPDATE SET col = EXCLUDED.col, loaded_at = now()`: có rồi thì ghi đè, chưa có thì chèn. `EXCLUDED` = dòng vừa định chèn.
- Lý do: dự báo và dữ liệu gần đây bị nguồn sửa lại (late-arriving data). `DO NOTHING` giữ số cũ sai mà không báo lỗi.
- Với upsert, `rowcount` đếm cả dòng bị ghi đè → chạy lại vẫn `rows_out = rows_in`. **Bằng chứng idempotent giờ là `COUNT(*)` trước = sau**, `loaded_at` cho biết lần ghi cuối.
- Muốn `rows_out` chỉ đếm dòng thật sự đổi: thêm `WHERE (cột cũ) IS DISTINCT FROM (EXCLUDED.cột)`.

### 2. Retry + backoff + timeout
| Loại lỗi | Ví dụ | Xử lý |
|---|---|---|
| Tạm thời phía server | 429, 500, 502, 503, 504 | Ghi lỗi, chờ, thử lại |
| Mạng | Timeout, ConnectionError | Ghi lỗi, chờ, thử lại |
| Do mình | 400, 404 | Ném ngay, thử lại vô ích |
- Chờ tăng dần 2 → 4 → 8s (exponential backoff): gọi lại ngay khi bị 429 chỉ bị chặn tiếp.
- Hết lượt → `raise` to rõ để `run_stage` ghi FAILED. `timeout=30` để request treo không giữ cả pipeline.
- Bẫy: `raise` bên trong `try` = thoát hàm ngay → vòng retry chỉ chạy 1 lần. Lỗi tạm thời phải **ghi lại** (`error = ...`), không ném.

### 3. Backfill
- Backfill = nạp bù một khoảng quá khứ một lần; incremental = mỗi ngày nạp phần mới; full load = nạp lại tất cả.
- **Chunking** theo năm: response vừa phải, lỗi chỉ mất một đoạn. Đoạn nối nhau không trùng, không hở (`cur = chunk_end + 1 ngày`).
- **Checkpoint**: commit sau mỗi tỉnh-năm. Chết giữa chừng thì phần trước còn; nhờ upsert chạy lại từ đầu vẫn an toàn.
- Giới hạn nguồn nằm trong config (`history_start`), code kẹp `max(start, history_start)`.
- Ước tính thời gian = số lần gọi (năm × tỉnh × nguồn) × giây/lần: 340 × ~2,3s ≈ 13 phút (thực tế 14,5).
- Raw lịch sử tách riêng `data/raw/{source}/backfill/` để không lẫn vào load hằng ngày.

### 4. Kiểm chứng sau khi nạp lớn
- Số dòng mỗi năm = 34 × 24 × số ngày (năm nhuận 298.656).
- DQ4 (khe hở giờ) = 0 trên toàn lịch sử → mép nối backfill/daily liền.
- NULL giải thích được (7 giờ đầu 04/08/2022) ghi vào README, không xem là lỗi.
- Biểu đồ "nhìn hợp lý" chưa chắc đúng: mùa vụ PM2.5 Hà Nội yếu hơn kỳ vọng → nguồn là mô hình, cần đối chiếu.

### 5. Python
- `chunks, cur = [], start` (tên bên trái, giá trị bên phải). `chunks = [], cur = start` là gán chuỗi + unpack → lỗi.
- Chạy script từ terminal: `PYTHONPATH=src .venv/bin/python pipelines/x.py`.
- Hàm dùng chung cho nhiều script (`run_stage`) đặt trong package, không đặt trong script.
