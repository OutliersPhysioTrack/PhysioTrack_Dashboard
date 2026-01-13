# PhysioTrack — Streamlit Dashboard

Project ini adalah dashboard berbasis **Streamlit** untuk memantau dan mengelola data rehabilitasi dari **backend PhysioTrack** yang dikirim dari esp32 dan mobile application lewat **REST API**.

## Fitur
- Dashboard ringkasan (angka penting + grafik)
- Data pasien dan detail pasien
- Data sesi latihan (durasi, reps, adherence, ROM, grip, dll)
- Program latihan / assignments
- Alerts / peringatan
- Monitoring device dan pembacaan sensor terbaru

## Prasyarat
- Python 3.10+
- Backend PhysioTrack (FastAPI) sudah berjalan dan bisa diakses

## Instalasi
Install library yang dibutuhkan:
```bash
pip install streamlit pandas requests
