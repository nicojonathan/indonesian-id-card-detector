CARA MENJALANKAN

1. Ekstrak folder project.
2. Salin file best.pt hasil training ke folder yang sama dengan app.py.
3. Buat virtual environment (opsional tetapi disarankan):
   python -m venv .venv
   Windows: .venv\Scripts\activate
   macOS/Linux: source .venv/bin/activate
4. Install dependensi:
   pip install -r requirements.txt
5. Jalankan:
   python app.py
6. Buka browser:
   http://127.0.0.1:5000
7. Klik Nyalakan Kamera dan izinkan akses kamera.

KONFIGURASI
- Default model: best.pt
- Class KTP: 0
- Confidence threshold: 0.40

Windows PowerShell, contoh mengganti lokasi model:
$env:MODEL_PATH="runs/detect/train/weights/best.pt"
$env:KTP_CLASS_ID="0"
$env:YOLO_CONF="0.40"
python app.py

Catatan:
- Sesuaikan MODEL_PATH dengan lokasi file best.pt milikmu.
- Kamera browser umumnya memerlukan localhost atau HTTPS.
- Frame hanya diproses di memori oleh contoh aplikasi ini; tidak disimpan.
- Untuk deployment publik, gunakan HTTPS, autentikasi, pembatasan akses, dan
  kebijakan privasi yang sesuai. Jangan mengekspos server development Flask.
