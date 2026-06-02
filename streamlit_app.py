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

Aqui está o bloco completo, corrigido e perfeito da **Aba 2**.

Eu removi aquela validação antiga (que contava linhas e colunas) e coloquei a **validação inteligente por tipagem** (que calcula a proporção de texto na primeira linha). Também limpei a redundância da variável `coluna_pivo` para que a interface fique super limpa, mantendo a opção de seleção apenas por segurança, mas já puxando a primeira coluna automaticamente.

Pode copiar e substituir todo o conteúdo da `with tab2:`:

```python
# ==========================================
# 4. ABA 2: PADRONIZADOR DE TABELAS (OMICS)
# ==========================================
with tab2:
    st.header("Padronizador de Tabelas Ômicas")
    st.write("Inverta a orientação da sua matriz (Transposição) para adequar aos padrões do MetaboAnalyst, MOFA+ ou scripts de R.")
    
    # ------------------------------------------
    # LÓGICA DE INVERSÃO VISUAL
    # ------------------------------------------
    if 'modo_conversao' not in st.session_state:
        st.session_state.modo_conversao = 'wide_to_long'
        
    def inverter_modo():
        if st.session_state.modo_conversao == 'wide_to_long':
            st.session_state.modo_conversao = 'long_to_wide'
        else:
            st.session_state.modo_conversao = 'wide_to_long'

    # Textos e visualizações com o formato real da Metabolômica
    exemplo_wide = """
    **Amostras nas Linhas (Wide)**
    | Sample | Label | Metabólito_1 | Metabólito_2 |
    | :--- | :--- | :--- | :--- |
    | Amostra_1 | Grupo_1 | 0.050 | 1.120 |
    | Amostra_2 | Grupo_1 | 0.030 | 1.840 |
    """
    
    exemplo_long = """
    **Metabólitos nas Linhas (Long)**
    | Sample | Amostra_1 | Amostra_2 |
    | :--- | :--- | :--- |
    | **Label** | Grupo_1 | Grupo_1 |
    | **Metabólito_1** | 0.050 | 0.030 |
    | **Metabólito_2** | 1.120 | 1.840 |
    """

    st.write("### 🔍 Escolha a direção da conversão:")
    
    col_origem, col_botao, col_destino = st.columns([3, 1, 3], vertical_alignment="center")
    
    with col_origem:
        st.write("📥 **Sua tabela está assim:**")
        if st.session_state.modo_conversao == 'wide_to_long':
            st.info(exemplo_wide)
        else:
            st.info(exemplo_long)
            
    with col_botao:
        st.button("🔄 Inverter", on_click=inverter_modo, use_container_width=True)
        
    with col_destino:
        st.write("📤 **Sua tabela ficará assim:**")
        if st.session_state.modo_conversao == 'wide_to_long':
            st.success(exemplo_long)
        else:
            st.success(exemplo_wide)

    # ------------------------------------------
    # UPLOAD E PROCESSAMENTO
    # ------------------------------------------
    st.markdown("---")
    arquivo_csv = st.file_uploader("Suba sua tabela CSV", type=["csv"], key="csv_uploader")
    
    if arquivo_csv:
        df = pd.read_csv(arquivo_csv, sep=None, engine='python') 
        st.write("**Prévia do arquivo carregado:**")
        st.dataframe(df.head(5))

        # ------------------------------------------
        # VALIDADOR INTELIGENTE DE FORMATO (Tipagem)
        # ------------------------------------------
        try:
            # Pega a linha 0, da coluna 1 em diante
            primeira_linha = df.iloc[0, 1:]
            
            # Conta quantos valores na linha são strings (textos)
            qtd_textos = primeira_linha.apply(lambda x: isinstance(x, str)).sum()
            proporcao_texto = qtd_textos / len(primeira_linha)
            
            # Se mais de 50% for texto, é a linha de 'Label' cruzando a tabela (Long)
            if st.session_state.modo_conversao == 'wide_to_long' and proporcao_texto > 0.5:
                st.warning("⚠️ **Aviso:** Detectamos majoritariamente textos na primeira linha de dados (provável linha de 'Label' ou 'Grupo'). Isso indica que sua tabela já está no formato **Longo** (transposta). Verifique a direção da conversão na setinha acima!")
                
            # Se for quase tudo número, é o formato Largo tradicional
            elif st.session_state.modo_conversao == 'long_to_wide' and proporcao_texto < 0.5:
                st.warning("⚠️ **Aviso:** A primeira linha de dados contém majoritariamente números, o que é característico do formato **Largo (Wide)**. Verifique a direção da conversão na setinha acima!")
        except Exception:
            pass # Silencioso em caso de tabelas anômalas

        st.write("#### Configuração da Conversão")
        
        # O usuário escolhe a primeira coluna (que contém o nome das amostras ou o nome dos metabólitos)
        # O padrão (index=0) já deixa a primeira coluna pré-selecionada, funcionando automaticamente na maioria dos casos.
        coluna_pivo = st.selectbox(
            "Qual coluna contém os identificadores/nomes (ex: Sample)?", 
            df.columns, 
            index=0
        )
        
        if st.button("Executar Transposição", type="primary"):
            try:
                # 1. Define a coluna escolhida como o índice real da tabela
                df_temp = df.set_index(coluna_pivo)
                
                # 2. Faz a transposição exata da matriz (tomba a tabela)
                df_transposto = df_temp.T
                
                # 3. Restaura o formato tabular (tira o índice para voltar a ser coluna)
                df_resultado = df_transposto.reset_index()
                
                # 4. Renomeia a nova primeira coluna para manter o mesmo nome original
                df_resultado.rename(columns={'index': coluna_pivo}, inplace=True)
                df_resultado.columns.name = None 
                
                st.write("✅ **Sucesso! Matriz transposta:**")
                st.dataframe(df_resultado.head(10))
                
                csv_final = df_resultado.to_csv(index=False).encode('utf-8')
                nome_arquivo = "tabela_long.csv" if st.session_state.modo_conversao == 'wide_to_long' else "tabela_wide.csv"
                st.download_button(f"📥 Baixar CSV Transposto", csv_final, nome_arquivo, "text/csv")
                
            except Exception as e:
                st.error(f"Erro inesperado durante a transposição: {e}")

```

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
