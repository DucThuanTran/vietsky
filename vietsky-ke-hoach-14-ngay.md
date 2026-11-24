# VietSky – Kế hoạch dự án Data Engineering 14 ngày

> **Thời gian:** Thứ Ba 17/11 → Thứ Hai 30/11/2026 · **Mục tiêu:** vào làm ngày 01/12 với một dự án cá nhân hoàn chỉnh, nắm chắc khái niệm Data Engineering / Data Operations, SQL và Python tự viết được.
> **Cách dùng file này:** đưa vào phần tài liệu của một Project trên Claude. Mỗi ngày cập nhật mục "Nhật ký tiến độ" ở cuối file.

---

## 0. Hướng dẫn dành cho AI (đọc trước khi trả lời tôi)

**Về tôi**
- Cử nhân Khoa học Máy tính, chuyên ngành AI (thiên về applied AI). Sắp vào vị trí liên quan Data Engineering / Data Operations: đảm bảo pipeline dữ liệu chạy ổn định, truy lỗi xem phát sinh ở giai đoạn nào. Có thể liên quan dữ liệu bản đồ, dữ liệu lớn, môi trường bảo mật cao.
- Python: viết được mức cơ bản, quen dùng nhưng phụ thuộc AI khi viết chương trình lớn. SQL: mới học (JOIN, GROUP BY, CTE, window function) nhưng chưa vững. Linux, Docker, Git: cơ bản.
- Máy: MacBook M2 Pro, 16GB RAM. Học buổi sáng, 4 tiếng/ngày.

**Luật bắt buộc** (cập nhật 20/11/2026)
1. **Học Data Engineering, không phải học code.** Không dùng thang gợi ý cấp 1/2/3, không viết thẳng cả file. Với **Python**: đưa **pseudocode chi tiết** (từng bước rõ ràng, nêu tên hàm/thư viện cần dùng, dữ liệu vào/ra mỗi bước), mỗi bước kèm 1 dòng **ý nghĩa DE** (bước này phục vụ chặng nào, chống lỗi gì). Tôi tự chuyển thành code; AI kiểm tra, chạy và sửa lỗi cú pháp lặt vặt.
2. **Khi tôi nói "sửa", "làm luôn", "cung cấp toàn bộ" thì làm đúng như vậy**, không hỏi lại, không bắt tôi tự gõ. Nếu có điều quan trọng cần biết, nói ngắn sau khi làm xong.
3. **Câu hỏi kiểm tra tập trung vào giải quyết bài toán**, không hỏi kiểu đánh đố "vì sao dùng A thay vì B" hay chi tiết kỹ thuật thuần. Hỏi theo tình huống thật:
   - Pipeline gặp tình huống X → chuyện gì xảy ra, phát hiện bằng cách nào, xử lý ra sao?
   - Cần đạt mục tiêu Y → chia thành những bước nào, kiểm tra kết quả thế nào?
   - Nhìn số liệu/log này → có gì bất thường, lỗi nằm ở chặng nào?
   Mục tiêu: hình thành **khung tư duy có hệ thống**, nhìn ra vấn đề, biết xây dựng lời giải.
4. Khi giải thích khái niệm: **định nghĩa ngắn → vai trò → thuộc chặng nào của pipeline → ví dụ trong VietSky**. Mỗi khái niệm gắn vào một tình huống thực tế người DE gặp.
5. Khi có lỗi: chỉ ra **lỗi ở chặng nào, dấu hiệu nhận biết, cách khoanh vùng**, rồi sửa luôn. Bài học nằm ở cách truy lỗi, không ở việc tôi tự gõ lại.
6. **SQL** là kỹ năng cốt lõi của DE: đưa **pseudocode SQL rõ ràng** hoặc **khung truy vấn sẵn, để trống chỗ `___`** cho tôi điền từ khóa/biểu thức, kèm câu hỏi nghiệp vụ mà truy vấn trả lời. AI kiểm tra và chạy thử.
7. Cuối mỗi buổi, khi tôi gõ "tổng kết": ra **3 câu hỏi tình huống** (theo luật 3), AI tự ghi nhật ký (mục 7) và sổ tay `docs/learning-log.md`.
8. Nếu tôi lan man ngoài kế hoạch, nhắc quay lại mục "Bắt buộc" của ngày.
9. Trả lời bằng tiếng Việt, ngắn gọn, giữ thuật ngữ tiếng Anh gốc trong ngoặc. Hỏi trước khi commit.

---

## 1. Dự án là gì?

### VietSky: nền tảng dữ liệu thời tiết và chất lượng không khí cho 34 tỉnh thành Việt Nam

Một hệ thống dữ liệu hoàn chỉnh, chạy trên máy cá nhân theo kiểu **hạ tầng nội bộ (on-premise)**, giống môi trường data center:

- **Thu thập** dữ liệu **thật** theo giờ (thời tiết + bụi mịn PM2.5, PM10, AQI) cho 34 tỉnh thành từ API công khai Open-Meteo (miễn phí, không cần API key).
- **Nạp lại dữ liệu lịch sử 3 năm** (2023 → nay), khoảng 1,5–2 triệu dòng. Đủ lớn để cảm nhận được bài toán dữ liệu lớn.
- **Kiểm tra chất lượng** dữ liệu tự động, **ghi log từng chặng** của pipeline, **đối soát số dòng** giữa các tầng.
- **Điều phối** bằng Airflow theo lịch hằng ngày.
- **Dashboard 2 trang** đầy màu sắc:
  - 🌏 **"Bầu trời Việt Nam"**: bản đồ PM2.5 của 34 tỉnh thành, xu hướng theo mùa, heatmap giờ × tháng, tương quan mưa/gió với bụi mịn.
  - 🛠️ **"Phòng điều hành"** (DataOps): lịch sử các lần chạy, số dòng qua từng chặng, tỷ lệ đạt các bài kiểm tra chất lượng, độ mới của dữ liệu.
- **Diễn tập sự cố**: tự gây 6 loại lỗi, truy nguyên nhân và viết **báo cáo sự cố (postmortem)**. Đây là điểm khác biệt lớn nhất khi đưa vào CV.

### Vì sao chọn dự án này
| Yêu cầu của tôi | Dự án đáp ứng thế nào |
|---|---|
| Dữ liệu thật, từ đời sống, có lịch sử nhiều năm | Thời tiết và bụi mịn thật của Việt Nam, lùi lại nhiều năm |
| Sát với công việc | Toàn bộ trọng tâm là **pipeline ổn định + truy lỗi theo chặng**, đúng mô tả công việc |
| Có trực quan hóa đẹp như Data Science / Data Analytics | Bản đồ, heatmap, biểu đồ xu hướng, biểu đồ tương quan |
| Hấp dẫn, có câu hỏi để khám phá | Xem mục "Những câu hỏi dữ liệu sẽ trả lời" bên dưới |
| Chắc chắn hoàn thành | Mỗi ngày tách **Bắt buộc** và **Mở rộng**; pipeline chạy được từ đầu đến cuối ngay từ ngày 5 |
| Bản đồ / GIS | Tọa độ, khoảng cách, bản đồ điểm, kiểm tra tọa độ hợp lệ |

### Những câu hỏi dữ liệu sẽ trả lời (động lực để làm tiếp)
1. Hà Nội ô nhiễm nhất vào **tháng nào, giờ nào** trong ngày? Vì sao?
2. **Mưa có "rửa sạch" bụi mịn không?** Sau cơn mưa, PM2.5 giảm bao nhiêu %?
3. **Gió mạnh** thì không khí sạch hơn bao nhiêu?
4. **Miền Bắc và miền Nam** có mùa ô nhiễm khác nhau không?
5. Đêm giao thừa có làm PM2.5 tăng đột biến không, và **dữ liệu mô hình có "bắt" được hiện tượng đó không?** (câu hỏi rèn tư duy phản biện về nguồn dữ liệu)

> ⚠️ **Lưu ý về nguồn dữ liệu (data lineage):** dữ liệu chất lượng không khí của Open-Meteo đến từ **mô hình khí quyển** (Copernicus CAMS), **không phải trạm đo thực địa**. Dữ liệu thời tiết lịch sử là dữ liệu tái phân tích (reanalysis) và **thường trễ vài ngày** so với hiện tại. Biết rõ dữ liệu của mình đến từ đâu và giới hạn của nó là một kỹ năng của người làm data. Hãy ghi điều này vào README.

---

## 2. Kiến trúc

```
                    ┌──────────────────────────── Airflow (điều phối hằng ngày) ───────────────────────────┐
                    │                                                                                       │
 [Open-Meteo API]   │   EXTRACT          LANDING (data lake)        STAGING (Postgres)      MART (Postgres) │
  - Thời tiết   ────┼─► extract.py ───►  data/raw/…/date=…/*.json ─► stg_weather_hourly ───► fact_weather   │
  - Không khí   ────┼─►                  data/lake/…/*.parquet       stg_air_quality_hourly   fact_air_quality│
  - Geocoding   ────┼─► (1 lần)          config/provinces.csv ─────► dim_location ─────────► dim_location   │
                    │                                                                         dim_date       │
                    │        │                    │                        │                       │         │
                    │        └──────── ops.pipeline_runs (log từng chặng: rows_in, rows_out, status) ┘         │
                    │                           ops.dq_results (kết quả kiểm tra chất lượng)                 │
                    └───────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                          Streamlit + Plotly dashboard
                                   (🌏 Bầu trời Việt Nam  |  🛠️ Phòng điều hành)
```

**Công nghệ:** Python 3.11+, `requests`, `pandas`, `psycopg` (v3), `python-dotenv`, `pyarrow`, `duckdb`, `pytest`, `streamlit`, `plotly` · PostgreSQL 16 (Docker) · Airflow (Docker Compose) · Git + GitHub.

**Cấu trúc repo đích (đến ngày 14):**
```
vietsky/
├── README.md                  # giới thiệu, sơ đồ, cách chạy, ảnh dashboard, bài học
├── docker-compose.yml         # Postgres (+ Airflow ở ngày 11)
├── .env.example               # mẫu biến môi trường, KHÔNG commit .env thật
├── requirements.txt
├── config/provinces.csv       # 34 tỉnh thành: mã, tên, vùng, lat, lon
├── sql/
│   ├── 01_staging.sql
│   ├── 02_mart.sql
│   └── dq_checks.sql
├── src/vietsky/
│   ├── config.py   extract.py   transform.py   load.py
│   ├── quality.py  run_log.py   chaos.py
├── pipelines/run_pipeline.py  pipelines/backfill.py
├── dags/vietsky_daily.py
├── dashboard/app.py
├── tests/
├── data/                      # trong .gitignore
└── docs/
    ├── runbook.md             # "pipeline lỗi thì kiểm tra theo thứ tự nào"
    ├── incidents/             # 6 báo cáo sự cố
    └── learning-log.md
```

---

## 3. Hệ thống giữ kỷ luật và động lực

### Lịch mỗi ngày (ưu tiên buổi sáng)
| Khung giờ | Việc |
|---|---|
| **08:00 – 08:15** | **Khởi động ấm:** chạy lại pipeline/kết quả hôm qua, đọc mục "TODO cho mai" trong nhật ký |
| **08:15 – 09:00** | **Học khái niệm** của ngày (đọc/xem + hỏi AI theo luật ở mục 0) |
| **09:00 – 10:00** | **Xây dự án**, phiên 1 |
| 10:00 – 10:15 | Nghỉ, rời màn hình |
| **10:15 – 11:45** | **Xây dự án**, phiên 2 |
| **11:45 – 12:15** | **Đóng ngày:** commit + push, cập nhật nhật ký, tự trả lời 3 câu "Tự kiểm tra", ghi "TODO cho mai" |
| 14:00 – 15:00 | *Dự phòng*, **chỉ dùng khi chưa xong phần Bắt buộc** |
| Tối | Nghỉ, làm việc khác. Không học. |

### 7 luật chống nản
1. **Xong "Bắt buộc" là thắng.** "Mở rộng" chỉ làm nếu còn giờ. Không cầu toàn.
2. **Mỗi ngày phải có một "chiến thắng nhìn thấy được"**: một biểu đồ, một con số, một bảng dữ liệu. Chụp màn hình lưu vào `docs/screenshots/`.
3. **Commit mỗi ngày.** Nhìn chuỗi ô xanh trên GitHub dày lên chính là phần thưởng.
4. **Dừng ở chỗ dễ làm tiếp:** cuối ngày ghi rõ bước đầu tiên của ngày mai. Sáng hôm sau không phải nghĩ "bắt đầu từ đâu".
5. **Kẹt quá 30 phút** với một lỗi: hỏi AI theo thang gợi ý. **Kẹt quá 60 phút:** ghi lỗi vào nhật ký, tạm bỏ qua, chuyển sang việc khác. Lỗi đó sẽ thành tư liệu cho ngày 13.
6. **Không bao giờ bỏ 2 ngày liên tiếp.** Ngày mệt thì làm tối thiểu 30 phút để giữ nhịp.
7. **Ngày 7 và ngày 14 là ngày nhẹ**, dùng để bù trễ và tổng kết.

---

## 4. Kế hoạch 14 ngày

> Mỗi ngày gồm: 🎯 Mục tiêu · 📚 Học · 🔤 Thuật ngữ · 🐍/🗄️ Python/SQL rèn trong ngày · 🛠️ Xây dự án · ✅ Bắt buộc · ➕ Mở rộng · 🏆 Chiến thắng · ❓ Tự kiểm tra

---

### TUẦN 1: XÂY PIPELINE CHẠY ĐƯỢC TỪ ĐẦU ĐẾN CUỐI

---

### Ngày 1 · Thứ Ba 17/11 · Khởi động và dòng dữ liệu thật đầu tiên
🎯 Lấy được dữ liệu thật đầu tiên và vẽ biểu đồ đầu tiên.

📚 **Học:** pipeline dữ liệu là gì, các chặng của nó; API, HTTP GET, JSON; vì sao lưu dữ liệu thô (raw) trước khi xử lý.

🔤 **Thuật ngữ:** data pipeline · data source · ingestion · API · JSON · batch · landing zone / raw layer · data lake

🐍 **Python:** `requests`, `json`, `pathlib`, f-string, viết hàm có tham số và giá trị trả về.

🛠️ **Xây dự án:**
- [ ] Cài/kiểm tra: Python 3.11+, VS Code, Docker Desktop (hoặc OrbStack), DBeaver, tài khoản GitHub.
- [ ] Tạo repo `vietsky`, `git init`, tạo `.gitignore` (có `data/`, `.env`, `.venv/`), tạo venv, file `requirements.txt`.
- [ ] Viết `src/vietsky/extract.py` với hàm `fetch_weather(lat, lon, start, end)` gọi `https://api.open-meteo.com/v1/forecast` (các biến hourly: `temperature_2m, relative_humidity_2m, precipitation, wind_speed_10m`).
- [ ] Lưu kết quả **nguyên bản** vào `data/raw/weather/date=YYYY-MM-DD/hanoi.json`.
- [ ] Đọc file JSON đó, vẽ biểu đồ nhiệt độ Hà Nội 7 ngày bằng Plotly.
- [ ] Commit + push lên GitHub.

✅ **Bắt buộc:** có file JSON thật trong `data/raw/` + biểu đồ + commit đầu tiên.
➕ **Mở rộng:** thêm tham số `timezone`, thử so sánh dữ liệu khi để mặc định (GMT/UTC) và khi đặt `Asia/Ho_Chi_Minh`. Ghi lại khác biệt (bài học múi giờ, sẽ dùng ở ngày 13).
🏆 **Chiến thắng:** biểu đồ nhiệt độ Hà Nội do chính bạn lấy dữ liệu và vẽ.
❓ **Tự kiểm tra:** (1) Vì sao phải lưu dữ liệu thô nguyên bản thay vì xử lý luôn? (2) Pipeline của bạn hiện có mấy chặng? (3) API trả về 429 hoặc 500 thì nghĩa là gì?

---

### Ngày 2 · Thứ Tư 18/11 · Dữ liệu tham chiếu 34 tỉnh thành + terminal
🎯 Có bảng 34 tỉnh thành đã kiểm chứng và lấy dữ liệu cho cả 34.

📚 **Học:** dữ liệu tham chiếu/dữ liệu chủ là gì; vì sao phải kiểm tra dữ liệu đầu vào; logging thay cho `print`. Việt Nam có **34 đơn vị hành chính cấp tỉnh từ 01/7/2025** (28 tỉnh + 6 thành phố).

🔤 **Thuật ngữ:** reference data / master data · dimension · data validation · logging · log level (DEBUG/INFO/WARNING/ERROR) · rate limit

🐍 **Python:** đọc/ghi CSV, vòng lặp, `try/except`, module `logging`, `time.sleep` để gọi API lịch sự.

🛠️ **Xây dự án:**
- [ ] Dùng Open-Meteo Geocoding API (`https://geocoding-api.open-meteo.com/v1/search?name=...&country_code=VN`) để lấy tọa độ trung tâm hành chính của 34 tỉnh thành → `config/provinces.csv` (cột: `province_code, name, region, lat, lon`).
- [ ] **Kiểm tra dữ liệu:** viết hàm kiểm tra tọa độ nằm trong khung Việt Nam (lat ≈ 8–24, lon ≈ 102–110), không trùng tên, đủ 34 dòng. Geocoding có thể trả về **sai địa điểm trùng tên**; tìm và sửa tay những dòng sai, ghi chú lại.
- [ ] Viết vòng lặp lấy dữ liệu thời tiết cho cả 34 tỉnh, có `logging` và `sleep`.
- [ ] **Terminal:** dùng `ls`, `du -sh`, `wc -l`, `grep`, `head`, và `jq` (cài bằng `brew install jq`) để khám phá thư mục raw: có bao nhiêu file, tổng dung lượng, file nào nhỏ bất thường.

✅ **Bắt buộc:** `provinces.csv` đủ 34 dòng đã kiểm chứng + 34 file JSON + log ghi ra file.
➕ **Mở rộng:** thêm cột `former_provinces` (tỉnh cũ trước sáp nhập). Cột này sẽ dùng làm ví dụ SCD ở ngày 8.
🏆 **Chiến thắng:** bản đồ điểm 34 tỉnh thành (Plotly `scatter_map`) vẽ từ chính file của bạn.
❓ **Tự kiểm tra:** (1) Bạn đã phát hiện dòng sai trong geocoding bằng cách nào? (2) Log INFO và log ERROR khác nhau thế nào về mục đích? (3) Vì sao cần `sleep` khi gọi API?

---

### Ngày 3 · Thứ Năm 19/11 · Database và tầng Staging
🎯 Đưa dữ liệu từ file vào Postgres và trả lời câu hỏi đầu tiên bằng SQL.

📚 **Học:** schema, kiểu dữ liệu, khóa chính; OLTP và OLAP; staging layer dùng để làm gì.

🔤 **Thuật ngữ:** schema · DDL / DML · primary key · data type · staging layer · load · OLTP vs OLAP · connection string

🗄️ **SQL:** `CREATE TABLE`, `INSERT`, `SELECT/WHERE/ORDER BY`, `JOIN`, `GROUP BY/HAVING`.
🐍 **Python:** `psycopg`, câu lệnh `with` (context manager), truyền tham số an toàn vào SQL (không nối chuỗi).

🛠️ **Xây dự án:**
- [ ] `docker-compose.yml` chạy `postgres:16`, mật khẩu đặt trong `.env`.
- [ ] `sql/01_staging.sql`: tạo `dim_location` và `stg_weather_hourly(location_id, ts_utc, temperature_2m, humidity, precipitation, wind_speed, loaded_at)`.
- [ ] `src/vietsky/load.py`: đọc JSON raw → **chuyển từ dạng cột sang dạng dòng** → insert vào staging.
- [ ] Viết tay ít nhất **15 truy vấn** trong `sql/explore.sql`: tỉnh nóng nhất hôm nay, trung bình nhiệt theo vùng, tỉnh có mưa nhiều nhất…

✅ **Bắt buộc:** dữ liệu 34 tỉnh nằm trong Postgres + 15 truy vấn tự viết.
➕ **Mở rộng:** luyện thêm 10 bài trên pgexercises.com (phần Joins, Aggregates).
🏆 **Chiến thắng:** bảng "Top 5 tỉnh nóng nhất hôm nay" chạy từ chính database của bạn.
❓ **Tự kiểm tra:** (1) Vì sao dữ liệu API dạng "mảng theo cột" phải chuyển thành dạng dòng? (2) Khóa chính của `stg_weather_hourly` nên là gì? (3) Vì sao không được nối chuỗi khi đưa tham số vào SQL?

---

### Ngày 4 · Thứ Sáu 20/11 · Nguồn thứ hai (bụi mịn) + SQL kiểm tra chất lượng
🎯 Thêm dữ liệu chất lượng không khí và viết các truy vấn "bắt lỗi" dữ liệu.

📚 **Học:** các khía cạnh của chất lượng dữ liệu; data profiling; AQI và PM2.5 là gì (chuẩn AQI dựa trên trung bình 24 giờ).

🔤 **Thuật ngữ:** data quality (completeness, accuracy, uniqueness, timeliness, validity) · data profiling · deduplication · NULL · CTE · window function · rolling average

🗄️ **SQL:** CTE (`WITH`), `ROW_NUMBER()` để tìm trùng, `LAG()` để tìm giờ bị thiếu, `AVG() OVER (... ROWS BETWEEN 23 PRECEDING AND CURRENT ROW)`.
🐍 **Python:** tái sử dụng hàm extract cho nguồn mới (tránh copy-paste), `datetime` và múi giờ.

🛠️ **Xây dự án:**
- [ ] Hàm `fetch_air_quality()` gọi `https://air-quality-api.open-meteo.com/v1/air-quality` (hourly: `pm2_5, pm10, us_aqi, nitrogen_dioxide, ozone`).
- [ ] **Profiling:** thử lùi `start_date` để xem API cho dữ liệu lịch sử **xa nhất đến đâu**. Ghi kết quả vào README.
- [ ] Bảng `stg_air_quality_hourly` + load.
- [ ] `sql/dq_checks.sql`, viết tay các truy vấn: dòng trùng · giá trị NULL theo cột · PM2.5 âm hoặc > 1000 · **giờ bị thiếu** (LAG) · tỉnh nào thiếu dữ liệu.

✅ **Bắt buộc:** 2 nguồn dữ liệu trong DB + ít nhất 5 truy vấn kiểm tra chất lượng chạy được.
➕ **Mở rộng:** truy vấn PM2.5 trung bình trượt 24 giờ cho Hà Nội và TP.HCM.
🏆 **Chiến thắng:** biểu đồ PM2.5 Hà Nội vs TP.HCM (trung bình trượt 24h).
❓ **Tự kiểm tra:** (1) `ROW_NUMBER()` giúp loại trùng thế nào? (2) Cách phát hiện "giờ bị thiếu" bằng `LAG`? (3) Data profiling khác data quality check ở điểm nào?

---

### Ngày 5 · Thứ Bảy 21/11 · Pipeline v1: một lệnh chạy tất cả
🎯 Gom mọi thứ thành một pipeline có cấu trúc, chạy bằng một lệnh, có ghi log từng chặng vào DB.

📚 **Học:** ETL và ELT; vì sao chia module; cấu hình và bí mật (secrets); observability cơ bản.

🔤 **Thuật ngữ:** ETL · ELT · transform · modularity · configuration · secrets · run ID · observability · pipeline metadata

🐍 **Python:** package và import giữa các file, `argparse` (tham số dòng lệnh `--date`), `python-dotenv`, `dataclass` cho cấu hình, `uuid` cho run ID.

🛠️ **Xây dự án:**
- [ ] Tách code: `config.py` · `extract.py` · `transform.py` · `load.py` · `run_log.py`.
- [ ] Bảng `ops.pipeline_runs(run_id, stage, source, started_at, finished_at, rows_in, rows_out, status, error_message)`.
- [ ] `pipelines/run_pipeline.py --date 2026-11-21`: chạy extract → load staging cho **cả 2 nguồn**, mỗi chặng ghi 1 dòng vào `pipeline_runs`.

✅ **Bắt buộc:** `python pipelines/run_pipeline.py --date ...` chạy trọn vẹn, `pipeline_runs` có log của từng chặng.
➕ **Mở rộng:** khi một chặng lỗi, ghi `status='FAILED'` và nội dung lỗi rồi dừng gọn, không crash xấu.
🏆 **Chiến thắng:** truy vấn `pipeline_runs` thấy rõ từng chặng: vào bao nhiêu dòng, ra bao nhiêu dòng.
❓ **Tự kiểm tra:** (1) Pipeline của bạn là ETL hay ELT? Vì sao? (2) Nếu `rows_in` ≠ `rows_out` ở một chặng thì nghĩa là gì? (3) Vì sao mật khẩu phải nằm trong `.env`?

---

### Ngày 6 · Chủ Nhật 22/11 · Độ tin cậy + nạp dữ liệu lịch sử 3 năm
🎯 Pipeline chạy lại không bị trùng, tự thử lại khi API lỗi, và nạp được khoảng 1,5–2 triệu dòng lịch sử.

📚 **Học:** idempotency; upsert; nạp tăng dần (incremental) bằng watermark; retry với backoff; backfill; dữ liệu đến trễ.

🔤 **Thuật ngữ:** idempotency · upsert · incremental load · full load · watermark · retry · exponential backoff · timeout · backfill · late-arriving data

🗄️ **SQL:** `INSERT ... ON CONFLICT (location_id, ts_utc) DO UPDATE`, `MAX(ts_utc)` làm watermark.
🐍 **Python:** viết hàm retry (vòng lặp + `sleep` tăng dần), `requests` với `timeout`, chia khoảng thời gian thành từng đoạn.

🛠️ **Xây dự án:**
- [ ] Đổi insert thành **upsert**. Chạy pipeline 2 lần cho cùng một ngày và **chứng minh** số dòng không đổi.
- [ ] Thêm retry + timeout cho mọi lời gọi API.
- [ ] `pipelines/backfill.py --start 2023-01-01 --end ...`: dữ liệu thời tiết lấy từ `https://archive-api.open-meteo.com/v1/archive`, chia đoạn theo năm, nghỉ giữa các lần gọi. Dữ liệu không khí lùi xa đến mức API cho phép (theo kết quả profiling ngày 4).
- [ ] Ghi vào README: số dòng đã nạp, thời gian chạy.

✅ **Bắt buộc:** upsert + retry chạy đúng + dữ liệu lịch sử đã nạp vào DB.
➕ **Mở rộng:** nạp tăng dần, chỉ lấy dữ liệu sau watermark.
🏆 **Chiến thắng:** biểu đồ PM2.5 theo tháng trong 3 năm. Bạn sẽ thấy **mùa ô nhiễm** của Hà Nội hiện ra.
❓ **Tự kiểm tra:** (1) Giải thích idempotency bằng ví dụ trong dự án. (2) Vì sao retry cần backoff thay vì gọi lại ngay? (3) Backfill khác incremental load thế nào?

**🌙 Bản nhẹ (áp dụng 23/11, cơ thể lệch giờ):** giữ nguyên 3 đầu ra bắt buộc, giảm thao tác. Khoảng 1h30 làm thật, 3 khối, mỗi khối 25–30 phút, nghỉ 5 phút giữa các khối.
- **Khối 1 · Upsert:** chỉ điền 5 chỗ trống trong khung SQL. AI chuyển thành code động trong `load_rows` và chạy chứng minh.
- **Khối 2 · Retry:** tự viết vòng lặp retry rút gọn (~12 dòng). AI test bằng URL lỗi.
- **Khối 3 · Backfill:** chỉ tự viết `split_by_year` (khái niệm chunking). AI làm phần còn lại: profiling độ trễ archive, config, `backfill.py`, chạy nền, README, biểu đồ PM2.5.
- **Bỏ hôm nay:** watermark, bảng thuật ngữ dài, ALTER CHECK.
- **Điểm dừng an toàn:** xong Khối 1 + 2 là đạt ngày. Khối 3 có thể dời sang Ngày 7 (ngày nhẹ, dùng để bù trễ).

---

### Ngày 7 · Thứ Hai 23/11 · ✅ MỐC 1: củng cố (ngày nhẹ)
🎯 Chắc chắn những gì đã làm là **của mình**: tự viết lại được, có test, có README.

📚 **Học:** unit test là gì, vì sao data engineer cần test hàm biến đổi.

🔤 **Thuật ngữ:** unit test · assertion · test fixture · regression · technical debt · code review

🐍 **Python:** `pytest`, viết hàm thuần (pure function) để dễ test.

🛠️ **Xây dự án:**
- [ ] **Bài kiểm tra độc lập:** xóa (hoặc đóng lại) `transform.py`, **viết lại từ đầu không nhìn code cũ, không hỏi AI**. So sánh với bản cũ.
- [ ] Viết 5–8 test trong `tests/` cho các hàm transform và hàm kiểm tra tọa độ.
- [ ] README v1: mục tiêu dự án, sơ đồ kiến trúc (vẽ bằng Mermaid), cách chạy.
- [ ] **Bù phần còn trễ** từ ngày 1–6.

✅ **Bắt buộc:** `pytest` chạy xanh + README v1 + mọi phần "Bắt buộc" ngày 1–6 đã xong.
➕ **Mở rộng:** nhờ AI review code ở **cấp 1** (chỉ nêu vấn đề, không sửa hộ), rồi tự sửa.
🏆 **Chiến thắng:** pipeline hoàn chỉnh đầu tiên, có test, trên GitHub. Bạn đã có một sản phẩm thật.
❓ **Tự kiểm tra:** (1) Phần nào bạn viết lại thấy khó nhất? Ghi vào nhật ký để ôn. (2) Hàm thuần là gì, vì sao dễ test? (3) Kể lại toàn bộ luồng dữ liệu của dự án trong 1 phút.

---

### TUẦN 2: NÂNG CẤP THÀNH HỆ THỐNG CHUẨN NGHỀ

---

### Ngày 8 · Thứ Ba 24/11 · Mô hình hóa dữ liệu: star schema
🎯 Xây tầng Mart phục vụ phân tích.

📚 **Học:** chuẩn hóa và phi chuẩn hóa; star schema; bảng fact và dimension; grain; khóa thay thế; SCD loại 1 và 2. Ví dụ thực tế: **63 tỉnh sáp nhập thành 34**, dữ liệu cũ gắn với tỉnh cũ thì xử lý thế nào?

🔤 **Thuật ngữ:** data modeling · normalization · star schema · fact table · dimension table · grain · surrogate key · natural key · SCD Type 1/2 · data mart · data warehouse

🗄️ **SQL:** `CREATE TABLE ... AS SELECT`, `INSERT ... SELECT` từ staging sang mart, JOIN fact với dimension, `EXTRACT(hour/month FROM ...)`.

🛠️ **Xây dự án:**
- [ ] `sql/02_mart.sql`: `dim_location`, `dim_date`, `fact_weather_hourly`, `fact_air_quality_hourly`. Ghi rõ **grain** của mỗi bảng fact trong comment.
- [ ] Thêm chặng `build_mart` vào pipeline (ghi log vào `pipeline_runs`).
- [ ] Viết truy vấn phân tích trên mart: PM2.5 trung bình theo **giờ × tháng** cho Hà Nội.

✅ **Bắt buộc:** 4 bảng mart có dữ liệu + chặng `build_mart` nằm trong pipeline.
➕ **Mở rộng:** `dim_location` dạng SCD2 với `valid_from/valid_to`, ví dụ tỉnh trước và sau 01/7/2025.
🏆 **Chiến thắng:** **heatmap giờ × tháng** của PM2.5 Hà Nội. Câu hỏi dữ liệu số 1 đã có lời giải.
❓ **Tự kiểm tra:** (1) Grain của `fact_air_quality_hourly` là gì? (2) Khi nào dùng SCD1, khi nào dùng SCD2? (3) Vì sao tầng mart nên tách khỏi staging?

---

### Ngày 9 · Thứ Tư 25/11 · Định dạng lưu trữ và dữ liệu lớn
🎯 Hiểu vì sao hệ thống dữ liệu lớn dùng Parquet và phân vùng, và tự đo được sự khác biệt.

📚 **Học:** lưu theo dòng và lưu theo cột; Parquet; nén; phân vùng; data lake, lakehouse; Spark, HDFS/object storage, Kafka (ở mức **giải quyết vấn đề gì**).

🔤 **Thuật ngữ:** row-oriented vs columnar · Parquet · compression · partitioning · partition pruning · predicate pushdown · data lakehouse · distributed processing · Spark · HDFS / object storage · streaming · Kafka · message queue

🐍 **Python:** `pandas.to_parquet` có `partition_cols`, `pyarrow`, `duckdb`, đo thời gian bằng `time.perf_counter()`.

🛠️ **Xây dự án:**
- [ ] Xuất dữ liệu lịch sử thành **CSV** và **Parquet phân vùng** `data/lake/air_quality/year=…/month=…/`.
- [ ] **Benchmark:** so sánh dung lượng, thời gian đọc toàn bộ, thời gian truy vấn 1 tháng của 1 tỉnh. Ghi bảng kết quả vào README.
- [ ] Dùng **DuckDB** chạy SQL trực tiếp trên file Parquet.

✅ **Bắt buộc:** bảng benchmark CSV vs Parquet với số liệu thật của bạn.
➕ **Mở rộng:** PySpark chạy local (cần cài Java) làm cùng một phép tổng hợp. Hoặc đọc khái niệm Kafka và vẽ sơ đồ: nếu dữ liệu đến theo thời gian thực thì kiến trúc VietSky thay đổi thế nào.
🏆 **Chiến thắng:** con số "Parquet nhỏ hơn X lần, nhanh hơn Y lần" do chính bạn đo.
❓ **Tự kiểm tra:** (1) Vì sao định dạng cột nhanh hơn với truy vấn phân tích? (2) Partition pruning hoạt động thế nào với `year=/month=`? (3) Khi nào cần Spark thay vì pandas?

---

### Ngày 10 · Thứ Năm 26/11 · Hệ thống kiểm tra chất lượng tự động + đối soát
🎯 Biến các truy vấn kiểm tra ở ngày 4 thành **hệ thống tự chạy sau mỗi lần pipeline chạy**.

📚 **Học:** quy tắc chất lượng dữ liệu; data contract; schema drift; freshness; đối soát; SLA; cảnh báo.

🔤 **Thuật ngữ:** data quality rule · data contract · schema validation · schema drift · freshness · completeness check · reconciliation · anomaly · threshold · SLA · alerting

🐍 **Python:** danh sách quy tắc dạng `list[dict]`, mỗi quy tắc là một câu SQL + ngưỡng; hàm chạy quy tắc trả kết quả đạt/không đạt.

🛠️ **Xây dự án:**
- [ ] `src/vietsky/quality.py` + bảng `ops.dq_results(run_id, check_name, table_name, status, failed_rows, checked_at)`.
- [ ] Tối thiểu 6 quy tắc: không NULL ở cột khóa · không trùng · PM2.5 trong khoảng hợp lệ · đủ 34 tỉnh · **độ mới** (dữ liệu mới nhất không cũ quá N giờ) · **schema** (đủ cột mong đợi trong JSON raw).
- [ ] **Đối soát:** số dòng raw = staging = mart (theo từng ngày, từng nguồn).
- [ ] Thêm chặng `quality_check` vào pipeline. Lỗi nghiêm trọng thì đánh dấu run `FAILED`.

✅ **Bắt buộc:** 6 quy tắc + đối soát chạy tự động, kết quả lưu vào `dq_results`.
➕ **Mở rộng:** phân mức `WARNING`/`CRITICAL`; in một bản tóm tắt cảnh báo ra log.
🏆 **Chiến thắng:** pipeline tự nói được "hôm nay dữ liệu có ổn không". Đây chính là công việc của bạn sắp tới.
❓ **Tự kiểm tra:** (1) Schema drift là gì, phát hiện ở chặng nào? (2) Đối soát số dòng giúp khoanh vùng lỗi ra sao? (3) Freshness khác completeness thế nào?

---

### Ngày 11 · Thứ Sáu 27/11 · Điều phối bằng Airflow
🎯 Pipeline chạy theo lịch, có phụ thuộc giữa các bước, tự thử lại khi lỗi, xem được trên giao diện.

📚 **Học:** orchestration; DAG; task và phụ thuộc; scheduler; retry; catchup/backfill trong Airflow; vì sao task phải idempotent.

🔤 **Thuật ngữ:** orchestration · DAG · task · dependency · scheduler · executor · retry · catchup · backfill · sensor · cron expression

🐍 **Python:** viết DAG bằng TaskFlow API (`@dag`, `@task`), gọi lại các hàm có sẵn trong `src/vietsky`.

🛠️ **Xây dự án:**
- [ ] Chạy Airflow bằng file Docker Compose chính thức (16GB RAM là đủ; nhớ cấp cho Docker ít nhất 4–6GB).
- [ ] `dags/vietsky_daily.py`: `extract_weather` & `extract_air_quality` (song song) → `load_staging` → `quality_check` → `build_mart`. Lịch chạy hằng ngày, `retries=2`.
- [ ] Chạy thử, chụp màn hình DAG xanh cho README.

✅ **Bắt buộc:** DAG chạy thành công ít nhất 1 lần trên giao diện Airflow.
⛑️ **Phương án dự phòng:** nếu cài Airflow mất quá 90 phút, chuyển sang dùng `cron` để chạy `run_pipeline.py` hằng ngày, và **vẽ sơ đồ DAG** trên giấy/Mermaid để vẫn nắm khái niệm. Không được để Airflow làm hỏng cả ngày.
➕ **Mở rộng:** thử `catchup` để Airflow tự chạy bù 3 ngày gần nhất.
🏆 **Chiến thắng:** ảnh chụp DAG màu xanh trên giao diện Airflow.
❓ **Tự kiểm tra:** (1) Vì sao 2 task extract chạy song song được còn `load_staging` thì không? (2) Task không idempotent thì retry gây hậu quả gì? (3) Catchup là gì?

---

### Ngày 12 · Thứ Bảy 28/11 · Dashboard 2 trang + kiến thức bản đồ
🎯 Dashboard đầy màu sắc: một trang phân tích, một trang vận hành.

📚 **Học:** serving layer; KPI và metric; hệ tọa độ WGS84 (EPSG:4326), biết thêm **VN-2000** là hệ tọa độ quốc gia của Việt Nam; GeoJSON; bản đồ điểm và bản đồ vùng (choropleth); công thức haversine.

🔤 **Thuật ngữ:** serving layer · BI · KPI / metric · data freshness indicator · CRS · WGS84 · VN-2000 · GeoJSON · choropleth · haversine

🐍 **Python:** `streamlit` (trang, bộ lọc, cache), `plotly.express` (`scatter_map`, `line`, `density_heatmap`, `scatter`).

🛠️ **Xây dự án:** `dashboard/app.py`
- [ ] **🌏 Trang "Bầu trời Việt Nam":** bản đồ 34 tỉnh tô màu theo PM2.5 · xu hướng nhiều năm (chọn tỉnh) · heatmap giờ × tháng · biểu đồ phân tán **lượng mưa vs PM2.5** và **gió vs PM2.5** · bảng xếp hạng tỉnh sạch/ô nhiễm.
- [ ] **🛠️ Trang "Phòng điều hành":** các lần chạy gần nhất (trạng thái, thời lượng) · **số dòng qua từng chặng** (biểu đồ phễu) · tỷ lệ đạt các bài kiểm tra chất lượng theo ngày · độ mới của từng nguồn.

✅ **Bắt buộc:** 2 trang chạy được, mỗi trang tối thiểu 3 biểu đồ.
➕ **Mở rộng:** hàm haversine tìm "tỉnh lân cận trong bán kính 150km" và so sánh PM2.5 giữa các tỉnh lân cận. Ô nhiễm có "lan" sang nhau không?
🏆 **Chiến thắng:** ảnh chụp dashboard cho README và CV. Câu hỏi dữ liệu số 2, 3, 4 đã có lời giải.
❓ **Tự kiểm tra:** (1) Vì sao trang "Phòng điều hành" quan trọng với vị trí Data Operations? (2) Lat/lon bị đảo thì trên bản đồ sẽ thấy gì? (3) WGS84 và VN-2000 khác nhau ở điểm nào?

---

### Ngày 13 · Chủ Nhật 29/11 · Diễn tập sự cố, kỹ năng lõi của công việc
🎯 Tự gây lỗi, tự truy ra nguyên nhân, viết báo cáo sự cố như một kỹ sư vận hành thật.

📚 **Học:** monitoring và observability; quy trình xử lý sự cố; phân tích nguyên nhân gốc (5 Whys); postmortem không đổ lỗi; runbook.

🔤 **Thuật ngữ:** incident · monitoring · observability · alert · root cause analysis (RCA) · 5 Whys · postmortem (blameless) · runbook · MTTD / MTTR · chaos testing

🐍 **Python:** `chaos.py` bật/tắt từng loại lỗi bằng biến môi trường hoặc tham số dòng lệnh.

🛠️ **Xây dự án:** `src/vietsky/chaos.py` gây 6 lỗi, mỗi lỗi chạy pipeline rồi **phát hiện bằng dashboard, log và SQL**:

| # | Lỗi cố tình gây ra | Chặng | Phát hiện bằng |
|---|---|---|---|
| 1 | API timeout / trả về 500 | Extract | retry log, run `FAILED` |
| 2 | Đổi tên một trường trong JSON (`pm2_5` → `pm25`) | Extract → Load | kiểm tra schema |
| 3 | Chạy pipeline 2 lần, tắt upsert | Load | kiểm tra trùng, đối soát |
| 4 | **Đảo lat/lon** của 3 tỉnh | Dữ liệu tham chiếu | kiểm tra tọa độ, bản đồ |
| 5 | Ghi thời gian theo giờ địa phương nhưng gắn nhãn UTC (lệch 7 tiếng) | Transform | heatmap giờ bất thường, freshness |
| 6 | Một tỉnh trả về toàn NULL | Extract | completeness, đủ 34 tỉnh |

- [ ] Với mỗi lỗi, viết `docs/incidents/0X-ten-loi.md` theo mẫu: **Triệu chứng → Phát hiện lúc nào, bằng gì → Khoanh vùng (chặng nào) → Nguyên nhân gốc (5 Whys) → Cách sửa → Cách phòng tránh**.
- [ ] Viết `docs/runbook.md`: **"Pipeline lỗi thì kiểm tra theo thứ tự nào"**.
  > Dữ liệu có đến không? → Đến đủ không? → Đúng cấu trúc không? → Xử lý đúng không? → Ghi vào đích đủ không? → Đúng giờ không?

✅ **Bắt buộc:** tối thiểu 4/6 lỗi có báo cáo sự cố + runbook.
➕ **Mở rộng:** đủ 6/6. Thêm các lỗi thật bạn đã gặp trong 12 ngày qua (lấy từ nhật ký).
🏆 **Chiến thắng:** thư mục `incidents/`. Hầu như không dự án fresher nào có phần này.
❓ **Tự kiểm tra:** (1) Lỗi nào khó phát hiện nhất, vì sao? (2) Kể lại 1 sự cố theo đúng cấu trúc postmortem trong 2 phút. (3) Hệ thống kiểm tra nào của bạn bắt được nhiều lỗi nhất?

---

### Ngày 14 · Thứ Hai 30/11 · ✅ MỐC 2: hoàn thiện và sẵn sàng (ngày nhẹ)
🎯 Dự án hoàn chỉnh, trình bày được, và bạn sẵn sàng cho ngày 01/12.

🛠️ **Việc cần làm:**
- [ ] **README hoàn chỉnh:** giới thiệu (2–3 câu) · sơ đồ kiến trúc · ảnh dashboard · cách chạy · bảng benchmark · tóm tắt các bài kiểm tra chất lượng · link tới `incidents/` · **bài học rút ra** · ghi chú nguồn dữ liệu (Open-Meteo, CC BY 4.0).
- [ ] Kiểm tra repo không có `.env`, mật khẩu hay dữ liệu raw lớn.
- [ ] **Thêm vào CV** (thay số thật của bạn):
  - *Xây dựng pipeline dữ liệu thời tiết và chất lượng không khí cho 34 tỉnh thành Việt Nam, xử lý ~[X] triệu bản ghi theo giờ; điều phối bằng Airflow, lưu trữ PostgreSQL theo mô hình star schema.*
  - *Thiết kế [N] quy tắc kiểm tra chất lượng dữ liệu và cơ chế đối soát giữa các tầng; pipeline idempotent, có retry và log theo từng chặng.*
  - *Diễn tập [N] kịch bản sự cố, viết postmortem và runbook; xây dashboard vận hành theo dõi độ mới dữ liệu và tỷ lệ đạt kiểm tra.*
- [ ] **Tự kiểm tra cuối:** đọc mục 5 (Bản đồ thuật ngữ), mỗi thuật ngữ tự nói được nghĩa, vai trò và giai đoạn. Đánh dấu những thuật ngữ còn mơ hồ.
- [ ] Chuẩn bị giấy tờ đi làm (CCCD, bản sao công chứng bằng tốt nghiệp, ảnh thẻ, sổ BHXH nếu có). Nghỉ ngơi sớm.

🏆 **Chiến thắng:** một dự án cá nhân hoàn chỉnh trên GitHub, và bạn kể được trọn vẹn câu chuyện kỹ thuật của nó.

---

## 5. Bản đồ thuật ngữ theo giai đoạn pipeline

> Mục tiêu: nghe thuật ngữ nào cũng trả lời được **nó là gì · vai trò · thuộc giai đoạn nào**. Cột "Ngày" là ngày bạn gặp nó trong dự án.

| Giai đoạn | Thuật ngữ | Nghĩa ngắn | Ngày |
|---|---|---|---|
| **Nguồn & Thu thập** | Data source | Nơi sinh ra dữ liệu (API, DB, file, cảm biến) | 1 |
| | Ingestion | Đưa dữ liệu từ nguồn vào hệ thống | 1 |
| | Batch vs Streaming | Xử lý theo lô định kỳ vs xử lý liên tục từng sự kiện | 1, 9 |
| | Full / Incremental load | Nạp toàn bộ vs chỉ nạp phần mới | 6 |
| | Watermark | Mốc đánh dấu đã nạp đến đâu | 6 |
| | Backfill | Chạy bù/nạp lại dữ liệu cho khoảng thời gian quá khứ | 6, 11 |
| | Late-arriving data | Dữ liệu đến trễ so với thời điểm nó xảy ra | 6 |
| | Rate limit | Giới hạn số lời gọi API trong một khoảng thời gian | 2 |
| | Retry / Exponential backoff | Thử lại khi lỗi, khoảng chờ tăng dần | 6 |
| | Message queue / Kafka | Hàng đợi trung gian cho dữ liệu dòng | 9 |
| **Lưu trữ** | Landing / Raw layer | Nơi giữ dữ liệu nguyên bản, chưa xử lý | 1 |
| | Data lake | Kho lưu file thô nhiều định dạng, chi phí rẻ | 1, 9 |
| | Data warehouse | Kho dữ liệu có cấu trúc, tối ưu cho phân tích | 8 |
| | Data lakehouse | Kết hợp lake (file rẻ) + warehouse (quản lý bảng, giao dịch) | 9 |
| | Staging layer | Tầng trung gian: dữ liệu đã làm sạch sơ bộ | 3 |
| | Data mart | Tầng dữ liệu phục vụ một mục đích phân tích cụ thể | 8 |
| | OLTP vs OLAP | Hệ giao dịch (ghi nhiều) vs hệ phân tích (đọc, tổng hợp nhiều) | 3 |
| | Parquet / Columnar | Định dạng lưu theo cột, nén tốt, đọc nhanh khi phân tích | 9 |
| | Partitioning | Chia dữ liệu theo khóa (ngày, tháng) để đọc ít hơn | 9 |
| | HDFS / Object storage | Hệ lưu trữ phân tán cho dữ liệu lớn | 9 |
| **Xử lý & Mô hình** | ETL vs ELT | Biến đổi trước khi nạp vs nạp rồi biến đổi trong kho | 5 |
| | Transform | Làm sạch, chuẩn hóa, gộp, tính toán | 3, 5 |
| | Idempotency | Chạy lại nhiều lần cho cùng kết quả | 6 |
| | Upsert | Có thì cập nhật, chưa có thì thêm | 6 |
| | Deduplication | Loại bỏ bản ghi trùng | 4 |
| | Star schema | Mô hình 1 bảng fact ở giữa, các bảng dimension xung quanh | 8 |
| | Fact / Dimension | Bảng sự kiện, số đo vs bảng mô tả ngữ cảnh | 8 |
| | Grain | Mỗi dòng của bảng fact đại diện cho cái gì | 8 |
| | Surrogate / Natural key | Khóa do hệ thống tự sinh vs khóa có nghĩa nghiệp vụ | 8 |
| | SCD Type 1/2 | Ghi đè thay đổi vs giữ lịch sử thay đổi của dimension | 8 |
| | Distributed processing / Spark | Xử lý song song trên nhiều máy | 9 |
| **Điều phối** | Orchestration | Điều khiển thứ tự, lịch chạy, phụ thuộc giữa các bước | 11 |
| | DAG | Đồ thị có hướng không chu trình mô tả các task | 11 |
| | Scheduler / Cron | Bộ lập lịch / cú pháp lịch chạy | 6, 11 |
| | Catchup | Airflow tự chạy bù các lần lỡ lịch | 11 |
| **Chất lượng dữ liệu** | Data profiling | Khảo sát đặc điểm dữ liệu (phân bố, NULL, khoảng giá trị) | 4 |
| | DQ dimensions | Đầy đủ, chính xác, duy nhất, kịp thời, hợp lệ | 4 |
| | Data validation | Kiểm tra dữ liệu theo quy tắc | 2, 10 |
| | Schema drift | Cấu trúc dữ liệu nguồn thay đổi ngoài ý muốn | 10, 13 |
| | Data contract | Thỏa thuận về cấu trúc và chất lượng giữa bên gửi và bên nhận | 10 |
| | Freshness | Dữ liệu mới nhất cách hiện tại bao lâu | 10 |
| | Reconciliation | Đối soát số liệu giữa các tầng hoặc giữa nguồn và đích | 10 |
| | Data lineage | Dữ liệu đến từ đâu, đi qua những bước nào | 1, 14 |
| **Phục vụ** | Serving layer | Tầng cung cấp dữ liệu cho người dùng hoặc ứng dụng | 12 |
| | BI / Dashboard | Trực quan hóa phục vụ ra quyết định | 12 |
| | KPI / Metric | Chỉ số đo lường | 12 |
| **Vận hành (DataOps)** | Observability | Khả năng hiểu trạng thái hệ thống qua log, metric, trace | 5, 13 |
| | Monitoring / Alerting | Theo dõi liên tục / cảnh báo khi vượt ngưỡng | 10, 13 |
| | SLA | Cam kết mức dịch vụ (ví dụ dữ liệu có trước 7h sáng) | 10 |
| | Incident / RCA | Sự cố / phân tích nguyên nhân gốc | 13 |
| | Postmortem | Báo cáo sau sự cố, không đổ lỗi, tập trung phòng tránh | 13 |
| | Runbook | Tài liệu hướng dẫn xử lý khi có sự cố | 13 |
| | MTTD / MTTR | Thời gian trung bình để phát hiện / khắc phục sự cố | 13 |
| **Không gian (GIS)** | CRS / WGS84 / VN-2000 | Hệ tọa độ; chuẩn GPS toàn cầu; chuẩn quốc gia Việt Nam | 12 |
| | GeoJSON | Định dạng JSON cho dữ liệu không gian | 12 |
| | Haversine | Công thức tính khoảng cách giữa 2 điểm trên mặt cầu | 12 |
| **Bảo mật** | Secrets management | Quản lý mật khẩu, khóa ngoài code | 5 |
| | Least privilege | Chỉ cấp quyền tối thiểu cần thiết | 14 |

---

## 6. Tài liệu tham khảo
- **Open-Meteo docs:** open-meteo.com/en/docs (Forecast, Historical/Archive, Air Quality, Geocoding)
- **SQL:** pgexercises.com · tài liệu PostgreSQL chính thức
- **Terminal:** MIT "The Missing Semester", bài Shell
- **Data Engineering tổng quan:** DataTalksClub Data Engineering Zoomcamp, chỉ dùng Module 1 (Docker + Postgres + ingestion) để tham khảo
- **Airflow:** tài liệu chính thức, phần "Running Airflow in Docker" và "TaskFlow tutorial"
- **Streamlit + Plotly:** docs.streamlit.io · plotly.com/python

---

## 7. Nhật ký tiến độ

> Cập nhật lúc 11:45 mỗi ngày. Copy khung dưới cho từng ngày.

```
### Ngày N – dd/mm
- Trạng thái: ✅ Xong Bắt buộc / ⚠️ Một phần / ❌ Chưa
- Đã làm:
- Khái niệm hiểu rõ:
- Khái niệm còn mơ hồ:
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
- Chiến thắng hôm nay:
- TODO cho mai (bước đầu tiên cụ thể):
- Mức tự viết (không AI) hôm nay: __ / 10
```

### Ngày 1 – 17/11
- Trạng thái: ✅ Xong Bắt buộc
- Đã làm: setup repo + venv + `.gitignore`, push GitHub; `extract.py` (`fetch_weather`, `save_raw`) lấy 168 dòng thời tiết HCM 01–07/11 → `data/raw/weather/date=2026-11-17/hcm.json`; `plot_raw.py` vẽ nhiệt độ bằng Plotly. Đổi thành phố mẫu từ Hà Nội sang HCM.
- Khái niệm hiểu rõ: raw layer lưu nguyên bản (lineage, reprocess); 3 chặng Extract → Landing → Visualization; partition theo ngày chạy; `params=` + `timeout`; kiểm tra 3 tầng (mạng → HTTP → nội dung).
- Khái niệm còn mơ hồ: xử lý 429/500 (đã trả lời sai "thử lại ngay"); tham số hàm nhận giá trị lúc gọi; truy cập dict JSON lồng nhau. Câu hỏi mở: chạy nhiều lần/ngày thì partition thế nào (→ run_id, ngày 5–6, 11).
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
  - 400 Bad Request → 4xx = lỗi phía mình → soi URL → `start_date=2026-011-01` sai định dạng → sửa `YYYY-MM-DD`.
  - `BASE_URL` chứa sẵn query, `hourly` là dict → in `response.url` thấy tham số trùng/sai → URL chỉ còn endpoint, `hourly` là chuỗi 4 biến.
  - `px.line` báo thiếu thư viện → cài `pandas numpy`.
  - Đường dẫn raw sai ngày (`date=2026-11-07`) → so với path `extract.py` in ra → dùng `RUN_DATE`.
- Chiến thắng hôm nay: biểu đồ nhiệt độ HCM 7 ngày (`docs/screenshots/day01_temp_hcm.png`), đỉnh nóng buổi trưa → đúng múi giờ.
- TODO cho mai: dán URL Geocoding `name=Hà Nội&country_code=VN` vào trình duyệt, xem JSON trả về những trường nào.
- Mức tự viết (không AI) hôm nay: __ / 10 (dùng cấp 3 cho `plot_temperature`)

### Ngày 2 – 18/11
- Trạng thái: ✅ Xong Bắt buộc (chưa làm bước 4 terminal)
- Đã làm: `geocode.py` lấy tọa độ trung tâm hành chính 34 tỉnh → `config/provinces.csv` (28 tự động, 6 sửa tay có `note`); `validate.py` kiểm tra số dòng / trùng tên / tọa độ trong khung VN, đã thử làm hỏng file 4 kiểu; `fetch_all.py` lấy thời tiết 34 tỉnh (192 dòng/tỉnh) → `data/raw/weather/date=2026-11-18/<province_code>.json`, log ra `logs/fetch_all.log`: 34 OK, 0 lỗi.
- Khái niệm hiểu rõ: reference data sai = lỗi im lặng (nguy hiểm hơn 500); 3 chiều chất lượng: completeness, uniqueness, validity; validate trước extract sau; feature_code PPLC/PPLA/PPL.
- Khái niệm còn mơ hồ: `try/except` trong vòng `for` (cô lập lỗi) và `sys.exit(1)` (mã thoát cho công cụ điều phối), phải nhờ giải thích; ADM1 (cả vùng) khác trường `admin1` (tên tỉnh chứa điểm).
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
  - Geocoding trả địa điểm nước ngoài → nhìn dữ liệu trả về → tham số đúng là `countryCode`, không phải `country_code` (API lặng lẽ bỏ qua tham số sai).
  - 17 tỉnh `not found`, vài tỉnh "tìm thấy" nhưng sai (Lào Cai, Bắc Ninh, Tây Ninh lấy TP cũ) → do tìm theo tên tỉnh → thêm cột `search_name` theo trung tâm hành chính sau sáp nhập 01/7/2025.
  - 6 tỉnh vẫn thiếu do GeoNames hạ Yên Bái/Bắc Giang/Đồng Hới xuống `PPLA2` → sửa tay, ghi `note`.
  - `validate.py` luôn báo đạt: `continue` sai thụt lề, kiểm tra tọa độ nằm ngoài vòng lặp, `if errors` đảo ngược → phát hiện khi cố tình đổi `lat=40`.
  - Hai lần chạy `fetch_all.py` cùng lúc ghi đè cùng 34 file → ví dụ thật cho câu hỏi partition nhiều lần/ngày (`run_id`).
- Chiến thắng hôm nay: 34 file JSON + log `Hoàn tất: 34 OK, 0 lỗi`.
- TODO cho mai: tạo `docker-compose.yml` chạy `postgres:16` (mật khẩu đặt trong file biến môi trường), `docker compose up -d`, kết nối thử bằng DBeaver.
- Mức tự viết (không AI) hôm nay: __ / 10 (AI sửa hộ một phần `geocode.py` và viết lại `fetch_all.py`)

### Ngày 3 – 19/11
- Trạng thái: ✅ Xong Bắt buộc
- Đã làm: `docker-compose.yml` chạy `postgres:16` (cổng 5433, named volume `pgdata`, cấu hình trong file biến môi trường); `sql/01_staging.sql` tạo `dim_location` + `stg_weather_hourly` (PK `(location_id, ts_utc)`, FK, `CHECK`); `load.py` chuyển JSON cột → dòng, nạp 34 tỉnh + 6528 dòng, chạy lại 2 lần vẫn 6528 (idempotent); `sql/explore.sql` 15 truy vấn chạy được cả 15.
- Khái niệm hiểu rõ: staging layer; PK ghép ngăn trùng + `ON CONFLICT` giúp chạy lại = idempotent; transaction rollback cả khối; volume giữ dữ liệu ngoài container; bí mật tách khỏi code; tham số `%s` chống SQL injection.
- Khái niệm còn mơ hồ: lúc đầu chưa rõ vai trò volume và lý do tách bí mật; upsert (`DO UPDATE`) cho bảng chiều (ngày 8).
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
  - Cổng 5432 đã bị Postgres Homebrew chiếm → đổi sang `5433:5432` (tránh kết nối nhầm database).
  - Giờ API là giờ địa phương không kèm múi giờ → gắn offset từ `utc_offset_seconds` → kiểm tra dòng đầu `2026-11-10 17:00+00` = 00:00 VN.
  - Khai báo volume cuối file đổi tên (`vietsky:`) không khớp `pgdata` → compose báo `undefined volume` → trả lại `pgdata:`.
- Chiến thắng hôm nay: Top 5 tỉnh nóng nhất 18/11 từ database của mình: Hồ Chí Minh 33.9°C, An Giang 33.7, Đồng Nai 32.9, Vĩnh Long 32.4, Tây Ninh 32.0.
- TODO cho mai: mở tài liệu Open-Meteo Air Quality API, gọi thử 1 URL cho HCM với `pm2_5,pm10`, xem JSON có giống dạng thời tiết không.
- Mức tự viết (không AI) hôm nay: __ / 10 (tự viết SQL DDL, `load.py`, 15 truy vấn; AI chỉ sửa nhỏ)

### Ngày 4 – 20/11
- Trạng thái: ✅ Xong Bắt buộc (chưa làm Mở rộng: rolling 24h + biểu đồ)
- Đã làm: tổng quát hóa `extract.py` (`fetch_hourly` + 2 hàm 1 dòng, `save_raw` theo `source`); `fetch_all.py` lấy cả thời tiết + bụi mịn 34 tỉnh (34 OK); profiling 2 API ghi vào `README.md`; bảng `stg_air_quality_hourly`; `load.py` config-driven (`SOURCES`, `sql.Identifier`) nạp 6528 + 6528 dòng, idempotent; `sql/dq_checks.sql` 5 check, cả 5 đạt (0 dòng).
- Khái niệm hiểu rõ: profiling ≠ quality check; API "cho hỏi" ≠ API "có dữ liệu" (PM2.5 thật từ 2022-08-04, `/forecast` chỉ ~3 tháng, cửa sổ trượt) → raw là nguồn lịch sử duy nhất; config-driven; NULL không so sánh bằng `=`; `WHERE` trước gộp, `HAVING` sau gộp.
- Khái niệm còn mơ hồ: viết điều kiện check bị **ngược** (lấy dòng tốt thay vì dòng lỗi) ở DQ1, DQ3, DQ4; chọn `PARTITION BY` / `ORDER BY` cho hàm cửa sổ; `INNER` vs `LEFT JOIN` khi đối soát.
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
  - `fetch_all.py` chỉ gắn `source="weather"`, chưa gọi API bụi mịn → đếm file `air_quality/` chỉ có 1 → thêm gọi 2 nguồn, all-or-nothing theo tỉnh.
  - File `hcm.json` từ lần chạy thử lẫn vào partition thật → sẽ vỡ khóa ngoại khi load → xóa; chạy thử không ghi chung thư mục pipeline.
  - `docker-compose.yml` đổi khai báo volume không khớp → `undefined volume` (sửa ở Ngày 3).
  - Chạy lại DDL `DROP` mất dữ liệu 18/11 trong DB → raw còn → cần backfill (ngày 5–6).
  - DQ5 dùng `INNER JOIN` → giả lập xóa Lai Châu trong transaction rồi rollback: `INNER` trả 0 dòng (bỏ sót), `LEFT` bắt được → đổi sang `LEFT JOIN`.
- Chiến thắng hôm nay: 2 nguồn dữ liệu trong DB + bộ 5 check chất lượng phủ uniqueness / completeness / validity.
- TODO cho mai: liệt kê các bước đang chạy tay (fetch_all → DDL → load → dq_checks) và ghi ra giấy thứ tự + điều kiện dừng giữa các bước, làm đầu vào cho pipeline v1.
- Mức tự viết (không AI) hôm nay: __ / 10 (tự viết `load.py` config-driven, DDL, 5 check theo khung; AI sửa `fetch_all.py` và điều kiện check)

### Ngày 5 – 21/11
- Trạng thái: ✅ Xong Bắt buộc (chưa làm Mở rộng: thử chủ động nhánh FAILED)
- Đã làm: `sql/00_ops.sql` (schema `ops`, bảng `pipeline_runs`, không `DROP`, idempotent); tách module `config.py` (dataclass `Source`, `api_variables` sinh từ ánh xạ cột) · `transform.py` · `load.py` (trả `rowcount`) · `run_log.py` (`start_stage`/`finish_stage`); `pipelines/run_pipeline.py --date` chạy extract → load cho 2 nguồn, mỗi chặng 1 dòng log. Chạy lần 1: 4 chặng SUCCESS, 6528 + 6528 dòng; chạy lại: load `rows_out = 0` (idempotent đo được).
- Khái niệm hiểu rõ: ETL vs ELT (Python chỉ đổi hình dạng, nghiệp vụ để SQL); modularity + orchestrator; config công khai (`config.py`) vs secrets (file biến môi trường); run ID; vòng đời RUNNING → SUCCESS/FAILED; `rows_in` vs `rows_out` để đối soát; log commit riêng, không bị rollback cùng dữ liệu.
- Khái niệm còn mơ hồ: import theo package (`from vietsky.x`, `PYTHONPATH=src`); type hint trả về (`-> tuple[int, int]` là kiểu, không phải tên biến); truyền tuple giá trị cho `%s`; log nằm trong bảng DB chứ không phải `print`.
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
  - Bảng staging biến mất (`relation does not exist`) → `\dt` chỉ còn `ops.pipeline_runs`, volume tạo lại lúc 11:47 (nghi `down -v`) → chạy lại `01_staging.sql`, pipeline dựng lại DB từ API/raw.
  - `config.py`: URL lấy từ biến môi trường không tồn tại → `None` im lặng; key `localhost` thay vì `host`; thiếu `api_variables` → sửa.
  - `ModuleNotFoundError: config` → import theo package `vietsky.config`.
  - `run_log.py` không truyền tuple giá trị cho `%s`, thiếu `run_date`/`status`, sai tên hàm → sửa, thử 1 run giả.
  - `run_pipeline.py`: `date - int`, `"SUCESS"` (bị `CHECK` chặn), truyền object `Source` vào SQL, `sys.exit` thụt lề trong vòng `for` (nguồn 2 không chạy) → sửa.
  - Bảng log lộ ra 2 lần chạy song song (run_id xen kẽ) → cần chặn chạy trùng (lock / `max_active_runs`, ngày 11).
- Chiến thắng hôm nay: `SELECT * FROM ops.pipeline_runs` thấy đủ 4 chặng/lần chạy, extract chiếm ~99% thời gian, lần chạy lại load 6528 → 0.
- TODO cho mai: đổi `load_rows` sang `ON CONFLICT ... DO UPDATE` (upsert) để bản dự báo mới ghi đè bản cũ, chạy lại 2 lần và so `pipeline_runs`.
- Mức tự viết (không AI) hôm nay: __ / 10 (tự viết theo pseudocode cả 5 file; AI sửa lỗi import, tham số SQL, thụt lề)

### Ngày 6 – 23/11 (bản nhẹ, cơ thể lệch giờ)
- Trạng thái: ✅ Xong Bắt buộc theo bản nhẹ (chưa làm Mở rộng: watermark / incremental)
- Đã làm: `load_rows` đổi sang upsert (`DO UPDATE SET ... = EXCLUDED.*, loaded_at = now()`), chạy lại ngày 21/11 → `COUNT(*)` giữ 6528/6528; `fetch_hourly` có retry 4 lần, backoff 2/4/8s, chỉ thử lại 429/5xx + lỗi mạng (test 4 kịch bản đạt); `config.py` thêm `history_url`/`history_start`; `run_stage` chuyển sang `run_log.py`; `pipelines/backfill.py` (chia đoạn theo năm, commit sau mỗi tỉnh-năm). Backfill 04/08/2022 → 23/11/2026: 1.283.568 dòng mỗi nguồn, 397s + 475s, 0 retry, 0 khe hở giờ.
- Khái niệm hiểu rõ: idempotency đo bằng `COUNT(*)` (không còn bằng `rows_out` khi dùng upsert); lỗi tạm thời (thử lại) vs lỗi do mình (ném ngay); chunking + checkpoint giúp chạy lại an toàn; kẹp ngày bắt đầu theo giới hạn nguồn (`max(start, history_start)`).
- Khái niệm còn mơ hồ: `raise` trong `try` làm thoát hàm → code phía sau unreachable (retry thành gọi 1 lần); gán 2 biến trên 1 dòng (`chunks, cur = [], start`); `PYTHONPATH=src` khi chạy script từ terminal.
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
  - Retry: PyCharm báo bước 4–5 unreachable → mọi nhánh trong `try/except` đều `raise`/`return` → đổi thành `error = ...`, chỉ `raise` khi hết lượt.
  - `split_by_year`: `chunks = [], cur = start` bị hiểu là gán chuỗi + unpack `date` → `chunks, cur = [], start`.
  - `No module named vietsky` → chạy từ terminal thiếu `PYTHONPATH=src`.
  - 238 `pm2_5` NULL = 7 giờ đầu 04/08/2022 × 34 tỉnh: giới hạn nguồn, không phải lỗi pipeline.
- Chiến thắng hôm nay: 2,57 triệu dòng lịch sử trong 14,5 phút; PM2.5 Hà Nội theo tháng có đỉnh 71,4 (01/2025), các đỉnh rơi vào tháng 12 → 4. Điểm lạ: mùa vụ không rõ như kỳ vọng (07/2025 = 58,2), dữ liệu là mô hình CAMS.
- TODO cho mai (Ngày 7, ngày nhẹ): so PM2.5 Hà Nội vs TP.HCM để kiểm tra mùa vụ; trả lời 2 câu tình huống Ngày 6; (tùy) watermark.
- Mức tự viết (không AI) hôm nay: __ / 10 (tự điền khung upsert, tự viết retry + split_by_year; AI làm config, backfill.py, sửa unreachable)

### Ngày 7 – 23/11 · ✅ Mốc 1
- Trạng thái: ✅ Xong Bắt buộc (bỏ qua: tự viết lại `transform.py`; test do AI viết theo yêu cầu; chưa làm Bước 4 bù trễ)
- Đã làm: cài `pytest` + `pytest.ini` (`pythonpath = src`); 8 test (5 cho `to_rows`, 3 cho `check_coordinates`) xanh 8/8; README v1: sơ đồ kiến trúc Mermaid (tự điền 4/4 đúng), luồng dữ liệu 5 ý, cách chạy 6 bước.
- Khái niệm hiểu rõ: các chặng extract → raw → transform + load → staging; `dim_location` là dữ liệu tham chiếu; log nằm ở `ops.pipeline_runs`.
- Khái niệm còn mơ hồ (từ bài kể luồng dữ liệu): transform đổi JSON → dòng + gắn múi giờ (không có CSV); schema lo định dạng, DQ checks lo nội dung; upsert + khoá chính bảo vệ dữ liệu khi chạy lại, `pipeline_runs` chỉ quan sát.
- Lỗi gặp phải → cách khoanh vùng → cách sửa: không có lỗi code; 3 chỗ hiểu lệch vai trò thành phần trong bài kể → sửa trong README.
- Chiến thắng hôm nay: pipeline hoàn chỉnh đầu tiên có test, README người khác chạy được.
- TODO: push lên GitHub; (tùy) so mùa vụ PM2.5 Hà Nội vs TP.HCM, dọn `fetch_all.py`/`plot_raw.py`/`geocode.py`; tự viết lại `transform.py` khi có thời gian. Ngày 8: star schema.
- Mức tự viết (không AI) hôm nay: __ / 10 (tự điền sơ đồ + viết bài kể luồng; AI viết test, README)

### Ngày 8 – 24/11 · Star schema
- Trạng thái: ✅ Xong Bắt buộc + 🏆 heatmap (chưa làm Mở rộng: SCD2 `dim_location`)
- Đã làm: `sql/02_mart.sql` (schema `mart`: `dim_location` surrogate key `SERIAL`, `dim_date` theo giờ VN, 2 fact grain 1 tỉnh × 1 giờ, PK `(location_key, ts_utc)`, FK tới dim); `sql/mart/dims.sql` (upsert SCD1 + lịch `generate_series`), `fact_*.sql` (full refresh `TRUNCATE` + `INSERT ... SELECT`, tra khoá qua JOIN); `00_ops.sql` mở CHECK cho `build_mart`; `src/vietsky/mart.py` đối soát staging = mart, lệch thì raise trước commit; chặng `build_mart` trong `run_pipeline.py`. Lần chạy cuối: 6/6 chặng SUCCESS, 1.284.384 dòng mỗi fact.
- Khái niệm hiểu rõ: grain = 1 dòng đại diện cho cái gì (= PK); measure (để tính) vs thuộc tính dim (để lọc/nhóm); `dim_date` theo giờ VN; dim upsert để khoá ổn định, fact full refresh vì là dữ liệu dẫn xuất.
- Khái niệm còn mơ hồ: tên cột vs từ khoá (`f.hour` vs `EXTRACT(HOUR ...)`); tên cột vs giá trị chữ (`region` vs `'Hà Nội'`); 2 `PRIMARY KEY` trong 1 bảng; `CREATE TABLE` vs `TRUNCATE`; GROUP BY theo thời điểm (`ts_utc`) thay vì giờ trong ngày (`hour_vn`), nên mỗi nhóm chỉ có 1 dòng.
- Lỗi gặp phải → cách khoanh vùng → cách sửa:
  - `build_mart` weather FAILED: FK chặn `date_key = 20261124` không có trong `dim_date` → lịch chỉ lấy MIN/MAX từ staging air_quality, nguồn này chưa load ngày 24/11 → lấy khoảng ngày từ cả 2 bảng staging (`UNION ALL`). Nhờ rollback, fact cũ vẫn còn đủ 1.283.568 dòng.
  - `wind_direction` không có trong staging → `wind_speed`.
- Chiến thắng hôm nay: heatmap PM2.5 Hà Nội 12 tháng × 24 giờ; query chỉ còn JOIN + GROUP BY, không cần `AT TIME ZONE`. Đỉnh 19–23h, đáy 11–12h; tháng 4 cao nhất (58,0, ô cao nhất 68,9 lúc 19h), giả thuyết: mùa đốt sinh khối ở Đông Nam Á lục địa.
- TODO cho mai (Ngày 9): trả lời 3 câu tình huống Ngày 8; (tùy) SCD2 `dim_location` theo đợt sáp nhập 01/7/2025.
- Mức tự viết (không AI) hôm nay: __ / 10 (tự trả lời thiết kế, tự điền DDL + dims.sql + fact.sql + Q16; AI viết mart.py, sửa run_pipeline.py, sửa lỗi dim_date)
