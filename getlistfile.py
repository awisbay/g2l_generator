import streamlit as st
import os
import datetime

# Fungsi untuk mendapatkan daftar file dan informasi tambahan
def get_file_list_with_info(folder_path):
    files_info = []
    # Pastikan folder_path adalah direktori yang valid
    if os.path.isdir(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # Hanya tambahkan jika itu adalah file (bukan sub-direktori)
            if os.path.isfile(item_path):
                # Dapatkan ukuran file (dalam bytes)
                file_size_bytes = os.path.getsize(item_path)
                # Konversi ke KB, MB, atau GB untuk tampilan yang lebih mudah dibaca
                if file_size_bytes < 1024:
                    file_size = f"{file_size_bytes} bytes"
                elif file_size_bytes < 1024 * 1024:
                    file_size = f"{file_size_bytes / 1024:.2f} KB"
                elif file_size_bytes < 1024 * 1024 * 1024:
                    file_size = f"{file_size_bytes / (1024 * 1024):.2f} MB"
                else:
                    file_size = f"{file_size_bytes / (1024 * 1024 * 1024):.2f} GB"

                # Dapatkan waktu modifikasi terakhir. Untuk sebagian besar sistem, ini seringkali
                # cukup mendekati waktu pembuatan file baru. Jika Anda butuh waktu pembuatan mutlak,
                # gunakan os.path.getctime() di sistem Unix/Linux atau stat().st_birthtime di macOS
                # dan Windows (dengan catatan berbeda interpretasi). Untuk kasus umum, getmtime lebih universal.
                timestamp = os.path.getmtime(item_path)
                date_modified = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

                files_info.append({
                    'name': item,
                    'size': file_size,
                    'date': date_modified # Mengganti 'date_created' menjadi 'date_modified' karena menggunakan getmtime
                })
    return files_info


def file_list_page_download_only():
    st.title("RNC Modump Download")

    # Tentukan jalur absolut ke folder yang ingin Anda tampilkan filenya.
    # Ganti '<user>' dengan nama pengguna yang sebenarnya di server Anda.
    # Contoh: /home/namauser/Documents
    folder_to_scan = "/home/ftpwisbay/log/ModumpRNC" # <--- GANTI INI DENGAN PATH ABSOLUT YANG BENAR

    # Tombol Refresh
    if st.button("Refresh Folder"):
        st.rerun() # Memaksa aplikasi untuk menjalankan ulang dan memuat ulang daftar file

    # Memastikan folder ada dan dapat diakses sebelum mencoba memindai
    if not os.path.isdir(folder_to_scan):
        st.error(f"Directory Not Found: `{folder_to_scan}`")
        st.stop() # Hentikan eksekusi Streamlit jika direktori tidak valid

    files_info = get_file_list_with_info(folder_to_scan)

    if files_info:
        #st.success(f"Ditemukan {len(files_info)} file di: `{folder_to_scan}`")
        st.markdown("---")

        # Struktur Kolom: Nama File | Ukuran | Tanggal Modifikasi | Download
        # Kita mengurangi jumlah kolom karena tidak ada lagi tombol Delete
        col1, col2, col3, col4 = st.columns([0.4, 0.1, 0.3, 0.2]) # Sesuaikan lebar kolom

        with col1:
            st.markdown("**File**")
        with col2:
            st.markdown("**Size**")
        with col3:
            st.markdown("**Date Modified**")
        st.divider()

        for file_data in files_info:
            file_path = os.path.join(folder_to_scan, file_data['name'])

            # Kolom untuk setiap baris file
            col1_file, col2_size, col3_date, col4_download = st.columns([0.4, 0.1, 0.3, 0.2])

            with col1_file:
                st.write(file_data['name'])
            with col2_size:
                st.write(file_data['size'])
            with col3_date:
                st.write(file_data['date'])

            with col4_download:
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="Download",
                        data=file.read(),
                        file_name=file_data['name'],
                        mime="application/octet-stream",
                        key=f"download_btn_{file_data['name']}" # Kunci unik untuk setiap tombol
                    )
    else:
        st.warning(f"No files inside folder: `{folder_to_scan}`.")

if __name__ == "__main__":
    file_list_page_download_only()