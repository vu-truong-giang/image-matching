Ở thư mục gốc image-matching/:

docker compose up --build

Sau đó mở:

http://localhost:5173

Backend docs:

http://localhost:8000/docs


5. Tắt container
docker compose down
6. Khi sửa code

Nếu sửa frontend/backend mà chưa thấy cập nhật:

docker compose down
docker compose up --build