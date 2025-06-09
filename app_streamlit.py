import streamlit as st
import os
import io # Necessário para ler os bytes do arquivo
import PyPDF2 # A biblioteca que acabamos de instalar

# Importa a função conversacional do seu script
# Nenhuma mudança na importação
from chatMed import obter_resposta_conversacional, my_google_api_key

# --- Função para extrair texto de PDF ---
def extrair_texto_pdf(file_bytes):
    """Recebe os bytes de um arquivo PDF e retorna o texto extraído."""
    try:
        # Cria um objeto de fluxo de bytes em memória
        pdf_file = io.BytesIO(file_bytes)
        # Lê o arquivo PDF
        reader = PyPDF2.PdfReader(pdf_file)
        texto_completo = ""
        # Itera sobre todas as páginas e extrai o texto
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        return f"Erro ao ler o arquivo PDF: {e}"

# --- Configuração da Página e Título (sem mudanças) ---
st.set_page_config(page_title="Chat Médico Interativo", layout="wide") # Mudei para 'wide' para dar mais espaço
st.title("🩺 Chat Médico Interativo com IA")
st.caption("Potencializado por CrewAI e Google Gemini. Agora com análise de documentos.")

# --- Colunas para layout: uma para o chat, outra para upload e avisos ---
col1, col2 = st.columns([2, 1])

with col2:
    # --- Aviso de Segurança ---
    aviso_seguranca = (
        "<div style='background-color:#FFD2D2; padding:10px; border-radius:5px; border: 1px solid #D8000C; margin-bottom: 20px;'>"
        "<h4 style='color:#D8000C; margin-top:0;'>⚠️ AVISO IMPORTANTE: NÃO É UM DIAGNÓSTICO MÉDICO</h4>"
        "<p style='color:#333;'>Esta é uma ferramenta de IA para triagem inicial. As informações e análises de documentos "
        "<strong>NÃO</strong> substituem o aconselhamento, diagnóstico ou tratamento médico profissional."
        "<br><strong>SEMPRE CONSULTE UM MÉDICO QUALIFICADO.</strong></p>"
        "</div>"
    )
    st.markdown(aviso_seguranca, unsafe_allow_html=True)
    
    # --- NOVO: Componente de Upload de Arquivo ---
    st.subheader("Analisar um Documento (PDF)")
    uploaded_file = st.file_uploader(
        "Envie um resultado de exame ou documento PDF para análise:",
        type=['pdf']
    )
    
    # Lógica para processar o arquivo assim que ele é enviado
    # Usamos o session_state para garantir que o arquivo seja processado apenas uma vez
    if uploaded_file is not None and uploaded_file.id not in st.session_state.get('processed_files', []):
        with st.spinner(f"Lendo e processando o arquivo '{uploaded_file.name}'..."):
            # Lê os bytes do arquivo
            file_bytes = uploaded_file.getvalue()
            # Extrai o texto
            texto_do_documento = extrair_texto_pdf(file_bytes)
            
            # Adiciona o texto extraído ao histórico da conversa (para dar contexto à IA)
            # Esta é a "mensagem do sistema" que a IA verá
            st.session_state.messages.append({
                "role": "user", 
                "content": f"INFORMAÇÃO DE DOCUMENTO: O seguinte texto foi extraído do documento '{uploaded_file.name}'. Analise-o e prepare-se para responder perguntas sobre ele.\n\n---\n{texto_do_documento}\n---"
            })
            
            # Adiciona uma mensagem de confirmação para o usuário ver
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Analisei o documento '{uploaded_file.name}'. Agora você pode me fazer perguntas sobre o conteúdo dele."
            })
            
            # Adiciona o ID do arquivo à lista de processados
            if 'processed_files' not in st.session_state:
                st.session_state.processed_files = []
            st.session_state.processed_files.append(uploaded_file.id)
            
            # Força o rerender da página para mostrar a mensagem de confirmação
            st.rerun()


with col1:
    # --- Verificação da API Key ---
    if not my_google_api_key:
        st.error("ERRO: A chave GOOGLE_API_KEY não foi carregada.")
        st.stop()

    # --- Gerenciamento e Exibição do Histórico da Conversa ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou seu assistente de saúde virtual. Você pode descrever seus sintomas ou me enviar um documento (PDF) para análise."}
        ]

    for message in st.session_state.messages:
        # Não mostra para o usuário o prompt gigante com o texto do PDF
        if "INFORMAÇÃO DE DOCUMENTO:" in message["content"] and message["role"] == "user":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Input do Usuário e Lógica do Chat ---
    if prompt := st.chat_input("Faça uma pergunta sobre o documento ou descreva seus sintomas..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analisando e pensando... 🧠⚙️"):
                try:
                    resposta_ia = obter_resposta_conversacional(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
                    st.markdown(resposta_ia)
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")