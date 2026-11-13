import os
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)

# Set MODEL_PATH to the location of your trained weights.
MODEL_PATH = os.environ.get("MODEL_PATH", "best.pt")
CONFIDENCE = float(os.environ.get("YOLO_CONF", "0.70"))
KTP_CLASS_ID = int(os.environ.get("KTP_CLASS_ID", "0"))

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model tidak ditemukan: {MODEL_PATH}. "
        "Letakkan best.pt di folder project atau set environment variable MODEL_PATH."
    )

model = YOLO(MODEL_PATH)

@app.after_request
def allow_iframe(response):
    response.headers.pop("X-Frame-Options", None)

    # Izinkan iframe dari domain mana pun.
    response.headers["Content-Security-Policy"] = "frame-ancestors *"

    return response

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/detect")
def detect():
    if "frame" not in request.files:
        return jsonify({"error": "Frame kamera tidak ditemukan"}), 400

    raw = request.files["frame"].read()
    image_array = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Frame tidak dapat dibaca"}), 400

    height, width = frame.shape[:2]

    # Run YOLO inference. No image is saved to disk.
    result = model.predict(frame, conf=CONFIDENCE, verbose=False)[0]

    detections = []
    if result.boxes is not None:
        for box in result.boxes:
            class_id = int(box.cls.item())
            if class_id != KTP_CLASS_ID:
                continue

            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            detections.append({
                "class_id": class_id,
                "label": "KTP",
                "confidence": float(box.conf.item()),
                "x1": max(0, min(width, x1)),
                "y1": max(0, min(height, y1)),
                "x2": max(0, min(width, x2)),
                "y2": max(0, min(height, y2))
            })

    return jsonify({
        "detected": len(detections) > 0,
        "width": width,
        "height": height,
        "detections": detections
    })

if __name__ == "__main__":
    # Camera access works on localhost. For access from other devices,
    # deploy behind HTTPS because browsers restrict getUserMedia on insecure origins.
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
