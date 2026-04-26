import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Logistik Bakti Gudang", layout="wide")

# --- INITIALIZATION (Agar data tidak hilang saat refresh) ---
if 'stok' not in st.session_state:
    st.session_state.stok = {}
if 'antrean' not in st.session_state:
    st.session_state.antrean = []
if 'history' not in st.session_state:
    st.session_state.history = []

# --- JUDUL APLIKASI ---
st.title("🚛 Dashboard Logistik 'Bakti Gudang' v1.0")
st.markdown("---")

# --- SIDEBAR UNTUK INPUT (OPERATOR) ---
st.sidebar.header("Panel Operator")

# Fitur TAMBAH
with st.sidebar.expander("📦 Pencatatan Persediaan (TAMBAH)"):
    nama_barang = st.text_input("Nama Barang", key="txt_barang")
    jumlah_barang = st.number_input("Jumlah", min_value=1, step=1)
    if st.button("Tambah ke Stok"):
        if nama_barang:
            # Update Stok
            st.session_state.stok[nama_barang] = st.session_state.stok.get(nama_barang, 0) + jumlah_barang
            # Simpan History untuk BATAL
            st.session_state.history.append(('TAMBAH', nama_barang, jumlah_barang))
            st.success(f"{nama_barang} sejumlah {jumlah_barang} berhasil dicatat.")
        else:
            st.error("Nama barang tidak boleh kosong!")

# Fitur ANTRE
with st.sidebar.expander("🚚 Registrasi Kendaraan (ANTRE)"):
    nama_truk = st.text_input("Nama Truk")
    if st.button("Daftarkan Truk"):
        if nama_truk:
            st.session_state.antrean.append(nama_truk)
            st.success(f"Truk {nama_truk} masuk antrean.")
        else:
            st.error("Nama truk tidak boleh kosong!")

# Fitur BATAL & PROSES
st.sidebar.markdown("---")
col_batal, col_proses = st.sidebar.columns(2)

if col_batal.button("⚠️ BATAL INPUT"):
    if st.session_state.history:
        jenis, nama, jumlah = st.session_state.history.pop()
        if jenis == 'TAMBAH':
            st.session_state.stok[nama] -= jumlah
            if st.session_state.stok[nama] <= 0:
                del st.session_state.stok[nama]
        st.warning("Input terakhir telah dibatalkan.")
    else:
        st.info("Tidak ada riwayat.")

if col_proses.button("✅ PROSES TRUK"):
    if st.session_state.antrean:
        truk_keluar = st.session_state.antrean.pop(0) # FIFO
        st.sidebar.balloons()
        st.sidebar.info(f"{truk_keluar} dipersilakan masuk.")
    else:
        st.sidebar.error("Antrean kosong!")

# --- DASHBOARD UTAMA (TAMPILAN DOSEN) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Daftar Stok (Audit Stok)")
    # Fitur CARI (O(1) search di balik layar Streamlit)
    search_query = st.text_input("Cari Barang Cepat...", placeholder="Ketik nama barang...")
    
    if search_query:
        if search_query in st.session_state.stok:
            st.info(f"Stok **{search_query}** saat ini: **{st.session_state.stok[search_query]}**")
        else:
            st.error("Barang tidak ditemukan.")
    
    # Menampilkan tabel stok
    if st.session_state.stok:
        st.table([{"Nama Barang": k, "Jumlah": v} for k, v in st.session_state.stok.items()])
    else:
        st.write("Gudang kosong.")

with col2:
    st.subheader("🛣️ Urutan Antrean Truk")
    if st.session_state.antrean:
        for i, truk in enumerate(st.session_state.antrean):
            st.write(f"{i+1}. 🚛 **{truk}**")
    else:
        st.write("Tidak ada antrean truk.")

# Tombol Keluar (Hanya simulasi di Web)
if st.button("KELUAR"):
    st.write("Sistem berhenti. Silakan tutup tab browser ini.")