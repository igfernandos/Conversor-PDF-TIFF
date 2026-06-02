import streamlit as st
import pymupdf
from PIL import Image, ImageFilter

# Configuração da página
st.set_page_config(page_title="Conversor PDF para TIFF", page_icon="📄")
st.title("Conversor de PDF para TIFF (Alta Qualidade)")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha seu PDF", type="pdf")

# Configurações de DPI e Nitidez
dpi = st.slider("Selecione o DPI", 300, 1200, 600)
otimizar = st.checkbox("Aplicar filtros de nitidez", value=True)

if uploaded_file is not None:
    if st.button("Converter"):
        # Abre o PDF na memória
        doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            fator = dpi / 72.0
            pix = page.get_pixmap(matrix=pymupdf.Matrix(fator, fator))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Filtro de nitidez (se ativado)
            if otimizar:
                img = img.filter(ImageFilter.SHARPEN).filter(ImageFilter.EDGE_ENHANCE)
            
            # Salva na memória
            output_name = f"pag_{i+1}_{dpi}dpi.tiff"
            img.save(output_name, format="TIFF", dpi=(dpi, dpi), compression="tiff_lzw")
            
            # Botão de download para o usuário
            with open(output_name, "rb") as f:
                st.download_button(f"Baixar Página {i+1}", f, file_name=output_name)