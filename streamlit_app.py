import streamlit as st
import pandas as pd
import pymupdf
from PIL import Image, ImageFilter

# ==========================================
# 1. CONFIGURAÇÃO GERAL DA PÁGINA
# ==========================================
st.set_page_config(page_title="Ferramentas do Pesquisador", layout="wide", page_icon="🔬")
st.title("Ferramentas")

# ==========================================
# 2. CRIAÇÃO DAS ABAS DE NAVEGAÇÃO
# ==========================================
tab1, tab2, tab3 = st.tabs(["📄 Conversor PDF", "📊 Padronizador de Tabelas", "🧮 Calculadora Log2FC"])

# ==========================================
# 3. ABA 1: CONVERSOR DE PDF
# ==========================================
with tab1:
    st.header("Conversor de PDF para TIFF")
    st.info("""
    **Esta é a ferramenta ideal para figuras científicas:**
    - **Preservação de Integridade:** Utilizamos compressão *Lossless* (LZW) que não degrada a qualidade das bandas ou gráficos.
    - **Renderização de Precisão:** Mantemos a fidelidade vetorial dos PDFs, garantindo nitidez absoluta em 600 ou 1200 DPI.
    - **Otimização de Detalhes:** Incluímos um filtro inteligente de nitidez (*Sharpen*) que reforça as bordas de elementos gráficos complexos.
    - **Seus dados estão seguros:** O processamento ocorre localmente ou via memória volátil, não temos acesso algum ao seu material.
    """)

    # Upload do arquivo
    uploaded_file = st.file_uploader("Escolha seu PDF", type="pdf", key="pdf_uploader")

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
        if st.button("Converter PDF"):
            try:
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
                        st.download_button(f"📥 Baixar Página {i+1}", f, file_name=output_name, key=f"dl_btn_{i}")
            except Exception as e:
                st.error(f"Erro ao processar o PDF: {e}")

# ==========================================
# 4. ABA 2: PADRONIZADOR DE TABELAS (OMICS)
# ==========================================
with tab2:
    st.header("Padronizador de Tabelas Ômicas")
    st.write("Converta matrizes de metabólitos para o formato 'Long' em 1 clique. Ideal para análises sistêmicas e integrações.")
    
    arquivo_csv = st.file_uploader("Suba sua tabela CSV", type=["csv"], key="csv_uploader")
    
    if arquivo_csv:
        # Lê o CSV
        df = pd.read_csv(arquivo_csv, sep=None, engine='python') 
        
        st.write("👀 **Prévia do arquivo original:**")
        st.dataframe(df.head())
        
        formato = st.radio(
            "Como os dados estão organizados na sua tabela?",
            ("Metabólitos nas LINHAS (Ex: Coluna 1 = Acetate, Coluna 2 = PC1...)", 
             "Amostras nas LINHAS (Ex: Colunas 1 e 2 = Sample/Label, Coluna 3 = Acetate...)")
        )
        
        if st.button("Padronizar Tabela"):
            try:
                if "Metabólitos nas LINHAS" in formato:
                    # Formato 1: Pega a 1ª coluna como ID (ex: 'label')
                    col_id = df.columns[0] 
                    df_long = df.melt(id_vars=[col_id], var_name="Amostra", value_name="Valor")
                    df_long.rename(columns={col_id: "Metabolito"}, inplace=True)
                    
                else:
                    # Formato 2: Assume que as 2 primeiras colunas são Sample e Label
                    colunas_id = list(df.columns[0:2])
                    df_long = df.melt(id_vars=colunas_id, var_name="Metabolito", value_name="Valor")
                    df_long.rename(columns={colunas_id[0]: "Amostra", colunas_id[1]: "Grupo"}, inplace=True)

                st.write("✅ **Tabela Padronizada (Formato Long):**")
                st.dataframe(df_long.head())
                
                csv_final = df_long.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV Padronizado", csv_final, "tabela_padronizada_long.csv", "text/csv")
                
            except Exception as e:
                st.error(f"Erro ao padronizar. Verifique se a estrutura bate com a opção escolhida. Detalhe do erro: {e}")

# ==========================================
# 5. ABA 3: CALCULADORA LOG2FC
# ==========================================
with tab3:
    st.header("Calculadora Log2FC")
    st.info("Ferramenta em desenvolvimento. Em breve você poderá calcular Fold Changes rapidamente aqui.")

# ==========================================
# 6. RODAPÉ (APOIE O PROJETO)
# ==========================================
st.markdown("---")
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### Sobre o Projeto")
    st.write("""
    Cansado de receber *feedback* de revisores pedindo figuras com mais resolução? 
    Desenvolvi este conversor para que pesquisadores não percam tempo com conversores genéricos que demoram muito e com limitações de uso. 
    
    Aqui, você converte quantos arquivos quiser para **qualidade de publicação** de forma gratuita, rápida e, principalmente, mantendo a integridade científica dos seus dados.
    
    Se essa ferramenta economizou o seu tempo, considere apoiar o desenvolvimento de novas funcionalidades.
    Feito por um pesquisador para outros pesquisadores :) 
    """)

with col2:
    st.write("### Apoie o projeto")
    
    # Criamos colunas com alinhamento vertical centralizado
    subcol1, subcol2 = st.columns([0.3, 1], vertical_alignment="center")
    
    with subcol1:
        # O parâmetro use_container_width=True e a ausência de links internos 
        # impedem o comportamento de clique/zoom em navegadores modernos
        st.image("https://static.vecteezy.com/system/resources/thumbnails/050/735/542/small_2x/a-black-cat-sitting-on-a-table-with-a-blue-cup-of-coffee-free-video.jpg", width=100)
    
    with subcol2:
        st.link_button("☕ Pagar um café", "https://buymeacoffee.com/igorfernandost")
