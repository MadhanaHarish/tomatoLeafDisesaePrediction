import React, { useState } from "react";

function Detect() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [detectedImage, setDetectedImage] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setDetectedImage(null); // reset when new file chosen
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            alert("Please select an image first!");
            return;
        }

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("image", selectedFile);

            const response = await fetch("http://127.0.0.1:5000/detect", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Detection failed");
            }

            // Convert response (blob) to image URL
            const blob = await response.blob();
            const imgUrl = URL.createObjectURL(blob);
            setDetectedImage(imgUrl);
        } catch (error) {
            console.error("Error:", error);
            alert("Detection failed. Check server logs.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: "20px", textAlign: "center" }}>
            <h2>YOLO Object Detection</h2>

            <input type="file" accept="image/*" onChange={handleFileChange} />

            <button
                onClick={handleUpload}
                disabled={!selectedFile || loading}
                style={{
                    marginLeft: "10px",
                    padding: "10px 20px",
                    background: "#007bff",
                    color: "white",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                }}
            >
                {loading ? "Detecting..." : "Upload & Detect"}
            </button>

            <div style={{ marginTop: "20px" }}>
                {detectedImage && (
                    <div>
                        <h3>Detected Image:</h3>
                        <img
                            src={detectedImage}
                            alt="Detected"
                            style={{ maxWidth: "500px", border: "2px solid #333" }}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

export default Detect;
