import streamlit as st
from drive_parser import parse_drive_folders
import requests

folder_id = st.text_input("ID de carpeta de Google Drive", "12mvWd_ppV1mHr0GRoaArAqTWYXopTAWt")
if st.button("Ver estructura de la carpeta"):
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    page = requests.get(url, timeout=20).text
    parsed = parse_drive_folders(page)
    st.write(parsed)
    st.write("IDs únicos:", [e['id'] for e in parsed])
    st.write("Títulos únicos:", [e['title'] for e in parsed])
    st.write("is_folder:", [e['is_folder'] for e in parsed])
    st.write("Links:", [e['link'] for e in parsed])
