# Proyek Analisis Data: Bike Sharing Dataset
Proyek ini menganalisis data penyewaan sepeda **Capital Bikeshare, Washington D.C. (2011–2012)** dan menyajikan hasilnya dalam dashboard interaktif menggunakan Streamlit.

Pertanyaan bisnis yang dijawab (sama dengan yang terdapat pada `notebook.ipynb`):

1. Pada jam berapa saja tiga jam dengan rata-rata penyewaan sepeda tertinggi pada hari kerja dibandingkan akhir pekan/hari libur sepanjang tahun 2012, dan berapa kali lipat penyewaan jam puncak dibandingkan jam terendah?
2. Berapa persen penurunan rata-rata penyewaan harian saat cuaca berkabut dan hujan/salju ringan dibandingkan cuaca cerah, serta pada kategori suhu apa rata-rata penyewaan harian paling tinggi selama periode 2011–2012?
3. Berapa persen pertumbuhan total penyewaan tahun 2012 dibandingkan dengan 2011 untuk pengguna casual dan registered, serta pada bulan apa saja pertumbuhannya paling rendah?

Analisis lanjutan (tanpa *machine learning*): pengelompokan manual (*manual grouping/binning*) berdasarkan kategori suhu dan tingkat permintaan per jam.

## Struktur Proyek

```
Submission
├── dashboard
│   ├── dashboard.py
│   ├── main_data.csv
│   └── day_data.csv
├── data
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

Keterangan:

- `data/day.csv` dan `data/hour.csv`: dataset mentah (pemisah kolom `;`).
- `notebook.ipynb`: proses analisis lengkap. Pada bagian akhir, notebook menyimpan data bersih ke `dashboard/main_data.csv` (per jam) dan `dashboard/day_data.csv` (per hari).
- `dashboard/dashboard.py`: aplikasi Streamlit. Kedua berkas CSV tersebut harus berada di folder yang sama dengan `dashboard.py` karena dibaca dari lokasi skrip.
- `url.txt`: tautan dashboard yang telah dideploy ke Streamlit Community Cloud.

## Prasyarat

- [Python](https://www.python.org/downloads/) 3.10 atau lebih baru
- [Visual Studio Code](https://code.visualstudio.com/) dengan ekstensi **Python** dan **Jupyter**

## Setup Environment

1. Buka folder proyek di VS Code: **File → Open Folder…** lalu pilih folder `Submission`.
2. Buka terminal bawaan VS Code: **Terminal → New Terminal**.
3. (Opsional, disarankan) buat virtual environment agar library proyek tidak tercampur dengan Python global.

   Windows:

   ```shell
   python -m venv venv
   venv\Scripts\activate
   ```

   macOS/Linux:

   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```

   Jika muncul error *execution policy* di PowerShell, jalankan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, lalu ulangi perintah aktivasi.

4. Pasang library yang dibutuhkan (untuk dashboard maupun notebook):

   ```shell
   pip install -r requirements.txt
   ```

## Menjalankan Notebook

1. Buka `notebook.ipynb` di VS Code atau Jupyter.
2. Pastikan folder kerja adalah folder utama proyek (`Submission`), karena data dibaca dengan path relatif `data/day.csv` dan `data/hour.csv`.
3. Pilih kernel Python yang sudah terpasang library proyek, lalu jalankan seluruh sel dari atas (**Run All**).

Sel terakhir pada bagian Analisis Lanjutan akan memperbarui `dashboard/main_data.csv` dan `dashboard/day_data.csv`.

## Menjalankan Dashboard

1. Pada terminal, pastikan posisi berada di folder utama proyek (`Submission`), yaitu folder yang berisi `notebook.ipynb`, `data`, dan `dashboard`. Jika terminal masih berada di dalam folder `dashboard`, pindah ke folder utama dengan perintah:

   ```shell
   cd ..
   ```

   Jika terminal berada di lokasi lain, pindah ke folder utama dengan `cd` diikuti lokasi folder proyek, misalnya:

   ```shell
   cd "C:\4. AQILLA\kuliah\semester 5\ASAH DICODING\KELAS FAD\Submission"
   ```

2. Jalankan dashboard:

   ```shell
   streamlit run dashboard/dashboard.py
   ```

   Jika perintah `streamlit` tidak dikenali, gunakan:

   ```shell
   python -m streamlit run dashboard/dashboard.py
   ```

   Pada Windows, jika perintah `python` tidak dikenali, gunakan:

   ```shell
   py -m streamlit run dashboard/dashboard.py
   ```
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.100.59:8501
```

Buka `http://localhost:8501` di browser untuk melihat dashboard. Tekan `Ctrl + C` di terminal untuk menghentikan aplikasi.

## Fitur Dashboard

- **Filter sidebar**: rentang tanggal dan musim.
- **Ringkasan indikator utama**: total penyewaan, rata-rata per hari, serta proporsi pengguna *registered* dan *casual*.
- **Pola Jam**: rata-rata penyewaan per jam untuk hari kerja dibandingkan akhir pekan/libur.
- **Cuaca dan Suhu**: pengaruh kondisi cuaca dan musim terhadap penyewaan.
- **Pertumbuhan**: pertumbuhan tahunan 2012 terhadap 2011 secara total, per tipe pengguna, dan per bulan.
- **Analisis Lanjutan**: pengelompokan penyewaan berdasarkan kategori suhu.

Teks insight pada dashboard dihitung dari data yang sedang difilter. Pengecualian: bagian **Pertumbuhan** selalu memakai seluruh data 2011–2012 agar perbandingan tahunan adil.

## Catatan Data

- Label musim mengikuti kode pada dokumentasi dataset (Musim Semi = kode 1, Musim Panas = 2, Musim Gugur = 3, Musim Dingin = 4). Musim Semi (kode 1) mencakup Januari sampai 20 Maret dan 21 sampai 31 Desember, yang secara kalender termasuk musim dingin di Washington D.C.
- Suhu dikembalikan ke satuan asli dengan pengali dari deskripsi dataset di Kaggle (`temp` × 41, `atemp` × 50, `hum` × 100, `windspeed` × 67).

## Sumber Data

Bike Sharing Dataset (Fanaee-T dan Gama), Capital Bikeshare.
