from flask import Flask, request, send_file
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import io
import os

app = Flask(__name__)

# CORS configuration for production
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Load YOLO model
MODEL_PATH = os.getenv('MODEL_PATH', './models/best11n.pt')
model = YOLO(MODEL_PATH)

@app.route('/detect', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400

    file = request.files['image']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Run YOLO detection
    results = model(img)
    annotated = results[0].plot()

    # Encode result as image
    _, buffer = cv2.imencode('.jpg', annotated)
    img_bytes = io.BytesIO(buffer)
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype='image/jpeg')

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

