import requests
import urllib.parse
import streamlit as st

st.set_page_config(page_title="Buscador", page_icon="🎓", layout="centered")

# --- ESTILIZAÇÃO E CUSTOMIZAÇÃO CSS ---
st.markdown(
    """
    <style>
    /* Fundo geral da aplicação (Verde Musgo Claro) */
    .stApp {
        background-color: #e8efe6;
    }

    /* Marca d'água "GFS" no canto superior direito */
    .stApp::before {
        content: "GFS";
        position: fixed;
        top: 15px;
        right: 30px;
        font-size: 38px;
        font-weight: 900;
        font-family: 'Arial Black', sans-serif;
        color: rgba(60, 90, 65, 0.15); /* Verde musgo com opacidade leve */
        letter-spacing: 3px;
        z-index: 9999;
        pointer-events: none;
    }

    /* Estilização do Título */
    h1 {
        color: #2d4a34 !important;
        font-weight: 700;
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

    /* Personalização do Botão */
    div.stButton > button {
        background-color: #3b5e43 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #2c4732 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- INTERFACE ---
st.title("Buscador")
st.write("Pesquisa de teses e dissertações de pós-graduação ordenadas das mais recentes às mais antigas.")

# Campo de entrada com o destaque em degradê
tema = st.text_input("Digite o tema desejado:", placeholder="Ex: aprendizagem motora educação física")

# Controles de filtro em colunas paralelas
col_filtro, col_qtd = st.columns([2, 1])

with col_filtro:
    tipo_trabalho = st.selectbox(
        "Tipo de documento:",
        options=["Todos", "Dissertações de Mestrado", "Teses de Doutorado"]
    )

with col_qtd:
    limite_resultados = st.select_slider(
        "Quantidade de resultados:",
        options=[10, 20, 30, 50],
        value=20
    )

# Filtro de Intervalo de Anos
ano_inicial, ano_final = st.slider(
    "Intervalo de anos da publicação:",
    min_value=1990,
    max_value=2026,
    value=(2010, 2026)
)

if st.button("Buscar Trabalhos"):
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
                
                # API da BDTD
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

                        for i, trabalho in enumerate(registros, start=1):
                            titulo = trabalho.get("title", "Título indisponível")
                            
                            # Autores
                            autores_raw = trabalho.get("authors", {})
                            autores_list = autores_raw.get("primary", {})
                            autores = ", ".join(autores_list.keys()) if autores_list else "Autor não informado"

                            # Ano e Instituição
                            anos = trabalho.get("publicationDates", ["Ano não informado"])
                            ano = anos[0] if anos else "N/A"
                            
                            instituicao_raw = trabalho.get("institutions", ["Instituição não informada"])
                            instituicao = instituicao_raw[0] if instituicao_raw else ""

                            # Links correlatos
                            id_trabalho = trabalho.get("id")
                            link_bdtd = f"https://bdtd.ibict.br/vufind/Record/{id_trabalho}" if id_trabalho else None
                            
                            urls = trabalho.get("urls", [])
                            link_direto = urls[0].get("url") if urls else link_bdtd

                            # Exibição do Card
                            with st.container():
                                st.markdown(f"### {i}. [{titulo}]({link_direto})")
                                st.caption(f"📅 **Ano:** {ano} | 👤 **Autor:** {autores} | 🏛️ **Instituição:** {instituicao}")
                                
                                # Botões de acesso aos materiais correlatos
                                c1, c2 = st.columns(2)
                                with c1:
                                    if link_direto:
                                        st.link_button("🔗 Abrir Repositório / PDF", link_direto, use_container_width=True)
                                with c2:
                                    if link_bdtd:
                                        st.link_button("🏛️ Ver Registro na BDTD", link_bdtd, use_container_width=True)
                                
                                st.divider()
                else:
                    st.error("Servidor da BDTD indisponível no momento.")

            except Exception as e:
                st.error(f"Erro na conexão: {e}")
