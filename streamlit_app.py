import streamlit as st
import pandas as pd
import pymupdf
from PIL import Image, ImageFilter

# ==========================================
# 1. CONFIGURAÇÃO GERAL DA PÁGINA
# ==========================================
st.set_page_config(page_title="ScienceToolbox", layout="wide", page_icon="🔬")
st.title("ScienceToolbox")

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
    st.write("Altere a estrutura das suas matrizes entre os formatos Largo (Wide) e Longo (Long) para facilitar análises e plotagem em R ou Python.")
    
    # ------------------------------------------
    # EXEMPLOS VISUAIS PARA O USUÁRIO
    # ------------------------------------------
    st.write("### 🔍 Identifique o formato atual da sua tabela:")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.info("""
        **Formato Largo (Wide)**
        Metabólitos nas colunas, amostras nas linhas (ou vice-versa). Padrão de exportação de softwares de RMN.
        
        | Amostra | Acetato | Glicose |
        | :--- | :--- | :--- |
        | Animal_1 | 0.05 | 1.12 |
        | Animal_2 | 0.03 | 1.84 |
        """)
        
    with col_ex2:
        st.info("""
        **Formato Longo (Long)**
        Cada linha é uma observação única. Padrão exigido por pacotes como ggplot2 e MOFA+.
        
        | Amostra | Feature | Valor |
        | :--- | :--- | :--- |
        | Animal_1 | Acetato | 0.05 |
        | Animal_1 | Glicose | 1.12 |
        """)

    # ------------------------------------------
    # UPLOAD E PROCESSAMENTO
    # ------------------------------------------
    st.markdown("---")
    arquivo_csv = st.file_uploader("Suba sua tabela CSV", type=["csv"], key="csv_uploader")
    
    if arquivo_csv:
        # Usamos sep=None para ler tanto CSVs separados por vírgula quanto por ponto-e-vírgula
        df = pd.read_csv(arquivo_csv, sep=None, engine='python') 
        
        st.write("👀 **Prévia do arquivo carregado:**")
        st.dataframe(df.head(4))
        
        # O usuário escolhe o fluxo
        direcao = st.radio(
            "O que você deseja fazer?",
            ("🔄 Tenho Formato Largo ➡️ Quero transformar em Longo (Melt)", 
             "🔄 Tenho Formato Longo ➡️ Quero transformar em Largo (Pivot)")
        )
        
        if "Melt" in direcao:
            st.write("#### Configuração: Wide para Long")
            # Seleção múltipla para colunas de identificação
            colunas_id = st.multiselect(
                "Selecione a(s) coluna(s) de Identificação (ex: Sample, Label, Tecido) que NÃO vão virar linhas:", 
                df.columns
            )
            
            if st.button("Transformar para Longo"):
                if colunas_id:
                    try:
                        df_resultado = df.melt(id_vars=colunas_id, var_name="Feature", value_name="Valor")
                        st.success("✅ Conversão concluída!")
                        st.dataframe(df_resultado.head(10))
                        
                        csv_final = df_resultado.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Baixar CSV Longo", csv_final, "tabela_long.csv", "text/csv")
                    except Exception as e:
                        st.error(f"Erro ao processar: {e}")
                else:
                    st.warning("⚠️ Selecione pelo menos uma coluna de identificação para continuar.")
                    
        else:
            st.write("#### Configuração: Long para Wide")
            # Seleção específica das colunas para reconstruir a tabela
            coluna_index = st.selectbox("Qual coluna contém os Nomes das Amostras (ficarão nas linhas)?", df.columns, index=0)
            coluna_colunas = st.selectbox("Qual coluna contém os Metabólitos/Features (virarão novas colunas)?", df.columns, index=1 if len(df.columns) > 1 else 0)
            coluna_valores = st.selectbox("Qual coluna contém as intensidades/valores numéricos?", df.columns, index=2 if len(df.columns) > 2 else 0)
            
            if st.button("Transformar para Largo"):
                try:
                    # Usamos pivot_table com aggfunc='mean' para evitar erros caso existam valores duplicados acidentais para a mesma amostra/metabólito
                    df_resultado = df.pivot_table(index=coluna_index, columns=coluna_colunas, values=coluna_valores, aggfunc='mean').reset_index()
                    # Remove o nome da categoria das colunas para o CSV ficar mais limpo
                    df_resultado.columns.name = None 
                    
                    st.success("✅ Conversão concluída!")
                    st.dataframe(df_resultado.head(10))
                    
                    csv_final = df_resultado.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar CSV Largo", csv_final, "tabela_wide.csv", "text/csv")
                except Exception as e:
                    st.error(f"Erro ao organizar a tabela. Verifique se as colunas selecionadas estão corretas. Detalhe: {e}")

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
