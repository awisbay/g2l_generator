module.exports = {
  apps : [{
    name   : "irsteam-app", // Nama aplikasi di PM2
    script : "/var/www/irsmigration/.g2lvenv/bin/streamlit", // Path ke executable streamlit di venv
    args   : "run main_page.py --server.port 8501 --server.headless true", // Argumen untuk streamlit
    cwd    : "/var/www/irsmigration", // Direktori kerja (lokasi main_page.py)
    interpreter: "none", // PENTING: Beritahu PM2 untuk tidak menggunakan interpreter (seperti Node.js)
    exec_mode: "fork"   // Mode eksekusi standar
  }]
}
