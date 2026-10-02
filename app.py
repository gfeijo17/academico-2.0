import requests
import streamlit as st

st.set_page_config(page_title="Busca de Teses e Dissertações", page_icon="🎓", layout="centered")

st.title("🎓 Buscador de Teses e Dissertações")
st.write("Pesquisa de trabalhos de mestrado e doutorado ordenados dos mais recentes aos mais antigos.")

# Campo de busca
tema = st.text_input("Digite o tema desejado:", placeholder="Ex: aprendizagem motora educação física")

if st.button("Buscar Trabalhos", type="primary"):
    if not tema.strip():
        st.warning("Por favor, digite um tema.")
    else:
        with st.spinner("Consultando teses e dissertações mais recentes..."):
            try:
                # API oficial da BDTD (Busca ordenada por ano decrescente: sort=publishDate+desc)
                url = f"https://bdtd.ibict.br/vufind/api/v1/search?lookfor={tema}&sort=publishDate+desc&limit=10"
                
                response = requests.get(url, timeout=12)
                
                if response.status_code == 200:
                    data = response.json()
                    registros = data.get("records", [])
                    total = data.get("resultCount", 0)

                    if not registros:
                        st.info("Nenhuma tese ou dissertação encontrada para este tema.")
                    else:
                        st.success(f"Encontrados {total} trabalhos. Exibindo os 10 mais recentes:")

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

                            # Links de acesso ao documento
                            id_trabalho = trabalho.get("id")
                            link_bdtd = f"https://bdtd.ibict.br/vufind/Record/{id_trabalho}" if id_trabalho else "#"
                            
                            urls = trabalho.get("urls", [])
                            link_direto = urls[0].get("url") if urls else link_bdtd

                            # Exibição do Card
                            with st.container():
                                st.markdown(f"### {i}. [{titulo}]({link_direto})")
                                st.caption(f"📅 **Ano:** {ano} | 👤 **Autor:** {autores} | 🏛️ **Instituição:** {instituicao}")
                                
                                # Botões de acesso
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    st.link_button("🔗 Acessar Documento", link_direto)
                                
                                st.divider()
                else:
                    st.error("Servidor da BDTD indisponível no momento. Tente novamente em instantes.")

            except Exception as e:
                st.error(f"Erro na conexão: {e}")
