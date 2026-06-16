# 📦 Aplikasi Pencatat Pengeluaran Harian
Jobsheet 11 - Integrasi OOP | Pemrograman Berorientasi Objek
Politeknik Negeri Semarang

## Struktur File
```
pengeluaran_harian/
├── konfigurasi.py          # Konstanta & konfigurasi path
├── database.py             # Fungsi akses database SQLite
├── model.py                # Kelas Transaksi (Data Class)
├── manajer_anggaran.py     # Kelas AnggaranHarian (logika bisnis)
├── setup_db_pengeluaran.py # Script setup database (jalankan sekali)
├── main_app.py             # UI Streamlit (file utama)
└── README.md               # File ini
```

## Cara Menjalankan di VSCode

### 1. Install dependensi
Buka terminal di VSCode (Ctrl+` atau Terminal > New Terminal), lalu jalankan:
```bash
pip install streamlit pandas
```

### 2. Setup database (jalankan SEKALI saja)
```bash
python setup_db_pengeluaran.py
```
Setelah ini, file `pengeluaran_harian.db` akan terbuat otomatis.

### 3. Jalankan aplikasi Streamlit
```bash
streamlit run main_app.py
```
Browser akan otomatis terbuka ke `http://localhost:8501`

---

## Fitur Aplikasi
- **➕ Tambah** — Form input pengeluaran baru
- **📋 Riwayat** — Lihat semua transaksi + **Hapus Transaksi** (fitur penugasan)
- **📊 Ringkasan** — Total & grafik per kategori, bisa filter tanggal

## Penugasan yang sudah diimplementasikan
Fitur **Hapus Transaksi** sudah ada di halaman Riwayat:
- `manajer_anggaran.py` → metode `hapus_transaksi(id_transaksi)`
- `main_app.py` → UI input ID + konfirmasi sebelum hapus
