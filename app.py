import datetime
import re
import requests
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Buscador", page_icon="🎓", layout="centered")

# --- VALORES PADRÃO DA APLICAÇÃO ---
ANO_ATUAL = datetime.datetime.now().year
ANO_15_ANOS_ATRAS = ANO_ATUAL - 15

# Inicialização do Session State
if "tema_input" not in st.session_state:
    st.session_state["tema_input"] = ""
if "tipo_trabalho_input" not in st.session_state:
    st.session_state["tipo_trabalho_input"] = "Todos"
if "limite_input" not in st.session_state:
    st.session_state["limite_input"] = 20
if "anos_input" not in st.session_state:
    st.session_state["anos_input"] = (ANO_15_ANOS_ATRAS, ANO_ATUAL)

def reset_campos():
    """Restaura todos os controles para os valores padrão."""
    st.session_state["tema_input"] = ""
    st.session_state["tipo_trabalho_input"] = "Todos"
    st.session_state["limite_input"] = 20
    st.session_state["anos_input"] = (ANO_15_ANOS_ATRAS, ANO_ATUAL)

def destacar_termo(texto, termo):
    """Destaca os termos da busca em negrito dentro do texto."""
    if not termo or not texto:
        return texto
    palavras = [re.escape(p) for p in termo.strip().split() if len(p) > 2]
    if not palavras:
        return texto
    padrao = re.compile(r'(' + '|'.join(palavras) + r')', re.IGNORECASE)
    return padrao.sub(r'**\1**', texto)

# --- ESTILIZAÇÃO E CUSTOMIZAÇÃO CSS ---
st.markdown(
    """
    <style>
    /* Fundo geral da aplicação (Verde Musgo Claro) */
    .stApp {
        background-color: #e8efe6;
    }

    /* Animação CSS para mover a marca d'água da esquerda para a direita */
    @keyframes moverGfs {
        0% {
            transform: translateX(-100px);
        }
        100% {
            transform: translateX(100vw);
        }
    }

    /* Elemento da Marca d'água Animada "GFS" */
    .stApp::before {
        content: "GFS";
        position: fixed;
        top: 10px;
        left: 0;
        font-size: 32px;
        font-weight: 900;
        font-family: 'Arial Black', sans-serif;
        color: rgba(60, 90, 65, 0.25);
        letter-spacing: 4px;
        z-index: 9999;
        pointer-events: none;
        white-space: nowrap;
        animation: moverGfs 12s linear infinite;
    }

    /* Estilização do Título */
    h1 {
        color: #2d4a34 !important;
        font-weight: 700;
        margin-top: 0px !important;
    }

    /* Campo de entrada de texto destacado com degradê verde */
    div[data-baseweb="input"] {
        background: linear-gradient(135deg, #d8e4d5 0%, #b8ceb3 100%) !important;
        border-radius: 10px !important;
        border: 1px solid #94b08f !important;
        padding: 4px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    div[data-baseweb="input"] input {
        background-color: transparent !important;
        color: #1e3323 !important;
        font-weight: 500 !important;
    }

    /* Padronização Unificada de Todos os Botões */
    div.stButton > button,
    div[data-testid="stLinkButton"] > a,
    div[data-testid="stDownloadButton"] > button,
    a[data-testid="stBaseButton-secondary"] {
        background-color: #3b5e43 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #3b5e43 !important;
        font-weight: 600 !important;
        text-align: center !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }

    /* Efeito de Hover em Todos os Botões */
    div.stButton > button:hover,
    div[data-testid="stLinkButton"] > a:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    a[data-testid="stBaseButton-secondary"]:hover {
        background-color: #2c4732 !important;
        border-color: #2c4732 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }

    div[data-testid="stColumn"] {
        display: flex;
        align-items: flex-start;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- CABEÇALHO COM BOTÃO "NOVA PESQUISA" NO CANTO SUPERIOR ESQUERDO ---
col_top_left, col_top_right = st.columns([1, 3])

with col_top_left:
    st.button("🔄 Nova Pesquisa", on_click=reset_campos, use_container_width=True)

st.title("Buscador")
st.write("Pesquisa de teses e dissertações de pós-graduação ordenadas das mais recentes às mais antigas.")

# --- FORMULÁRIO DE PESQUISA (PERMITE SUBMIT COM ENTER) ---
with st.form(key="search_form"):
    tema = st.text_input(
        "Digite o tema desejado:",
        placeholder="Ex: aprendizagem motora educação física",
        key="tema_input"
    )

    col_filtro, col_qtd = st.columns([2, 1])

    with col_filtro:
        tipo_trabalho = st.selectbox(
            "Tipo de documento:",
            options=["Todos", "Dissertações de Mestrado", "Teses de Doutorado"],
            key="tipo_trabalho_input"
        )

    with col_qtd:
        limite_resultados = st.select_slider(
            "Quantidade de resultados:",
            options=[10, 20, 30, 50],
            key="limite_input"
        )

    ano_inicial, ano_final = st.slider(
        "Intervalo de anos da publicação:",
        min_value=1990,
        max_value=ANO_ATUAL,
        key="anos_input"
    )

    buscar_btn = st.form_submit_button("Buscar Trabalhos", use_container_width=True)

# --- EXECUÇÃO DA BUSCA ---
if buscar_btn:
    if not tema.strip():
        st.warning("Por favor, digite um tema.")
    else:
        with st.spinner("Consultando a BDTD..."):
            try:
                termo_busca = tema.strip()
                if tipo_trabalho == "Dissertações de Mestrado":
                    termo_busca += ' "dissertação"'
                elif tipo_trabalho == "Teses de Doutorado":
                    termo_busca += ' "tese"'

                query_encoded = urllib.parse.quote(termo_busca)
                
                url = (
                    f"https://bdtd.ibict.br/vufind/api/v1/search?"
                    f"lookfor={query_encoded}&sort=publishDate+desc&limit={limite_resultados}"
                    f"&daterange[]=publishDate&publishDatefrom={ano_inicial}&publishDateto={ano_final}"
                )
                
                response = requests.get(url, timeout=12)
                
                if response.status_code == 200:
                    data = response.json()
                    registros = data.get("records", [])
                    total = data.get("resultCount", 0)

                    if not registros:
                        st.info("Nenhuma tese ou dissertação encontrada para este tema no período selecionado.")
                    else:
                        st.success(f"Encontrados {total} resultados ({ano_inicial}-{ano_final}). Exibindo os {len(registros)} mais recentes:")

                        # Preparação dos dados para exportação CSV
                        dados_exportacao = []

                        for i, trabalho in enumerate(registros, start=1):
                            titulo = trabalho.get("title", "Título indisponível")
                            
                            autores_raw = trabalho.get("authors", {})
                            autores_list = autores_raw.get("primary", {})
                            autores = ", ".join(autores_list.keys()) if autores_list else "Autor não informado"

                            anos = trabalho.get("publicationDates", ["Ano não informado"])
                            ano = anos[0] if anos else "N/A"
                            
                            instituicao_raw = trabalho.get("institutions", ["Instituição não informada"])
                            instituicao = instituicao_raw[0] if instituicao_raw else ""

                            resumo_raw = trabalho.get("summary", [])
                            if isinstance(resumo_raw, list) and resumo_raw:
                                resumo = resumo_raw[0]
                            elif isinstance(resumo_raw, str):
                                resumo = resumo_raw
                            else:
                                resumo = "Resumo não disponibilizado no registro."

                            id_trabalho = trabalho.get("id")
                            link_bdtd = f"https://bdtd.ibict.br/vufind/Record/{id_trabalho}" if id_trabalho else None
                            
                            urls = trabalho.get("urls", [])
                            link_repositorio = urls[0].get("url") if urls else link_bdtd

                            # --- LÓGICA DE EXTRAÇÃO DO PDF DIRETO ---
                            link_pdf = None
                            for u in urls:
                                u_str = u.get("url", "")
                                u_lower = u_str.lower()
                                if u_lower.endswith(".pdf") or "bitstream" in u_lower or "/download" in u_lower:
                                    link_pdf = u_str
                                    break
                            
                            if not link_pdf:
                                link_pdf = link_repositorio

                            # Identificação de Mestrado ou Doutorado
                            tag_tipo = "🎓 Doutorado" if "doutor" in titulo.lower() or "tese" in titulo.lower() else "📜 Mestrado"

                            # Citação ABNT
                            citacao_abnt = f"{autores.upper()}. **{titulo}**. {ano}. {instituicao}."

                            # Adiciona à lista de exportação
                            dados_exportacao.append({
                                "Título": titulo,
                                "Autor": autores,
                                "Ano": ano,
                                "Instituição": instituicao,
                                "Resumo": resumo,
                                "Link Repositório": link_repositorio,
                                "Link PDF": link_pdf,
                                "Link BDTD": link_bdtd
                            })

                            # --- EXIBIÇÃO DO CARD ---
                            with st.container():
                                st.markdown(f"### {i}. [{titulo}]({link_repositorio})")
                                st.caption(f"{tag_tipo} | 📅 **Ano:** {ano} | 👤 **Autor:** {autores} | 🏛️ **Instituição:** {instituicao}")
                                
                                # Resumo com destaque de palavras-chave e botão de PDF
                                c_resumo, c_pdf = st.columns([3.2, 1])
                                with c_resumo:
                                    with st.expander("📝 Ler resumo"):
                                        st.markdown(destacar_termo(resumo, tema))
                                with c_pdf:
                                    if link_pdf:
                                        st.link_button("📄 PDF", link_pdf, use_container_width=True)

                                # Expander com a citação ABNT
                                with st.expander("📜 Copiar citação (ABNT)"):
                                    st.code(citacao_abnt, language="markdown")

                                # Botões inferiores
                                c1, c2 = st.columns(2)
                                with c1:
                                    if link_repositorio:
                                        st.link_button("🔗 Abrir Repositório", link_repositorio, use_container_width=True)
                                with c2:
                                    if link_bdtd:
                                        st.link_button("🏛️ Ver Registro na BDTD", link_bdtd, use_container_width=True)
                                
                                st.divider()

                        # Botão para exportação dos resultados em CSV
                        if dados_exportacao:
                            df = pd.DataFrame(dados_exportacao)
                            csv_data = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Baixar Resultados (.csv)",
                                data=csv_data,
                                file_name=f"pesquisa_bdtd_{tema.replace(' ', '_')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

                else:
                    st.error("Servidor da BDTD indisponível no momento.")

            except Exception as e:
                st.error(f"Erro na conexão: {e}")
