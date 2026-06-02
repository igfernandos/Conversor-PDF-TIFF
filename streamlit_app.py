import streamlit as st
import pymupdf
from PIL import Image, ImageFilter

# Configuração da página
st.set_page_config(page_title="Conversor PDF para TIFF", page_icon="📄")
st.title("Conversor de PDF para TIFF")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha seu PDF", type="pdf")

# Configurações de DPI e Nitidez
st.write("### Configurações de Qualidade")

# Opções de clique (radio buttons)
opcao_dpi = st.radio(
    "Escolha o DPI padrão:",
    (300, 600, 1200),
    index=1, # O índice 1 é o 600
    horizontal=True
)

# Opção de digitação (caso queiram algo específico)
custom_dpi = st.number_input(
    "Ou digite um valor personalizado:", 
    min_value=72, 
    max_value=2400, 
    value=opcao_dpi
)

# O DPI que será usado no script:
dpi = custom_dpi
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
