import streamlit as st
from scholarly import scholarly

st.set_page_config(page_title="Buscador Acadêmico", page_icon="🎓")

st.title("🎓 Buscador Acadêmico")
st.write("Digite o tema desejado para pesquisar os 10 primeiros artigos do Google Acadêmico e obter os links em PDF.")

# Entrada do tema
tema = st.text_input("Tema da pesquisa:", placeholder="Ex: inteligência artificial na educação")

if st.button("Buscar Artigos", type="primary"):
    if not tema.strip():
        st.warning("Por favor, informe um tema.")
    else:
        with st.spinner("Consultando o Google Acadêmico... Isso pode levar alguns segundos."):
            try:
                search_query = scholarly.search_pubs(tema)
                resultados = []

                # Tenta recuperar até 10 publicações
                for _ in range(10):
                    try:
                        artigo = next(search_query)
                        resultados.append(artigo)
                    except StopIteration:
                        break

                if not resultados:
                    st.info("Nenhum artigo foi encontrado para este tema.")
                else:
                    st.success(f"{len(resultados)} artigos encontrados com sucesso!")

                    for i, artigo in enumerate(resultados, start=1):
                        bib = artigo.get('bib', {})
                        titulo = bib.get('title', 'Sem título disponível')
                        
                        # Formatação de autores
                        autores = bib.get('author', ['Autor não informado'])
                        if isinstance(autores, list):
                            autores = ", ".join(autores)
                            
                        ano = bib.get('pub_year', 'N/A')
                        resumo = bib.get('abstract', 'Resumo não disponível.')
                        
                        link_artigo = artigo.get('pub_url', '#')
                        link_pdf = artigo.get('eprint_url', None)

                        with st.container():
                            st.markdown(f"### {i}. [{titulo}]({link_artigo})")
                            st.caption(f"**Autores:** {autores} | **Ano:** {ano}")
                            st.write(resumo)

                            if link_pdf:
                                st.link_button("📄 Baixar PDF", link_pdf)
                            else:
                                st.caption("⚠️ *Link direto para PDF não disponível. Acesse pelo link principal do artigo.*")
                            
                            st.divider()

            except Exception as e:
                st.error(f"Erro ao acessar o Google Acadêmico: {e}")
