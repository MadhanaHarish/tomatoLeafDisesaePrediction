from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import io
import os
import gc
import traceback

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Load YOLO model once globally
MODEL_PATH = os.getenv('MODEL_PATH', './models/best11n.pt')
model = YOLO(MODEL_PATH)

@app.route('/detect', methods=['POST', 'OPTIONS'])
def detect_image():
    # Declare variables at function scope for finally block
    file = img_bytes = nparr = img = results = annotated = None

    try:
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200

        # Check if image present
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        img_bytes = file.read()
        if len(img_bytes) == 0:
            return jsonify({'error': 'Empty file'}), 400

        # Decode image
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400

        # Run YOLO inference
        results = model(img, verbose=False)
        annotated = results[0].plot()

        # Encode annotated image
        success, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not success:
            return jsonify({'error': 'Failed to process image'}), 500

        img_io = io.BytesIO(buffer)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg')

    except Exception as e:
        print("Error in detect_image:", e)
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500  # Generic error for production

    finally:
        # Safe memory cleanup
        gc.collect()

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)