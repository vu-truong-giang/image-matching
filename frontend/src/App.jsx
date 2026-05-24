import { useState } from "react";
// Using backend-converted PNGs; remove TiffViewer usage
import { Upload, Image as ImageIcon, Search, ShieldCheck, RotateCw, Download, Loader2 } from "lucide-react";

const API_URL = "http://localhost:8000";

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [mode, setMode] = useState("sift");
  const [results, setResults] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setImagePreview(URL.createObjectURL(file));
    setProcessedImage(null);
    setResults([]);
    setMessage("");
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      alert("Bạn cần chọn ảnh trước");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);
      setMessage("");
      setResults([]);
      setProcessedImage(null);

      let endpoint = "/search";

      if (mode === "watermark") {
        endpoint = "/embed-watermark";
      }

      if (mode === "attack") {
        endpoint = "/transform";
        formData.append("attack_type", "rotate");
        formData.append("angle", "30");
      }

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Gọi API thất bại");
      }

      const data = await response.json();
      console.log("API response:", data);

      if (mode === "sift") {
        setResults(data.results || []);
        setMessage(`Ảnh truy vấn: ${data.query_image || selectedFile.name}`);
        if (data.results && data.results.length > 0) {
          const firstResult = data.results[0];

          const imageName = firstResult.image_name || "";
          if ((/\.(tiff?|tif)$/i).test(imageName)) {
            setProcessedImage(`${API_URL}/dataset_png/${imageName}`);
          } else {
            setProcessedImage(`${API_URL}/dataset/${imageName}`);
          }
        }
      }

      if (mode === "watermark") {
        setMessage(data.message || "Nhúng thủy vân thành công");
        if (data.output_image) {
          setProcessedImage(`${API_URL}/${data.output_image}`);
        }
      }

      if (mode === "attack") {
        setMessage(data.message || "Tấn công hình học thành công");
        if (data.output_image) {
          setProcessedImage(`${API_URL}/${data.output_image}`);
        }
      }
    } catch (error) {
      console.error(error);
      setMessage("Có lỗi khi gọi API. Kiểm tra backend FastAPI đã chạy chưa.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-6 text-slate-800">
      <div className="mx-auto max-w-6xl">
        <header className="mb-6 rounded-2xl bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold">Hệ thống xử lý ảnh</h1>
          <p className="mt-2 text-slate-600">
            Demo đề tài: nhận dạng ảnh bằng SIFT và thủy vân số chống tấn công hình học.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-3">
          <section className="rounded-2xl bg-white p-5 shadow-sm lg:col-span-1">
            <h2 className="mb-4 text-xl font-semibold">1. Chọn ảnh</h2>

            <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center hover:bg-slate-100">
              <Upload className="mb-3 h-10 w-10 text-slate-500" />
              <span className="font-medium">Tải ảnh lên</span>
              <span className="mt-1 text-sm text-slate-500">JPG, PNG, TIFF</span>
              <input type="file" accept="image/*,.tiff,.tif" className="hidden" onChange={handleImageChange} />
            </label>

            <h2 className="mb-3 mt-6 text-xl font-semibold">2. Chọn chức năng</h2>
            <div className="space-y-3">
              <button
                onClick={() => setMode("sift")}
                className={`flex w-full items-center gap-3 rounded-xl p-3 text-left transition ${
                  mode === "sift" ? "bg-blue-600 text-white" : "bg-slate-100 hover:bg-slate-200"
                }`}
              >
                <Search className="h-5 w-5" />
                Tìm ảnh tương đồng bằng SIFT
              </button>

              <button
                onClick={() => setMode("watermark")}
                className={`flex w-full items-center gap-3 rounded-xl p-3 text-left transition ${
                  mode === "watermark" ? "bg-blue-600 text-white" : "bg-slate-100 hover:bg-slate-200"
                }`}
              >
                <ShieldCheck className="h-5 w-5" />
                Nhúng thủy vân
              </button>

              <button
                onClick={() => setMode("attack")}
                className={`flex w-full items-center gap-3 rounded-xl p-3 text-left transition ${
                  mode === "attack" ? "bg-blue-600 text-white" : "bg-slate-100 hover:bg-slate-200"
                }`}
              >
                <RotateCw className="h-5 w-5" />
                Tấn công hình học
              </button>
            </div>

            <button
              onClick={handleProcess}
              disabled={loading}
              className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-green-600 py-3 font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading && <Loader2 className="h-5 w-5 animate-spin" />}
              {loading ? "Đang xử lý..." : "Thực hiện xử lý"}
            </button>
          </section>

          <section className="rounded-2xl bg-white p-5 shadow-sm lg:col-span-2">
            <h2 className="mb-4 text-xl font-semibold">3. Kết quả xử lý</h2>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border bg-slate-50 p-4">
                <h3 className="mb-3 font-semibold">Ảnh đầu vào</h3>
                <div className="flex h-72 items-center justify-center overflow-hidden rounded-xl bg-white">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Ảnh đầu vào" className="h-full w-full object-contain" />
                  ) : (
                    <div className="text-center text-slate-400">
                      <ImageIcon className="mx-auto mb-2 h-12 w-12" />
                      Chưa có ảnh
                    </div>
                  )}
                </div>
              </div>

              <div className="rounded-2xl border bg-slate-50 p-4">
                <h3 className="mb-3 font-semibold">Ảnh sau xử lý</h3>
                <div className="flex h-72 items-center justify-center overflow-hidden rounded-xl bg-white text-center text-slate-400">
                  {processedImage ? (
                    <img src={processedImage} alt="Ảnh sau xử lý" className="h-full w-full object-contain" />
                  ) : (
                    <div>
                      <ImageIcon className="mx-auto mb-2 h-12 w-12" />
                      Kết quả sẽ hiển thị tại đây
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-5 rounded-2xl border bg-slate-50 p-4">
              <h3 className="mb-3 font-semibold">Thông tin kết quả</h3>

              {message && <p className="mb-3 text-sm text-slate-700">{message}</p>}

              {mode === "sift" && (
                <div>
                  <p className="mb-3 text-sm">
                    Kết quả tìm kiếm ảnh tương đồng trong dataset:
                  </p>

                  {results.length > 0 ? (
                    <div className="overflow-hidden rounded-xl border bg-white">
                      <table className="w-full text-sm">
                        <thead className="bg-slate-200">
                          <tr>
                            <th className="p-3 text-left">STT</th>
                            <th className="p-3 text-left">Tên ảnh</th>
                            <th className="p-3 text-left">Score</th>
                          </tr>
                        </thead>
                        <tbody>
                          {results.map((item, index) => (
                            <tr key={index} className="border-t">
                              <td className="p-3">{index + 1}</td>
                              <td className="p-3 font-medium">{item.image_name}</td>
                              <td className="p-3">{item.score}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">Chưa có kết quả.</p>
                  )}
                </div>
              )}

              {mode === "watermark" && (
                <div className="space-y-2 text-sm">
                  <p><b>Chức năng:</b> Nhúng thủy vân vào ảnh bằng DWT + SVD.</p>
                  <p><b>API gọi:</b> POST /embed-watermark</p>
                </div>
              )}

              {mode === "attack" && (
                <div className="space-y-2 text-sm">
                  <p><b>Chức năng:</b> Tạo ảnh bị tấn công hình học như xoay, crop hoặc resize.</p>
                  <p><b>API gọi:</b> POST /transform</p>
                </div>
              )}
            </div>

            <div className="mt-5 flex justify-end">
              <button className="flex items-center gap-2 rounded-xl bg-slate-800 px-5 py-3 font-semibold text-white hover:bg-slate-900">
                <Download className="h-5 w-5" />
                Tải kết quả
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
