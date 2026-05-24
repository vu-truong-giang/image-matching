import { useState } from "react";
import {
  Upload,
  Image as ImageIcon,
  Search,
  ShieldCheck,
  RotateCw,
  Download,
  Loader2,
  Images,
  ScanSearch,
} from "lucide-react";

const API_URL = "http://localhost:8000";

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [mode, setMode] = useState("sift");
  const [results, setResults] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [embedFiles, setEmbedFiles] = useState([]);
  const [watermarkFile, setWatermarkFile] = useState(null);
  const [embedResults, setEmbedResults] = useState([]);

  const isMultiWatermark = mode === "multi-watermark";

  const [attackType, setAttackType] = useState("rotate");
 const [attackValue, setAttackValue] = useState(30);

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setImagePreview(URL.createObjectURL(file));
    setProcessedImage(null);
    setResults([]);
    setEmbedResults([]);
    setMessage("");
  };

  const handleEmbedMany = async () => {
    if (!embedFiles.length) {
      alert("Bạn cần chọn nhiều ảnh để embed");
      return;
    }

    if (!watermarkFile) {
      alert("Bạn cần chọn ảnh watermark");
      return;
    }

    const formData = new FormData();

    for (let file of embedFiles) {
      formData.append("files", file);
    }

    formData.append("watermark", watermarkFile);

    try {
      setLoading(true);
      setMessage("");
      setEmbedResults([]);
      setProcessedImage(null);
      setResults([]);

      const response = await fetch(`${API_URL}/embed-watermark-folder`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Embed nhiều ảnh thất bại");
      }

      const data = await response.json();
      setMessage(data.message || "Embed nhiều ảnh thành công");
      setEmbedResults(data.results || []);
    } catch (error) {
      console.error(error);
      setMessage("Có lỗi khi embed nhiều ảnh. Kiểm tra backend FastAPI đã chạy chưa.");
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    if (isMultiWatermark) {
      await handleEmbedMany();
      return;
    }

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
      setEmbedResults([]);
      setProcessedImage(null);

      let endpoint = "/search";

      if (mode === "watermark") {
        endpoint = "/embed-watermark";
      }
      if (mode === "extract-watermark") {
        endpoint = "/extract-watermark";
      }

      if (mode === "attack") {
        endpoint = "/transform";
        formData.append("attack_type", attackType);
        formData.append("value", attackValue);
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

          if (/\.(tiff?|tif)$/i.test(imageName)) {
            setProcessedImage(`${API_URL}/dataset_png/${imageName}`);
          } else {
            setProcessedImage(`${API_URL}/dataset/${imageName}`);
          }
        }
      }

      if (mode === "watermark") {
        setMessage(data.message || "Nhúng thủy vân thành công");

        if (data.output_path) {
          setProcessedImage(`${API_URL}/${data.output_path}`);
        }
      }
      if (mode === "extract-watermark") {
        setMessage(data.message || "Trích xuất watermark thành công");

        if (data.output_path) {
          setProcessedImage(`${API_URL}/${data.output_path}`);
        }
      }

      if (mode === "attack") {
        setMessage(data.message || "Tấn công hình học thành công");

        if (data.output_path) {
          setProcessedImage(`${API_URL}/${data.output_path}`);
        }
      }
    } catch (error) {
      console.error(error);
      setMessage("Có lỗi khi gọi API. Kiểm tra backend FastAPI đã chạy chưa.");
    } finally {
      setLoading(false);
    }
  };

  const buttonClass = (buttonMode) =>
    `flex w-full items-center gap-3 rounded-xl p-3 text-left transition ${
      mode === buttonMode
        ? "bg-blue-600 text-white"
        : "bg-slate-100 hover:bg-slate-200"
    }`;

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

            {!isMultiWatermark && (
              <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center hover:bg-slate-100">
                <Upload className="mb-3 h-10 w-10 text-slate-500" />
                <span className="font-medium">Tải ảnh lên</span>
                <span className="mt-1 text-sm text-slate-500">JPG, PNG, TIFF</span>
                <input
                  type="file"
                  accept="image/*,.tiff,.tif"
                  className="hidden"
                  onChange={handleImageChange}
                />
              </label>
            )}

            {isMultiWatermark && (
              <div className="rounded-2xl border bg-slate-50 p-4">
                <label className="mb-3 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-white p-5 text-center hover:bg-slate-100">
                  <Upload className="mb-2 h-8 w-8 text-slate-500" />
                  <span className="font-medium">Chọn nhiều ảnh</span>
                  <span className="text-sm text-slate-500">
                    Giữ Ctrl hoặc Shift để chọn nhiều ảnh
                  </span>
                  <input
                    type="file"
                    accept="image/*,.tiff,.tif"
                    multiple
                    className="hidden"
                    onChange={(e) => setEmbedFiles(Array.from(e.target.files || []))}
                  />
                </label>

                <p className="mb-3 text-sm text-slate-600">
                  Đã chọn: {embedFiles.length} ảnh
                </p>

                <label className="mb-3 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-white p-5 text-center hover:bg-slate-100">
                  <ShieldCheck className="mb-2 h-8 w-8 text-slate-500" />
                  <span className="font-medium">Chọn ảnh watermark</span>
                  <input
                    type="file"
                    accept="image/*,.tiff,.tif"
                    className="hidden"
                    onChange={(e) => setWatermarkFile(e.target.files?.[0] || null)}
                  />
                </label>

                <p className="text-sm text-slate-600">
                  Watermark: {watermarkFile ? watermarkFile.name : "Chưa chọn"}
                </p>
              </div>
            )}

            <h2 className="mb-3 mt-6 text-xl font-semibold">2. Chọn chức năng</h2>
            <div className="space-y-3">
              <button onClick={() => setMode("sift")} className={buttonClass("sift")}>
                <Search className="h-5 w-5" />
                Tìm ảnh tương đồng bằng SIFT
              </button>

              <button onClick={() => setMode("watermark")} className={buttonClass("watermark")}>
                <ShieldCheck className="h-5 w-5" />
                Nhúng thủy vân
              </button>

              <button
                onClick={() => setMode("multi-watermark")}
                className={buttonClass("multi-watermark")}
              >
                <Images className="h-5 w-5" />
                Nhúng thủy vân nhiều ảnh
              </button>
              <button
                  onClick={() => setMode("extract-watermark")}
                  className={`flex w-full items-center gap-3 rounded-xl p-3 text-left transition ${
                    mode === "extract-watermark"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-100 hover:bg-slate-200"
                  }`}
                >
                  <ScanSearch className="h-5 w-5" />
                  Trích xuất watermark
                </button>

              <button onClick={() => setMode("attack")} className={buttonClass("attack")}>
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
              {loading ? "Đang xử lý..." : isMultiWatermark ? "Embed nhiều ảnh" : "Thực hiện xử lý"}
            </button>
          </section>

          <section className="rounded-2xl bg-white p-5 shadow-sm lg:col-span-2">
            <h2 className="mb-4 text-xl font-semibold">3. Kết quả xử lý</h2>
            
            <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border bg-slate-50 p-4">
                  <h3 className="mb-3 font-semibold">Ảnh đầu vào</h3>
                  <div className="flex h-72 items-center justify-center overflow-hidden rounded-xl bg-white">
                    {imagePreview ? (
                      <img
                        src={imagePreview}
                        alt="Ảnh đầu vào"
                        className="h-full w-full object-contain"
                      />
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
                      <img
                        src={processedImage}
                        alt="Ảnh sau xử lý"
                        className="h-full w-full object-contain"
                      />
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
                  <p className="mb-3 text-sm">Kết quả tìm kiếm ảnh tương đồng trong dataset:</p>

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
                  <p>
                    <b>Chức năng:</b> Nhúng thủy vân vào ảnh bằng DWT + SVD.
                  </p>
                  <p>
                    <b>API gọi:</b> POST /embed-watermark
                  </p>
                </div>
              )}

              {mode === "multi-watermark" && (
                <div className="space-y-4 text-sm">
                  <p>
                    <b>Chức năng:</b> Nhúng cùng một watermark vào nhiều ảnh.
                  </p>
                  <p>
                    <b>API gọi:</b> POST /embed-watermark-folder
                  </p>

                  {embedResults.length > 0 ? (
                    <div className="overflow-hidden rounded-xl border bg-white">
                      <table className="w-full text-sm">
                        <thead className="bg-slate-200">
                          <tr>
                            <th className="p-3 text-left">STT</th>
                            <th className="p-3 text-left">Tên ảnh</th>
                            <th className="p-3 text-left">Ảnh output</th>
                            <th className="p-3 text-left">Trạng thái</th>
                          </tr>
                        </thead>
                        <tbody>
                          {embedResults.map((item, index) => (
                            <tr key={index} className="border-t">
                              <td className="p-3">{index + 1}</td>
                              <td className="p-3">{item.filename}</td>
                              <td className="p-3">{item.watermarked_filename || "-"}</td>
                              <td className="p-3">{item.status}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">
                      Chưa có kết quả embed nhiều ảnh.
                    </p>
                  )}
                </div>
              )}
              {mode === "extract-watermark" && (
                <div className="space-y-2 text-sm">
                  <p>
                    <b>Chức năng:</b> Trích xuất watermark từ ảnh đã nhúng.
                  </p>
                  <p>
                    <b>API gọi:</b> POST /extract-watermark
                  </p>
                  <p className="text-slate-600">
                    Chọn ảnh có tên dạng <b>watermarked_...</b> để backend tìm đúng file USV.
                  </p>
                </div>
              )}

              {mode === "attack" && (
                <div className="space-y-4 text-sm">
                  <p>
                    <b>Chức năng:</b> Tạo ảnh bị tấn công hình học.
                  </p>

                  <div>
                    <label className="mb-2 block font-medium">
                      Chọn kiểu tấn công
                    </label>

                    <select
                      value={attackType}
                      onChange={(e) => setAttackType(e.target.value)}
                      className="w-full rounded-xl border p-3"
                    >
                      <option value="rotate">Xoay ảnh</option>
                      <option value="crop">Cắt viền</option>
                      <option value="resize">Resize</option>
                      <option value="brightness">Tăng sáng</option>
                      <option value="noise">Thêm nhiễu</option>
                    </select>
                  </div>

                  {attackType !== "noise" && (
                    <div>
                      <label className="mb-2 block font-medium">
                        Nhập giá trị
                      </label>

                      <input
                        type="number"
                        value={attackValue}
                        onChange={(e) => setAttackValue(e.target.value)}
                        className="w-full rounded-xl border p-3"
                        placeholder="Ví dụ rotate: 30"
                      />
                    </div>
                  )}

                  <div className="rounded-xl bg-slate-100 p-3">
                    {attackType === "rotate" && <p>Rotate: nhập góc xoay, ví dụ 30.</p>}
                    {attackType === "crop" && <p>Crop: nhập phần trăm cắt, ví dụ 0.1.</p>}
                    {attackType === "resize" && <p>Resize: nhập tỉ lệ, ví dụ 0.7.</p>}
                    {attackType === "brightness" && <p>Brightness: nhập độ sáng, ví dụ 50.</p>}
                    {attackType === "noise" && <p>Noise: không cần nhập giá trị.</p>}
                  </div>

                  <p>
                    <b>API gọi:</b> POST /transform
                  </p>
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
