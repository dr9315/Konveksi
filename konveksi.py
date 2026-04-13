import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Keuangan Konveksi", layout="wide")

# Inisialisasi session state untuk menyimpan data jika belum ada
if 'transaksi_data' not in st.session_state:
    st.session_state.transaksi_data = pd.DataFrame(columns=[
        "Tanggal", "Keterangan", "Pihak Terkait", "Kategori", "Nominal"
    ])

# --- FUNGSI HELPER ---
def format_rupiah(nominal):
    return f"Rp {nominal:,.0f}".replace(",", ".")

# --- UI UTAMA ---
st.title("🧵 Sistem Pencatatan Keuangan Konveksi")
st.info("Mode Testing: Data tersimpan sementara di memori browser.")

# --- BAGIAN INPUT (FORM) ---
with st.expander("➕ Tambah Transaksi Baru", expanded=True):
    with st.form("form_transaksi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tgl = st.date_input("Tanggal Transaksi", datetime.now())
            kategori = st.radio("Kategori", ["Debit (Masuk)", "Kredit (Keluar)"])
            nominal = st.number_input("Nominal (Rupiah)", min_value=0, step=1000)
            
        with col2:
            keterangan = st.text_input("Jenis Transaksi (Contoh: DP Jahit, Beli Kain)")
            pihak = st.text_input("Dari Pihak Siapa (Contoh: Nama Pelanggan/Supplier)")
            
        submit_button = st.form_submit_button("Simpan Transaksi")

        if submit_button:
            if keterangan and pihak and nominal > 0:
                new_data = pd.DataFrame([{
                    "Tanggal": tgl,
                    "Keterangan": keterangan,
                    "Pihak Terkait": pihak,
                    "Kategori": kategori,
                    "Nominal": nominal
                }])
                st.session_state.transaksi_data = pd.concat([st.session_state.transaksi_data, new_data], ignore_index=True)
                st.success("Transaksi berhasil dicatat!")
            else:
                st.error("Mohon isi semua field dengan benar.")

# --- BAGIAN FILTER & AKUMULASI ---
st.divider()
st.subheader("📊 Laporan & Akumulasi")

if not st.session_state.transaksi_data.empty:
    # Filter Tanggal Dinamis
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        rentang = st.selectbox("Pilih Rentang Waktu", ["Semua", "10 Hari Terakhir", "30 Hari Terakhir", "Custom"])
        
        # Logika Filter
        today = datetime.now().date()
        df = st.session_state.transaksi_data.copy()
        df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date

        if rentang == "10 Hari Terakhir":
            df = df[df['Tanggal'] >= (today - timedelta(days=10))]
        elif rentang == "30 Hari Terakhir":
            df = df[df['Tanggal'] >= (today - timedelta(days=30))]
        elif rentang == "Custom":
            start_date = st.date_input("Mulai", today - timedelta(days=7))
            end_date = st.date_input("Sampai", today)
            df = df[(df['Tanggal'] >= start_date) & (df['Tanggal'] <= end_date)]

    # Perhitungan Akumulasi
    total_debit = df[df['Kategori'] == "Debit (Masuk)"]['Nominal'].sum()
    total_kredit = df[df['Kategori'] == "Kredit (Keluar)"]['Nominal'].sum()
    saldo_akhir = total_debit - total_kredit

    # Display Ringkasan Angka (User Friendly)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Debit", format_rupiah(total_debit))
    c2.metric("Total Kredit", format_rupiah(total_kredit))
    c3.metric("Saldo Akumulasi", format_rupiah(saldo_akhir), delta_color="normal")

    # Tabel Data
    st.dataframe(df, use_container_width=True)

    # Fitur Download (Karena belum ada DB, ini penting agar data bisa disimpan ke Excel)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Laporan (CSV)", data=csv, file_name=f"laporan_keuangan_{today}.csv", mime="text/csv")

else:
    st.warning("Belum ada data transaksi. Silakan isi form di atas.")