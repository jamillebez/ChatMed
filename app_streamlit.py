import streamlit as st
import os # Para verificar se a chave foi carregada, embora dotenv faça o trabalho principal

# Importa a função principal do seu script CrewAI
# Certifique-se de que 'seu_crewai_script.py' está na mesma pasta
from chatMed import analisar_sintomas_com_crewai, my_google_api_key

# Interface do Streamlit
st.set_page_config(page_title="Analisador de Sintomas com IA", layout="centered")
st.title("🩺 Analisador de Sintomas com IA")
st.caption("Potencializado por CrewAI e Modelos de Linguagem da Google")
st.markdown("---")

# Verificar se a API Key foi carregada (mais para feedback ao usuário)
if not my_google_api_key:
    st.error("ERRO: A chave GOOGLE_API_KEY não foi carregada. "
             "Verifique seu arquivo .env ou as variáveis de ambiente do sistema.")
    st.stop() # Impede a execução do restante do app se a chave não estiver presente

st.subheader("Descreva seus sintomas abaixo:")
sintomas_usuario = st.text_area("Ex: 'Febre alta há 2 dias, dor de garganta intensa...'", height=200)

if st.button("Analisar Sintomas Agora", type="primary"):
    if sintomas_usuario.strip(): # Verifica se o usuário digitou algo
        with st.spinner("Processando com a equipe de especialistas IA... Isso pode levar um momento. 🧠⚙️"):
            try:
                # Chama a função do seu script CrewAI
                relatorio_medico = analisar_sintomas_com_crewai(sintomas_usuario)

                # Exibe o aviso de segurança e o relatório
                st.markdown("---")
                aviso_seguranca = (
                    "<div style='background-color:#FFD2D2; padding:10px; border-radius:5px; border: 1px solid #D8000C;'>"
                    "<h4 style='color:#D8000C; margin-top:0;'>⚠️ AVISO IMPORTANTE DE SEGURANÇA E RESPONSABILIDADE:</h4>"
                    "<p style='color:#333;'>Este é o resultado de uma demonstração tecnológica e <strong>NÃO</strong> substitui "
                    "aconselhamento médico profissional, diagnóstico ou tratamento."
                    "<br><strong>SEMPRE CONSULTE UM MÉDICO QUALIFICADO PARA QUESTÕES DE SAÚDE.</strong></p>"
                    "</div><br>"
                )
                st.markdown(aviso_seguranca, unsafe_allow_html=True)

                st.subheader("Resultado da Análise da Equipe Médica (IA):")
                st.markdown(relatorio_medico) # st.markdown pode renderizar melhor o texto formatado

            except Exception as e:
                st.error(f"Ocorreu um erro inesperado durante a análise: {e}")
                st.exception(e) # Mostra o traceback do erro para depuração

    else:
        st.warning("Por favor, descreva seus sintomas no campo acima antes de analisar.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>Lembre-se: esta é uma ferramenta de demonstração.</p>", unsafe_allow_html=True)