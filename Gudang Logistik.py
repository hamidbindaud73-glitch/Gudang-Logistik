import streamlit as st
import json
import os

FILE_DATABASE = "data_gudang_penyimpanan.json"

def perbarui_database():
    data_simpanan = {
        "inventaris": st.session_state.inventaris,
        "antrean_kendaraan": st.session_state.antrean_kendaraan,
        "log_aktivitas": st.session_state.log_aktivitas
    }
    with open(FILE_DATABASE, "w") as berkas:
        json.dump(data_simpanan, berkas)

def inisialisasi_data():
    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, "r") as berkas:
                data = json.load(berkas)
                st.session_state.inventaris = data.get("inventaris", {})
                st.session_state.antrean_kendaraan = data.get("antrean_kendaraan", [])
                st.session_state.log_aktivitas = data.get("log_aktivitas", [])
        except:
            pass

# Menyiapkan Session State di Awal
if 'inventaris' not in st.session_state:
    inisialisasi_data()
    if 'inventaris' not in st.session_state:
        st.session_state.inventaris = {}
        st.session_state.antrean_kendaraan = []
        st.session_state.log_aktivitas = []

# --- PENGATURAN ANTARMUKA (UI) ---
st.set_page_config(page_title="Sistem Manajemen Gudang", layout="wide")
st.title("Sistem Operasional & Logistik Gudang")
st.markdown("*Aplikasi pengelolaan akumulasi stok barang dan pemrosesan muatan truk.*")

# --- BAGIAN SIDEBAR UNTUK INPUT ---
st.sidebar.header("⚙️ Menu Operasional")
st.sidebar.subheader("Input Barang Baru")
with st.sidebar.form("form_input_barang"):
    nama_item = st.text_input("Nama Barang")
    jumlah_item = st.number_input("Kuantitas Masuk", min_value=1, step=1)
    tombol_simpan = st.form_submit_button("Tambahkan ke Inventaris")
    
    if tombol_simpan:
        if nama_item.strip():
            stok_sebelumnya = st.session_state.inventaris.get(nama_item, 0)
            st.session_state.inventaris[nama_item] = stok_sebelumnya + jumlah_item
            
            st.session_state.log_aktivitas.append(('INPUT', nama_item, jumlah_item))
            perbarui_database()
            st.success(f"Item {nama_item} berhasil ditambahkan sebanyak {jumlah_item}.")
        else:
            st.error("Nama barang tidak boleh kosong!")

st.sidebar.divider()

# Modul Antrean Truk beserta Detail Muatan yang Akan Diambil
st.sidebar.subheader("🚚 Registrasi Truk & Rencana Muatan")
id_truk = st.sidebar.text_input("Plat Nomor / ID Truk")

# Menggunakan selectbox dari barang yang ada di inventaris agar operator mudah memilih
pilihan_barang = list(st.session_state.inventaris.keys())
if not pilihan_barang:
    barang_diangkut = st.sidebar.text_input("Barang yang Akan Diangkut (Ketik Manual)")
else:
    barang_diangkut = st.sidebar.selectbox("Pilih Barang yang Akan Diangkut", pilihan_barang)

jumlah_diangkut = st.sidebar.number_input("Jumlah yang Akan Diangkut", min_value=1, step=1)

if st.sidebar.button("Masukan ke Antrean Parkir"):
    if id_truk.strip() and barang_diangkut:
        # Menyimpan data truk dalam bentuk objek/dictionary agar lengkap
        data_truk = {
            "id": id_truk.strip(),
            "barang": barang_diangkut,
            "jumlah": jumlah_diangkut
        }
        st.session_state.antrean_kendaraan.append(data_truk)
        perbarui_database()
        st.sidebar.success(f"Truk {id_truk} antre untuk mengangkut {jumlah_diangkut} {barang_diangkut}.")
    else:
        st.sidebar.warning("Harap isi ID Truk dan Nama Barang dengan benar!")

st.sidebar.divider()

# Modul Aksi Lanjutan (Batal & Proses)
st.sidebar.subheader("Aksi Cepat")
kolom_kiri, kolom_kanan = st.sidebar.columns(2)

if kolom_kiri.button("Undo / Batal Masuk"):
    if st.session_state.log_aktivitas:
        aksi, nama_target, qty_target = st.session_state.log_aktivitas.pop()
        if aksi == 'INPUT':
            if nama_target in st.session_state.inventaris:
                st.session_state.inventaris[nama_target] -= qty_target
                if st.session_state.inventaris[nama_target] <= 0:
                    st.session_state.inventaris.pop(nama_target)
        perbarui_database()
        st.sidebar.success("Pembatalan stok masuk berhasil.")
    else:
        st.sidebar.info("Tidak ada riwayat input barang untuk dibatalkan.")

if kolom_kanan.button("Proses Truk (Pergi)"):
    if st.session_state.antrean_kendaraan:
        # Mengambil truk urutan pertama (FIFO)
        truk_keluar = st.session_state.antrean_kendaraan.pop(0)
        
        truk_id = truk_keluar["id"]
        truk_barang = truk_keluar["barang"]
        truk_jumlah = truk_keluar["jumlah"]
        
        # [FITUR BARU]: Otomatis memotong/mengupdate stok di gudang saat truk diproses
        if truk_barang in st.session_state.inventaris:
            stok_sekarang = st.session_state.inventaris[truk_barang]
            sisa_stok = stok_sekarang - truk_jumlah
            
            if sisa_stok <= 0:
                st.session_state.inventaris.pop(truk_barang) # Hapus dari rak jika habis
                st.sidebar.success(f"Truk {truk_id} pergi. Barang '{truk_barang}' di gudang sekarang HABIS.")
            else:
                st.session_state.inventaris[truk_barang] = sisa_stok
                st.sidebar.success(f"Truk {truk_id} berhasil memuat {truk_jumlah} {truk_barang} dan meninggalkan gudang.")
        else:
            st.sidebar.warning(f"Truk {truk_id} diproses, namun '{truk_barang}' tidak ditemukan di inventaris gudang.")
            
        perbarui_database()
    else:
        st.sidebar.error("Tidak ada truk di area parkir.")

# --- BAGIAN UTAMA (DASHBOARD) ---
kolom_kiri_utama, kolom_kanan_utama = st.columns([1.3, 1])

with kolom_kiri_utama:
    st.subheader("Daftar Real-Time Inventaris Gudang")
    
    # Fitur Pencarian Cepat
    kata_kunci = st.text_input("Cari Barang...", placeholder="Masukan nama barang di sini...")
    if kata_kunci:
        hasil_pencarian = st.session_state.inventaris.get(kata_kunci)
        if hasil_pencarian is not None:
            st.info(f"Stok saat ini untuk **{kata_kunci}**: **{hasil_pencarian}** unit.")
        else:
            st.warning("Barang tidak ada di dalam rak gudang.")
    
    # Menampilkan Tabel Inventaris
    if st.session_state.inventaris:
        data_tabel = [{"Nama Item": nama, "Total Stok Tersedia": qty} for nama, qty in st.session_state.inventaris.items()]
        st.dataframe(data_tabel, use_container_width=True)
    else:
        st.caption("Gudang kosong. Belum ada stok barang yang dimasukkan.")

with kolom_kanan_utama:
    st.subheader("Urutan Antrean Truk & Target Muatan")
    if st.session_state.antrean_kendaraan:
        for nomor, data_truk in enumerate(st.session_state.antrean_kendaraan, start=1):
            # Menampilkan detail truk beserta barang & jumlah yang akan diangkut
            st.markdown(f"**{nomor}.** Plat/ID: **{data_truk['id']}**")
            st.caption(f"↳ *Rencana Muat: {data_truk['jumlah']} unit x [{data_truk['barang']}]*")
    else:
        st.caption("Area parkir kosong. Semua kendaraan sudah diproses.")
