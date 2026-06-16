# main_app.py
import streamlit as st
import datetime
import pandas as pd
import locale

try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except Exception:
        print("Locale id_ID/Indonesian tidak tersedia.")


def format_rp(angka):
    try:
        return locale.currency(angka or 0, grouping=True, symbol='Rp ')[:-3]
    except Exception:
        return f"Rp {angka or 0:,.0f}".replace(",", ".")


try:
    from model import Transaksi
    from manajer_anggaran import AnggaranHarian
    from konfigurasi import KATEGORI_PENGELUARAN
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan semua file .py ada di direktori yang sama.")
    st.stop()

st.set_page_config(page_title="Catatan Pengeluaran", layout="wide", initial_sidebar_state="expanded")


# --- Inisialisasi Pengelola Anggaran (Gunakan Cache) ---
@st.cache_resource
def get_anggaran_manager():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi AnggaranHarian...")
    return AnggaranHarian()


anggaran = get_anggaran_manager()


# =========================================================
# HALAMAN: Tambah Pengeluaran
# =========================================================
def halaman_input(anggaran: AnggaranHarian):
    st.header("💸 Tambah Pengeluaran Baru")
    with st.form("form_transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            deskripsi = st.text_input("Deskripsi*", placeholder="Contoh: Makan siang")
        with col2:
            kategori = st.selectbox("Kategori*:", KATEGORI_PENGELUARAN, index=0)
        col3, col4 = st.columns([1, 1])
        with col3:
            jumlah = st.number_input("Jumlah (Rp)*:", min_value=0.01, step=1000.0,
                                     format="%.0f", value=None, placeholder="Contoh: 25000")
        with col4:
            tanggal = st.date_input("Tanggal*:", value=datetime.date.today())
        submitted = st.form_submit_button("💾 Simpan Transaksi")
        if submitted:
            if not deskripsi:
                st.warning("Deskripsi wajib diisi!", icon="⚠️")
            elif jumlah is None or jumlah <= 0:
                st.warning("Jumlah wajib diisi dan harus lebih dari 0!", icon="⚠️")
            else:
                with st.spinner("Menyimpan..."):
                    tx = Transaksi(deskripsi, float(jumlah), kategori, tanggal)
                    if anggaran.tambah_transaksi(tx):
                        st.cache_data.clear()
                        st.toast("✅ Transaksi berhasil disimpan!", icon="✅")
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Gagal menyimpan transaksi.", icon="❌")


# =========================================================
# HALAMAN: Riwayat Transaksi (+ Fitur Hapus)
# =========================================================
def halaman_riwayat(anggaran: AnggaranHarian):
    st.subheader("📋 Detail Semua Transaksi")

    if st.button("🔄 Refresh Riwayat"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner("Memuat riwayat..."):
        df_transaksi = anggaran.get_dataframe_transaksi()

    if df_transaksi is None:
        st.error("Gagal mengambil data riwayat.")
        return
    elif df_transaksi.empty:
        st.info("Belum ada transaksi yang tercatat.")
        return

    st.dataframe(df_transaksi, use_container_width=True, hide_index=True)

    # -------------------------------------------------------
    # PENUGASAN: Fitur Hapus Transaksi
    # -------------------------------------------------------
    st.divider()
    st.subheader("🗑️ Hapus Transaksi")
    st.caption("Masukkan ID transaksi yang ingin dihapus (lihat kolom 'id' di tabel atas).")

    col_hapus1, col_hapus2 = st.columns([1, 2])
    with col_hapus1:
        id_hapus = st.number_input("ID Transaksi yang akan dihapus:", min_value=1, step=1, value=None,
                                   placeholder="Masukkan ID...")

    if id_hapus is not None:
        id_hapus = int(id_hapus)
        # Cek apakah ID ada di DataFrame
        id_list = df_transaksi['id'].tolist() if 'id' in df_transaksi.columns else []
        if id_hapus not in id_list:
            st.warning(f"ID {id_hapus} tidak ditemukan dalam daftar transaksi.", icon="⚠️")
        else:
            # Tampilkan data transaksi yang akan dihapus
            baris = df_transaksi[df_transaksi['id'] == id_hapus]
            st.warning(f"Anda akan menghapus transaksi berikut:", icon="⚠️")
            st.dataframe(baris, use_container_width=True, hide_index=True)

            # Tombol konfirmasi hapus
            if st.button(f"🗑️ Konfirmasi Hapus ID {id_hapus}", type="primary"):
                with st.spinner("Menghapus transaksi..."):
                    berhasil = anggaran.hapus_transaksi(id_hapus)
                if berhasil:
                    st.success(f"Transaksi ID {id_hapus} berhasil dihapus!", icon="✅")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Gagal menghapus transaksi ID {id_hapus}.", icon="❌")


# =========================================================
# HALAMAN: Ringkasan
# =========================================================
def halaman_ringkasan(anggaran: AnggaranHarian):
    st.subheader("📊 Ringkasan Pengeluaran")
    col_filter1, col_filter2 = st.columns([1, 2])

    with col_filter1:
        pilihan_periode = st.selectbox(
            "Filter Periode:",
            ["Semua Waktu", "Hari Ini", "Pilih Tanggal"],
            key="filter_periode",
            on_change=lambda: st.cache_data.clear()
        )

    tanggal_filter = None
    label_periode = "(Semua Waktu)"

    if pilihan_periode == "Hari Ini":
        tanggal_filter = datetime.date.today()
        label_periode = f"({tanggal_filter.strftime('%d %b %Y')})"
    elif pilihan_periode == "Pilih Tanggal":
        if 'tanggal_pilihan_state' not in st.session_state:
            st.session_state.tanggal_pilihan_state = datetime.date.today()
        tanggal_filter = st.date_input(
            "Pilih Tanggal:",
            value=st.session_state.tanggal_pilihan_state,
            key="tanggal_pilihan"
        )
        st.session_state.tanggal_pilihan_state = tanggal_filter
        label_periode = f"({tanggal_filter.strftime('%d %b %Y')})"

    with col_filter2:
        @st.cache_data(ttl=300)
        def hitung_total_cached(tgl_filter):
            return anggaran.hitung_total_pengeluaran(tanggal=tgl_filter)

        total_pengeluaran = hitung_total_cached(tanggal_filter)
        st.metric(label=f"Total Pengeluaran {label_periode}", value=format_rp(total_pengeluaran))

    st.divider()
    st.subheader(f"Pengeluaran per Kategori {label_periode}")

    @st.cache_data(ttl=300)
    def get_kategori_cached(tgl_filter):
        return anggaran.get_pengeluaran_per_kategori(tanggal=tgl_filter)

    with st.spinner("Memuat ringkasan kategori..."):
        dict_per_kategori = get_kategori_cached(tanggal_filter)

    if not dict_per_kategori:
        st.info("Tidak ada data pengeluaran untuk periode ini.")
    else:
        try:
            data_kategori = [{"Kategori": kat, "Total": jml} for kat, jml in dict_per_kategori.items()]
            df_kategori = pd.DataFrame(data_kategori).sort_values(by="Total", ascending=False).reset_index(drop=True)
            df_kategori['Total (Rp)'] = df_kategori['Total'].apply(format_rp)

            col_kat1, col_kat2 = st.columns(2)
            with col_kat1:
                st.write("**Tabel:**")
                st.dataframe(df_kategori[['Kategori', 'Total (Rp)']], hide_index=True, use_container_width=True)
            with col_kat2:
                st.write("**Grafik:**")
                st.bar_chart(df_kategori.set_index('Kategori')['Total'], use_container_width=True)
        except Exception as e:
            st.error(f"Gagal menampilkan ringkasan: {e}")


# =========================================================
# FUNGSI UTAMA
# =========================================================
def main():
    st.sidebar.title("💰 Catatan Pengeluaran Harian")
    menu_pilihan = st.sidebar.radio(
        "Pilih Menu:",
        ["➕ Tambah", "📋 Riwayat", "📊 Ringkasan"],
        key="menu_utama"
    )
    st.sidebar.markdown("---")
    st.sidebar.info("Jobsheet 11 - Integrasi OOP\nPemrograman Berorientasi Objek")

    manajer_anggaran = get_anggaran_manager()

    if menu_pilihan == "➕ Tambah":
        halaman_input(manajer_anggaran)
    elif menu_pilihan == "📋 Riwayat":
        halaman_riwayat(manajer_anggaran)
    elif menu_pilihan == "📊 Ringkasan":
        halaman_ringkasan(manajer_anggaran)

    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP | Politeknik Negeri Semarang")


if __name__ == "__main__":
    main()
