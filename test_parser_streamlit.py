import streamlit as st
from drive_parser import parse_drive_folders
import requests

folder_id = st.text_input("ID de carpeta de Google Drive", "12mvWd_ppV1mHr0GRoaArAqTWYXopTAWt")
if st.button("Probar parser y mostrar entradas"):
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    page = requests.get(url, timeout=20).text
    parsed = parse_drive_folders(page)
    st.write(f"Entradas parseadas: {len(parsed)}")
    for entry in parsed:
        st.write(entry)
