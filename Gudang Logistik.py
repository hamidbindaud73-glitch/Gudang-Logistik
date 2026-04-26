import streamlit as st
import json
import os

# --- KONFIGURASI FILE & PENYIMPANAN ---
DATA_FILE = "database_gudang.json"

def save_data():
    """Menyimpan data dari session_state ke file JSON agar permanen"""
    data = {
        "stok": st.session_state.stok,
        "antrean": st.session_state.antrean,
        "history": st.session_state.history
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    """Memuat data dari file JSON saat aplikasi pertama kali dibuka"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                st.session_state.stok = data.get("stok", {})
                st.session_state.antrean = data.get("antrean", [])
                st.session_state.history = data.get("history", [])
        except Exception:
            # Jika file korup atau kosong, mulai dengan data baru
            pass

# --- INISIALISASI SESSION STATE ---
if 'stok' not in st.session_state:
    load_data()
    # Jika setelah load tetap belum ada (file baru), buat defaultnya
    if 'stok' not in st.session_state:
        st.session_state.stok = {}
        st.session_state.antrean = []
        st.session_state.history = []

# --- TAMPILAN ANTARMUKA (UI) ---
st.set_page_config(page_title="Bakti Gudang Dashboard", layout="wide")
st.title("🚛 Dashboard Logistik 'Bakti Gudang' v1.0")
st.info("Sistem ini mengelola inventaris (O(1) Search) dan antrean truk (FIFO).")

# --- PANEL OPERATOR (SIDEBAR) ---
st.sidebar.header("🕹️ Panel Kontrol Operator")

# 1. Fitur TAMBAH STOK
with st.sidebar.expander("📦 Tambah Persediaan (TAMBAH)"):
    with st.form("form_tambah"):
        nama_brg = st.text_input("Nama Barang")
        jumlah_brg = st.number_input("Jumlah", min_value=1, step=1)
        submit_tambah = st.form_submit_button("Simpan ke Rak")
        
        if submit_tambah:
            if nama_brg:
                st.session_state.stok[nama_brg] = st.session_state.stok.get(nama_brg, 0) + jumlah_brg
                st.session_state.history.append(('TAMBAH', nama_brg, jumlah_brg))
                save_data() # Simpan ke JSON
                st.success(f"Berhasil mencatat {nama_brg}")
            else:
                st.error("Nama barang wajib diisi!")

# 2. Fitur ANTRE KENDARAAN
with st.sidebar.expander("🚚 Antrean Truk (ANTRE)"):
    nama_truk = st.text_input("ID/Nama Truk")
    if st.sidebar.button("Daftarkan ke Parkir"):
        if nama_truk:
            st.session_state.antrean.append(nama_truk)
            save_data() # Simpan ke JSON
            st.sidebar.success(f"{nama_truk} masuk antrean.")
        else:
            st.sidebar.warning("Isi nama truk!")

# 3. Fitur PROSES & BATAL
st.sidebar.markdown("---")
col_b, col_p = st.sidebar.columns(2)

if col_b.button("⚠️ BATAL"):
    if st.session_state.history:
        jenis, nama, jml = st.session_state.history.pop()
        if jenis == 'TAMBAH':
            st.session_state.stok[nama] -= jml
            if st.session_state.stok[nama] <= 0:
                del st.session_state.stok[nama]
        save_data()
        st.sidebar.warning("Input terakhir dibatalkan.")
    else:
        st.sidebar.info("Tidak ada riwayat.")

if col_p.button("✅ PROSES"):
    if st.session_state.antrean:
        truk_masuk = st.session_state.antrean.pop(0) # FIFO
        save_data()
        st.sidebar.success(f"{truk_masuk} diproses.")
    else:
        st.sidebar.error("Antrean kosong.")

# --- DISPLAY UTAMA ---
col_stok, col_truk = st.columns([3, 2])

with col_stok:
    st.subheader("📋 Audit Stok Barang")
    # Fitur CARI (O(1))
    cari = st.text_input("Cari Barang Cepat...", placeholder="Ketik nama untuk cek stok...")
    if cari:
        hasil = st.session_state.stok.get(cari)
        if hasil is not None:
            st.success(f"Ditemukan! Stok **{cari}**: {hasil}")
        else:
            st.error(f"Barang '{cari}' tidak ada di sistem.")
    
    # Tabel Inventaris
    if st.session_state.stok:
        st.table([{"Barang": k, "Jumlah": v} for k, v in st.session_state.stok.items()])
    else:
        st.write("Belum ada data stok.")

with col_truk:
    st.subheader("🛣️ Urutan Parkir Truk")
    if st.session_state.antrean:
        for idx, t in enumerate(st.session_state.antrean):
            st.write(f"{idx+1}. 🚛 **{t}**")
    else:
        st.write("Area parkir kosong.")
