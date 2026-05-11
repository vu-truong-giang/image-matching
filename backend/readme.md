main.py        code FastAPI
requirements  thư viện cần cài
dataset/       chứa ảnh gốc để tìm kiếm
uploads/       chứa ảnh người dùng upload
static/        chứa ảnh kết quả trả về frontend



Ảnh gốc
→ DWT
→ lấy vùng LL
→ SVD vùng LL
→ nhúng watermark vào ma trận S
→ inverse SVD
→ inverse DWT
→ ảnh đã nhúng watermark