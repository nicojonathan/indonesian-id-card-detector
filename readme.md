# KTP Detection with YOLO

A lightweight web application for detecting Indonesian identity cards (**Kartu Tanda Penduduk / KTP**) in a live camera feed. It uses a trained Ultralytics YOLO model for server-side inference and provides a guided capture flow for integrating the cropped KTP image into a parent website.

## Features

- **Live KTP detection** — captures camera frames periodically and sends them to a Flask endpoint for YOLO inference.
- **Visual detection feedback** — draws bounding boxes and confidence scores over detected KTPs.
- **KTP-aligned capture guide** — displays a centered dotted guide using the Indonesian ID-card aspect ratio (85.6 × 54 mm).
- **Guide-based auto-cropping** — when the user chooses to capture, the image is cropped to the area inside the guide.
- **User-confirmed capture** — detection runs automatically, but the final image is captured and sent only after the user presses the capture button.
- **Parent-page integration** — sends the captured image and related metadata to the embedding page with `window.postMessage()`.
- **Iframe support** — can be embedded in another website when camera permissions and the server's frame-embedding policy are configured correctly.
- **No application-side image storage** — camera frames are processed in memory for inference; the example application does not save them to disk.

## How it works

1. The user opens the page and grants the browser permission to use the camera.
2. The browser requests camera access using the environment-facing camera when available.
3. Approximately every 300 ms, the frontend resizes a camera frame and sends it to `POST /detect`.
4. Flask decodes the frame and passes it to the configured YOLO model.
5. The backend filters detections using the configured KTP class ID and confidence threshold, then returns bounding-box coordinates and confidence values as JSON.
6. The frontend draws the returned detections over the live preview.
7. Once a KTP is detected, the user can press **Ambil Foto & Kirim**. The frontend crops the camera image to the dotted guide area and sends the resulting image to the parent page.

> **Important:** live detection and final capture are separate steps. Detection is performed on the resized camera frame; the guide defines the crop area for the image sent after the user confirms capture.

## Tech stack

- **Backend:** Python, Flask
- **Object detection:** Ultralytics YOLO
- **Image processing:** OpenCV, NumPy
- **Frontend:** HTML, CSS, JavaScript, browser MediaDevices API, Canvas API

## Project structure

```text
ktp_yolo_webcam/
├── app.py
├── best.pt                 # Add your trained YOLO weights here
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

The `best.pt` model file is not included. Use your own trained weights and make sure its KTP class mapping matches the configured class ID.

## Requirements

- Python 3.9 or newer (use a Python version supported by your installed PyTorch/Ultralytics release).
- A trained Ultralytics YOLO weights file, for example `best.pt`.
- A modern browser with camera access support.
- Camera access must be served from `localhost` or a secure context (**HTTPS**) in normal browser environments.

## Getting started

### 1. Clone or download the project

```bash
git clone <your-repository-url>
cd ktp_yolo_webcam
```

If you downloaded the source archive instead, extract it and open a terminal in the `ktp_yolo_webcam` directory.

### 2. Add the YOLO model

Copy your trained model file into the project directory as `best.pt`, or set `MODEL_PATH` to its location.

### 3. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure and run

Default configuration:

| Setting | Default | Description |
|---|---:|---|
| `MODEL_PATH` | `best.pt` | Path to the trained YOLO weights |
| `KTP_CLASS_ID` | `0` | Class index assigned to KTP in the model |
| `YOLO_CONF` | `0.40` | Minimum confidence threshold for detections |

**Windows PowerShell example**

```powershell
$env:MODEL_PATH="best.pt"
$env:KTP_CLASS_ID="0"
$env:YOLO_CONF="0.40"
python app.py
```

**macOS / Linux example**

```bash
export MODEL_PATH="best.pt"
export KTP_CLASS_ID="0"
export YOLO_CONF="0.40"
python app.py
```

Or simply run with the defaults:

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), select **Nyalakan Kamera**, and allow camera access.

## API

### `POST /detect`

Accepts a multipart form upload containing a camera frame.

**Request**

| Field | Type | Description |
|---|---|---|
| `frame` | File (JPEG/image) | Camera frame to process |

**Successful response**

```json
{
  "detected": true,
  "width": 640,
  "height": 360,
  "detections": [
    {
      "class_id": 0,
      "label": "KTP",
      "confidence": 0.96,
      "x1": 120.0,
      "y1": 70.0,
      "x2": 510.0,
      "y2": 300.0
    }
  ]
}
```

The `detections` array can contain more than one KTP detection. Coordinates are expressed in pixels relative to the submitted frame. When no KTP is found, `detected` is `false` and `detections` is an empty array.

## Embedding in a parent website

The application can be displayed inside an iframe. The parent page must grant camera permission to the iframe:

```html
<iframe
  src="https://your-detection-host.example/"
  allow="camera"
  title="KTP Detection"
  width="100%"
  height="640"
></iframe>
```

For cross-origin embedding:

- Serve both the parent page and the detection application over HTTPS.
- Configure the detection server's Content Security Policy `frame-ancestors` directive to allow only the intended parent origin(s).
- Do not send an `X-Frame-Options` policy that blocks the intended embedding origin.
- The browser may also require the parent page's Permissions Policy to allow camera access for the iframe.

### Capture message

After the user confirms the capture, the iframe posts a message to its parent window with this structure:

```javascript
{
  type: "KTP_DETECTED",
  payload: {
    image: imageFile,       // Cropped JPEG File
    detections: detections, // Latest YOLO detection result(s)
    timestamp: "...",      // ISO 8601 timestamp
    crop: {
      width: 0,             // Crop dimensions in source-video pixels
      height: 0
    }
  }
}
```

The parent page can listen for the event:

```javascript
window.addEventListener("message", (event) => {
  // Always validate the sender origin before trusting a message.
  if (event.origin !== "https://your-detection-host.example") return;

  if (event.data?.type === "KTP_DETECTED") {
    const { image, detections, timestamp, crop } = event.data.payload;
    // Handle the captured File and metadata in your application.
  }
});
```

The message contains a browser `File` object, so the parent can handle it like a file selected through an upload input. For production, use a specific target origin in `postMessage()` instead of `"*"` and validate the sender origin in the parent page.

## Privacy and security

- The example backend decodes incoming frames and performs inference in memory; it does not write submitted frames to disk.
- The confirmed crop is passed to the parent page as a `File`. The parent application determines what happens to that file next.
- KTP images contain sensitive personal information. Use the application only in trusted environments and explain any subsequent processing to users.
- Use HTTPS outside localhost, restrict iframe embedding to trusted origins, validate `postMessage` origins, and add appropriate authentication, rate limiting, and access controls before public deployment.
- Do not expose Flask's development server directly to the public internet. Deploy behind a production-ready WSGI server and HTTPS reverse proxy.

## Troubleshooting

| Issue | What to check |
|---|---|
| `Model tidak ditemukan` | Confirm that `best.pt` exists or that `MODEL_PATH` points to the correct file. |
| Camera permission denied | Allow camera access in the browser and check OS-level camera permissions. |
| Camera unavailable in an embedded page | Confirm HTTPS, the iframe `allow="camera"` attribute, and the parent/server Permissions Policy. |
| Iframe is blocked | Review `Content-Security-Policy: frame-ancestors` and remove conflicting frame-blocking `X-Frame-Options` settings. |
| KTP is not detected | Check the model's KTP class index, lighting, camera focus, model weights, and `YOLO_CONF`. |
| Detection is too sensitive or too strict | Adjust `YOLO_CONF` and evaluate the result with representative images. |

## License

No license is specified yet. Add a `LICENSE` file before distributing or reusing this project publicly.
