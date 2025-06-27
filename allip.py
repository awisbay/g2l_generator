import streamlit as st
import os
import datetime

# Fungsi untuk mendapatkan daftar file dan informasi tambahan
def get_file_list_with_info(folder_path):
    files_info = []
    if os.path.isdir(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
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

                # Dapatkan waktu modifikasi terakhir (yang seringkali sama dengan waktu pembuatan untuk file baru)
                timestamp = os.path.getmtime(item_path)
                date_created = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

                files_info.append({
                    'name': item,
                    'size': file_size,
                    'date': date_created
                })
    return files_info

# ---
# Halaman Daftar File dengan Aksi dan Informasi Tambahan
def file_list_actions_page():
    st.title("Allip LOG")
    st.markdown("---")

    folder_to_scan = "/home/ftpwisbay/log/bscallip" # <--- GANTI INI DENGAN PATH ABSOLUT YANG BENAR

    # Inisialisasi Session State untuk Konfirmasi
    if 'file_to_delete' not in st.session_state:
        st.session_state.file_to_delete = None

    # Tombol Refresh
    if st.button("Refresh Folder"):
        st.session_state.file_to_delete = None
        st.rerun()

    if not os.path.isdir(folder_to_scan):
        st.error(f"Directory not found: `{folder_to_scan}`")
        st.stop()

    files_info = get_file_list_with_info(folder_to_scan)

    if files_info:
        #st.success(f"Ditemukan {len(files_info)} file di: `{folder_to_scan}`")
        st.markdown("---")

        # Struktur Kolom: Nama File | Ukuran | Tanggal Dibuat | Download | Delete
        col1, col2, col3, col4, col5 = st.columns([0.4, 0.2, 0.2, 0.15, 0.15]) # Sesuaikan lebar kolom

        with col1:
            st.write("**File Name**")
        with col2:
            st.write("**Size**")
        with col3:
            st.write("**Date Created**")
        with col4:
            st.write("**Download**")
        with col5:
            st.write("**Delete**")
        st.markdown("---")

        for file_data in files_info:
            file_path = os.path.join(folder_to_scan, file_data['name'])

            col1_file, col2_size, col3_date, col4_download, col5_delete = st.columns([0.4, 0.2, 0.2, 0.15, 0.15])

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
                        key=f"download_btn_{file_data['name']}"
                    )

            with col5_delete:
                # Logika Konfirmasi Delete (tetap sama)
                if st.session_state.file_to_delete == file_data['name']:
                    confirm_col, cancel_col = st.columns(2)
                    with confirm_col:
                        if st.button("Yes", key=f"confirm_delete_{file_data['name']}", help="Click for deletion confirmation."):
                            try:
                                os.remove(file_path)
                                st.success(f"File '{file_data['name']}' is deleted.")
                                st.session_state.file_to_delete = None
                                st.rerun()
                            except OSError as e:
                                st.error(f"Failed to delete '{file_data['name']}': {e}")
                    with cancel_col:
                        if st.button("No", key=f"cancel_delete_{file_data['name']}", help="Click for cancel deletion."):
                            st.session_state.file_to_delete = None
                            st.rerun()
                else:
                    if st.button("Delete", key=f"delete_btn_{file_data['name']}"):
                        st.session_state.file_to_delete = file_data['name']
                        st.warning(f"Are you sure to delete '{file_data['name']}'? Click Confirm.")
                        st.rerun()
    else:
        st.warning(f"No file in folder: `{folder_to_scan}`.")
        #st.info("Pastikan jalur direktori sudah benar dan aplikasi Streamlit memiliki izin akses untuk membaca/menulis direktori tersebut.")

# ---
# Jalankan Aplikasi Streamlit
if __name__ == "__main__":
    file_list_actions_page()