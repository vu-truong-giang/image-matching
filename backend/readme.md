main.py        code FastAPI
requirements  thư viện cần cài
dataset/       chứa ảnh gốc đã nhúng watermark để tìm kiếm 
extracted/     ảnh khi đã khôi phục sẽ trích xuất watermark , watermark dc lưu vào đây 
static/        chứa ảnh bị tấn công rotate , zoom , .... 
uploads/       chứa ảnh người dùng upload
usv/           chứa 3 file S,U,V khi đã nhúng watermark vào ảnh
watermarks/    chứa logo watermark để nhúng vào ảnh 



Ảnh gốc
→ DWT
→ lấy vùng LL
→ SVD vùng LL
→ nhúng watermark vào ma trận S
→ inverse SVD
→ inverse DWT
→ ảnh đã nhúng watermark


Trong SVD:

A=USV
T

1. S_host

Là:

singular values của ảnh gốc

được lấy từ:

U_host, S_host, Vt_host = np.linalg.svd(LL)

Ví dụ:

S_host = [5000, 3200, 1800, ...]
Nó dùng để làm gì?

Khi extract watermark:

S_extract = (S_w - S_host) / alpha

Bạn cần:

S_host gốc

để biết watermark đã làm thay đổi singular values bao nhiêu.

2. U_wm

Là:

ma trận U của watermark

từ:

U_wm, S_wm, Vt_wm = np.linalg.svd(watermark)
3. Vt_wm

Là:

ma trận Vᵀ của watermark
Tại sao cần U_wm và Vt_wm

Vì khi extract bạn chỉ recover được:

S_extract

là singular values watermark thôi.

Muốn dựng lại watermark phải:

watermark_extract =
U_wm
×
diag(S_extract)
×
Vt_wm