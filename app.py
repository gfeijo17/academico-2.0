import streamlit as st
from scholarly import scholarly

# Configuração da página
st.set_page_config(
    page_title="Buscador Acadêmico",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Buscador do Google Acadêmico")
st.write("Digite um tema abaixo para buscar os 10 primeiros artigos e obter os links de download em PDF.")

# Campo de entrada
tema = st.text_input("Tema de pesquisa:", placeholder="Ex: inteligência artificial na educação")

if st.button("Buscar Artigos", type="primary"):
    if not tema.strip():
        st.warning("Por favor, digite um tema para pesquisar.")
    else:
        with st.spinner("Buscando artigos no Google Acadêmico... Aguarde."):
            try:
                search_query = scholarly.search_pubs(tema)
                resultados = []

                # Pega os 10 primeiros resultados
                for _ in range(10):
                    try:
                        artigo = next(search_query)
                        resultados.append(artigo)
                    except StopIteration:
                        break

                if not resultados:
                    st.info("Nenhum artigo encontrado para este tema.")
                else:
                    st.success(f"Encontrados {len(resultados)} resultados!")

                    # Exibe os resultados
                    for i, artigo in enumerate(resultados, start=1):
                        bib = artigo.get('bib', {})
                        titulo = bib.get('title', 'Sem título')
                        autores = bib.get('author', ['Autor desconhecido'])
                        if isinstance(autores, list):
                            autores = ", ".join(autores)
                        ano = bib.get('pub_year', 'N/A')
                        resumo = bib.get('abstract', 'Sem resumo disponível.')
                        
                        link_pub = artigo.get('pub_url', '#')
                        link_pdf = artigo.get('eprint_url', None)

                        # Card do Artigo
                        with st.container():
                            st.markdown(f"### {i}. [{titulo}]({link_pub})")
                            st.caption(f"**Autores:** {autores} | **Ano:** {ano}")
                            st.write(resumo)

                            if link_pdf:
                                st.link_button("📄 Baixar PDF", link_pdf)
                            else:
                                st.caption("⚠️ *Link direto para PDF não disponível. Acesse pelo link do título.*")
                            
                            st.divider()

            except Exception as e:
                st.error(f"Ocorreu um erro na busca: {e}")
