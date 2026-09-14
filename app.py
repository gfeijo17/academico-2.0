import os
import io
import datetime
import requests
import streamlit as st
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="Pesquisador Acadêmico & NotebookLM", page_icon="🎓", layout="wide")

st.title("🎓 Pesquisador Acadêmico com Google Drive & Gemini Notebook")
st.markdown("Busque no Google Acadêmico em português, salve os PDFs no Google Drive, adicione ao seu Notebook de pesquisa e gere um roteiro de podcast automaticamente.")

# ==============================================================================
# CONFIGURAÇÕES E CHAVES
# ==============================================================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "").strip()
SERPER_API_KEY = st.secrets.get("SERPER_API_KEY", "").strip()

# Configurações do Google Drive (Necessário Token OAuth ou Service Account)
GOOGLE_DRIVE_TOKEN = st.secrets.get("GOOGLE_DRIVE_TOKEN", None)

# --- FUNÇÃO 1: BUSCA GOOGLE SCHOLAR (PORTUGUÊS - 5 RESULTADOS) ---
def buscar_scholar_pt(query, api_key, num_results=5):
    """Busca 5 artigos em português no Google Acadêmico via Serper."""
    url = "https://google.serper.dev/scholar"
    payload = {
        "q": query,
        "gl": "br",
        "hl": "pt-br",
        "lr": "lang_pt",
        "num": num_results
    }
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            results = response.json().get('organic', [])[:num_results]
            artigos = []
            for r in results:
                pdf_url = None
                # Busca por link direto para PDF nas fontes
                if 'resources' in r and isinstance(r['resources'], list):
                    for res in r['resources']:
                        if res.get('link', '').lower().endswith('.pdf') or 'pdf' in res.get('title', '').lower():
                            pdf_url = res.get('link')
                            break
                if not pdf_url and r.get('link', '').lower().endswith('.pdf'):
                    pdf_url = r.get('link')

                artigos.append({
                    "title": r.get('title', 'Sem título'),
                    "link": r.get('link', '#'),
                    "snippet": r.get('snippet', 'Sem resumo disponível.'),
                    "publication": r.get('publicationInfo', 'Fonte não informada'),
                    "pdf_link": pdf_url
                })
            return artigos
        else:
            st.error(f"Erro Serper: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return []

# --- FUNÇÃO 2: DOWNLOAD DO PDF ---
def baixar_pdf(url):
    """Baixa o conteúdo em bytes de um link PDF."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200 and 'pdf' in res.headers.get('Content-Type', '').lower():
            return res.content
    except Exception:
        pass
    return None

# --- FUNÇÃO 3: CRIAR PASTA E FAZER UPLOAD NO GOOGLE DRIVE ---
def salvar_no_google_drive(nome_pesquisa, arquivos_pdf):
    """Cria pasta 'nome-da-pesquisa_DD/MM/AAAA' e salva os PDFs."""
    if not GOOGLE_DRIVE_TOKEN:
        st.warning("⚠️ Token do Google Drive não configurado nos Secrets. Pulando etapa do Drive.")
        return None

    try:
        creds = Credentials.from_authorized_user_info(GOOGLE_DRIVE_TOKEN)
        service = build('drive', 'v3', credentials=creds)

        data_atual = datetime.datetime.now().strftime("%d-%m-%Y")
        nome_pasta = f"{nome_pesquisa}_{data_atual}"

        # Criar a pasta no Drive
        folder_metadata = {
            'name': nome_pasta,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')

        # Upload dos PDFs
        for pdf in arquivos_pdf:
            file_metadata = {
                'name': pdf['filename'],
                'parents': [folder_id]
            }
            media = MediaIoBaseUpload(io.BytesIO(pdf['bytes']), mimetype='application/pdf')
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        return folder_id
    except Exception as e:
        st.error(f"Erro ao salvar no Google Drive: {e}")
        return None

# --- INTERFACE PRINCIPAL ---
termo_busca = st.text_input("Digite o tema da pesquisa acadêmica:", placeholder="Ex: inteligência artificial na educação")

if st.button("Executar Pesquisa e Fluxo de Trabalho", type="primary"):
    if not termo_busca:
        st.warning("Por favor, digite um tema.")
    else:
        st.markdown("---")
        
        # PASSO 1: Pesquisar no Google Acadêmico
        with st.spinner("1/4 - Pesquisando artigos no Google Acadêmico em português..."):
            artigos = buscar_scholar_pt(termo_busca, SERPER_API_KEY, num_results=5)
            
        if not artigos:
            st.error("Nenhum artigo encontrado. Verifique a chave da API do Serper.")
        else:
            st.success(f"Encontrados {len(artigos)} artigos acadêmicos.")
            
            # Exibir os 5 resultados e URLs acessíveis
            st.subheader("📚 Artigos Selecionados:")
            for i, art in enumerate(artigos, 1):
                st.markdown(f"**{i}. {art['title']}**")
                st.write(f"🔗 **URL Principal:** [{art['link']}]({art['link']})")
                if art['pdf_link']:
                    st.write(f"📄 **PDF Direto:** [{art['pdf_link']}]({art['pdf_link']})")
                else:
                    st.write("⚠️ *PDF direto não detectado na busca.*")
                st.caption(f"Publicação: {art['publication']}")
                st.write("---")

            # PASSO 2: Download dos PDFs
            with st.spinner("2/4 - Baixando os arquivos PDF disponíveis..."):
                pdfs_baixados = []
                for i, art in enumerate(artigos, 1):
                    url_target = art['pdf_link'] or art['link']
                    pdf_bytes = baixar_pdf(url_target)
                    if pdf_bytes:
                        nome_arquivo = f"Artigo_{i}_{termo_busca.replace(' ', '_')}.pdf"
                        pdfs_baixados.append({"filename": nome_arquivo, "bytes": pdf_bytes, "title": art['title'], "snippet": art['snippet']})

            st.info(f"{len(pdfs_baixados)} de 5 PDFs baixados com sucesso.")

            # PASSO 3: Criar Pasta e Salvar no Google Drive
            with st.spinner("3/4 - Criando pasta e salvando arquivos no Google Drive..."):
                drive_folder_id = salvar_no_google_drive(termo_busca, pdfs_baixados)
                if drive_folder_id:
                    st.success(f"📁 Pasta criada no Google Drive com sucesso!")

            # PASSO 4: Criar Roteiro de Podcast via Gemini API
            with st.spinner("4/4 - Processando o conteúdo das fontes e gerando o Roteiro do Podcast..."):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)

                    # Consolidação do texto dos 5 artigos/PDFs
                    contexto_fontes = ""
                    for pdf in pdfs_baixados:
                        contexto_fontes += f"\n\n--- ARTIGO: {pdf['title']} ---\n{pdf['snippet']}"

                    prompt_podcast = f"""
                    Você é um roteirista profissional de podcasts científicos e educacionais.
                    Com base no conteúdo dos 5 artigos científicos pesquisados sobre o tema "{termo_busca}":

                    FONTES DOS ARTIGOS:
                    {contexto_fontes}

                    Crie um ROTEIRO COMPLETO DE PODCAST de resumo (Audio Overview) entre dois apresentadores:
                    - **Apresentador 1 (Anfitrião):** Conduz a conversa de forma dinâmica e faz perguntas instigantes.
                    - **Apresentador 2 (Especialista):** Explica os conceitos acadêmicos e descobertas dos 5 artigos de forma didática.

                    Mantenha a conversa natural, em português do Brasil, destacando os pontos em comum e descobertas principais dos artigos baixados.
                    """

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_podcast
                    )

                    st.subheader("🎙️ Roteiro do Podcast Gerado")
                    st.markdown(response.text)

                    # Opção de Download do Roteiro
                    st.download_button(
                        label="📥 Baixar Roteiro (.txt)",
                        data=response.text,
                        file_name=f"roteiro_podcast_{termo_busca.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Erro ao gerar o roteiro com a API do Gemini: {e}")
