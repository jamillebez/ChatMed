import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models.litellm import ChatLiteLLM

# CARREGAR VARIÁVEIS DE AMBIENTE E INSTANCIAR LLM
load_dotenv()
my_google_api_key = os.getenv("GOOGLE_API_KEY")

if not my_google_api_key:
    raise ValueError("Chave de API do Google (GOOGLE_API_KEY) não encontrada.")

llm = ChatLiteLLM(
    model="gemini/gemini-1.5-flash",
    api_key=my_google_api_key
)

# AGENTE 1: DIAGNÓSTICO
agente_diagnostico = Agent(
    role="IA de Suporte à Decisão para Diagnóstico Neurológico",
    goal="""Analisar dados clínicos (anamnese, exame físico) para gerar um diagnóstico diferencial técnico, citando critérios relevantes (ex: DSM-5, CID-11, critérios de LINET) e estratificando as hipóteses por probabilidade para auxiliar o médico usuário.""",
    backstory="""Você é um sistema de IA treinado com as mais recentes diretrizes e publicações em neurologia. Sua função é servir como uma ferramenta de consulta rápida para médicos, oferecendo um diferencial baseado em evidências para casos complexos.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# AGENTE 2: EXAMES
agente_exames = Agent(
    role="Consultor de IA para Exames de Neuroimagem e Neurofisiologia",
    goal="""Com base em um diagnóstico diferencial, sugerir e justificar um plano de workup com exames complementares. Detalhar a relevância clínica de cada exame (ex: 'RNM de encéfalo com contraste para avaliação de lesões desmielinizantes') para o caso em questão.""",
    backstory="""Você é uma IA especialista em diretrizes de exames de imagem e testes neurológicos. Você auxilia médicos a escolherem o método de investigação mais custo-efetivo e com maior acurácia diagnóstica.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# AGENTE 3: AVALIAÇÃO DE RISCO
agente_risco = Agent(
    role="IA para Estratificação de Risco Clínico e Urgência",
    goal="""Realizar a estratificação de risco do caso clínico, destacando 'red flags' específicas. Classificar a urgência (eletiva, prioritária, emergência) com base em protocolos reconhecidos e justificar a classificação para o médico.""",
    backstory="""Você é uma IA treinada em protocolos de triagem de emergência e modelos de predição de risco. Seu objetivo é alertar o médico sobre potenciais gravidades que exijam ação imediata.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# AGENTE 4: RELATOR FINAL
agente_relator = Agent(
    role="Assistente de IA para Geração de Sumário Clínico",
    goal="""Sintetizar as análises dos agentes de diagnóstico, exames e risco em um sumário clínico estruturado e conciso. O formato deve ser adequado para uma rápida revisão por um profissional ou para inclusão em prontuário eletrônico.""",
    backstory="""Você é uma IA especializada em documentação médica. Sua habilidade é consolidar múltiplas análises técnicas em um sumário claro, objetivo e clinicamente útil.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# FUNÇÃO PRINCIPAL QUE ORQUESTRA A EQUIPE (CREW)
def rodar_analise_completa(dados_paciente: str) -> str:
    
    tarefa_diagnostico = Task(
         description=f"Com base nos dados clínicos do paciente, gerar um diagnóstico diferencial técnico e probabilístico. Dados: {dados_paciente}",
         agent=agente_diagnostico,
         expected_output="Uma lista de diagnósticos diferenciais com probabilidades e breves justificativas clínicas."
    )

    tarefa_exames = Task(
         description="Com base no diferencial diagnóstico, propor um plano de workup com justificativa técnica para cada exame sugerido.",
         agent=agente_exames,
         context=[tarefa_diagnostico],
         expected_output="Uma seção de 'Sugestão de Workup' com a lista de exames e sua pertinência clínica."
    )

    tarefa_risco = Task(
         description="Realizar a estratificação de risco do paciente, destacando 'red flags' e justificando o nível de urgência.",
         agent=agente_risco,
         context=[tarefa_diagnostico, tarefa_exames],
         expected_output="Uma seção de 'Estratificação de Risco' com a classificação (ex: Baixo, Moderado, Alto) e os fatores que levaram a essa conclusão."
    )

    tarefa_relatorio = Task(
         description="Consolidar todas as análises prévias em um sumário clínico estruturado, destinado a um médico.",
         agent=agente_relator,
         context=[tarefa_diagnostico, tarefa_exames, tarefa_risco],
         expected_output="""Um sumário clínico em markdown com as seções:
         1. Sumário do Caso Clínico.
         2. Hipóteses Diagnósticas (Diferencial).
         3. Sugestões de Workup.
         4. Estratificação de Risco e Conduta Recomendada.
         5. Observações (para fins de suporte à decisão)."""
     )
    
    crew = Crew(
         agents=[agente_diagnostico, agente_exames, agente_risco, agente_relator],
         tasks=[tarefa_diagnostico, tarefa_exames, tarefa_risco, tarefa_relatorio],
         process=Process.sequential,
         verbose=True
    )
    
    resultado_final = crew.kickoff()
    return resultado_final