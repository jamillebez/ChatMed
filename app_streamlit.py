import streamlit as st
import io
import PyPDF2
from chatMed import rodar_analise_completa, my_google_api_key

# --- Função para extrair texto de PDF ---
def extrair_texto_pdf(file_bytes):
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        st.error(f"Erro ao ler o arquivo PDF: {e}")
        return ""

# --- Configuração da Página ---
st.set_page_config(page_title="Suporte à Decisão Clínica", layout="centered")
st.title("Ferramenta de Suporte à Decisão em Neurologia")
st.caption("IA para auxiliar médicos na avaliação e workup de casos neurológicos.")

# --- Verificação da API Key ---
if not my_google_api_key:
    st.error("ERRO CRÍTICO: A chave GOOGLE_API_KEY não foi configurada. Verifique seu arquivo .env.")
    st.stop()

# --- Área de Input do Usuário ---
st.subheader("1. Insira os dados clínicos do paciente")
sintomas_usuario = st.text_area(
    "Insira dados da anamnese, queixa principal, exame físico e informações relevantes para a análise.",
    height=200,
    placeholder="Ex: Paciente, 45 anos, sexo feminino, com história de cefaleia pulsátil hemicraniana D há 2 dias, associada a fotofobia e fonofobia. Exame neurológico sem déficits focais..."
)

st.subheader("2. (Opcional) Anexe laudos ou documentos")
uploaded_file = st.file_uploader(
    "Envie laudos de exames anteriores ou outros documentos em PDF.",
    type=['pdf']
)

# --- Botão para iniciar a análise ---
st.subheader("3. Gerar Sumário Clínico")
if st.button("Analisar Caso", type="primary"):
    
    texto_documento = ""
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        texto_documento = extrair_texto_pdf(file_bytes)

    dados_completos = f"""
    DADOS CLÍNICOS FORNECIDOS PELO MÉDICO:
    ---
    {sintomas_usuario}
    ---
    
    CONTEÚDO EXTRAÍDO DE DOCUMENTO PDF ANEXO:
    ---
    {texto_documento}
    ---
    """
    
    if not sintomas_usuario.strip() and not texto_documento.strip():
        st.error("Por favor, insira os dados do caso ou anexe um documento para análise.")
    else:
        with st.spinner("A equipe de IAs está processando o caso clínico... Isso pode levar um ou dois minutos."):
            try:
                # Chamar a função principal do backend
                resultado_final = rodar_analise_completa(dados_completos)
                
                st.divider()
                st.success("Análise Concluída!")
                
                # Exibir o relatório final
                st.markdown(resultado_final)
                
            except Exception as e:
                st.error(f"Ocorreu um erro durante a análise: {e}")