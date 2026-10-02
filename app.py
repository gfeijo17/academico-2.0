import streamlit as st
from scholarly import scholarly

st.set_page_config(page_title="Buscador Acadêmico", page_icon="🎓", layout="centered")

st.title("🎓 Buscador Acadêmico")
st.write("Insira um tema para pesquisar os 10 primeiros artigos no Google Acadêmico e obter os links de acesso e PDF.")

tema = st.text_input("Tema de pesquisa:", placeholder="Ex: aprendizagem motora na educação física")

if st.button("Buscar Artigos", type="primary"):
    if not tema.strip():
        st.warning("Por favor, informe um tema válido.")
    else:
        with st.spinner("Buscando publicações no Google Acadêmico..."):
            try:
                search_query = scholarly.search_pubs(tema)
                resultados = []

                for _ in range(10):
                    try:
                        artigo = next(search_query)
                        resultados.append(artigo)
                    except StopIteration:
                        break

                if not resultados:
                    st.info("Nenhum resultado foi localizado para esse tema.")
                else:
                    st.success(f"{len(resultados)} artigos encontrados com sucesso!")

                    for i, artigo in enumerate(resultados, start=1):
                        bib = artigo.get('bib', {})
                        titulo = bib.get('title', 'Título não informado')
                        
                        autores = bib.get('author', ['Autor não informado'])
                        if isinstance(autores, list):
                            autores = ", ".join(autores)
                            
                        ano = bib.get('pub_year', 'N/A')
                        resumo = bib.get('abstract', 'Resumo indisponível.')
                        
                        link_artigo = artigo.get('pub_url', '#')
                        link_pdf = artigo.get('eprint_url', None)

                        with st.container():
                            st.markdown(f"### {i}. [{titulo}]({link_artigo})")
                            st.caption(f"**Autores:** {autores} | **Ano:** {ano}")
                            st.write(resumo)

                            if link_pdf:
                                st.link_button("📄 Baixar PDF", link_pdf)
                            else:
                                st.caption("⚠️ *Link direto para PDF indisponível (acesse através do título).*")
                            
                            st.divider()

            except Exception as e:
                st.error(f"Erro no processamento da consulta: {e}")
