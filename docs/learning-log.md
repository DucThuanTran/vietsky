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
