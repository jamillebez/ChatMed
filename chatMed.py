import os
from dotenv import load_dotenv # Para carregar variáveis de ambiente do arquivo .env
from crewai import Agent, Task, Crew
from langchain_community.chat_models.litellm import ChatLiteLLM

# ==============================================================================
# CARREGAR VARIÁVEIS DE AMBIENTE (ESPECIALMENTE A API KEY)
# ==============================================================================
load_dotenv() # Carrega variáveis do arquivo .env para o ambiente
my_google_api_key = os.getenv("GOOGLE_API_KEY")

if not my_google_api_key:
    raise ValueError("Chave de API do Google (GOOGLE_API_KEY) não encontrada. "
                     "Certifique-se de que ela está definida no arquivo .env ou como variável de ambiente.")

# ==============================================================================
# INSTANCIAÇÃO DO LLM
# ==============================================================================
llm = ChatLiteLLM(
    model="gemini/gemini-1.5-flash",
    api_key=my_google_api_key # Usa a chave carregada
)

# ==============================================================================
# AVISO IMPORTANTE DE SEGURANÇA E RESPONSABILIDADE
# (Mantenha este aviso)
# ==============================================================================
# Este código é uma demonstração tecnológica e NÃO um substituto para
# aconselhamento médico profissional, diagnóstico ou tratamento.
# SEMPRE CONSULTE UM MÉDICO QUALIFICADO PARA QUESTÕES DE SAÚDE.
# ==============================================================================

def analisar_sintomas_com_crewai(sintomas_do_paciente_str: str) -> str:
    """
    Função que encapsula a lógica do CrewAI para analisar sintomas.
    Recebe uma string de sintomas e retorna o relatório final.
    """

    analista_de_sintomas = Agent(
        role="Analista de Sintomas Clínicos",
        goal="Extrair e listar de forma clara todos os sintomas mencionados na descrição de um paciente.",
        backstory="Você é um especialista em triagem médica, treinado para identificar os principais pontos nas queixas dos pacientes.",
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

    pesquisador_diagnosticos = Agent(
        role="Pesquisador de Diagnósticos Médicos",
        goal="Com base em uma lista de sintomas, pesquisar possíveis diagnósticos e suas causas. Sempre enfatize que não é um diagnóstico definitivo.",
        backstory="Você é um pesquisador médico meticuloso que correlaciona sintomas a possíveis condições médicas.",
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

    especialista_encaminhamento = Agent(
        role="Especialista em Encaminhamento Médico",
        goal="Analisar os possíveis diagnósticos e sugerir os tipos de especialistas médicos mais adequados.",
        backstory="Você é um profissional experiente da área da saúde que guia o paciente, indicando o especialista correto.",
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

    tarefa_analise_sintomas = Task(
        description=f"Analise a seguinte descrição de um paciente e liste todos os sintomas encontrados:\n\n---\n{sintomas_do_paciente_str}\n---",
        agent=analista_de_sintomas,
        expected_output="Uma lista em tópicos (bullet points) com cada sintoma identificado."
    )

    tarefa_pesquisa_diagnosticos = Task(
        description="Usando a lista de sintomas fornecida, investigue e crie um relatório sobre possíveis diagnósticos.",
        agent=pesquisador_diagnosticos,
        context=[tarefa_analise_sintomas],
        expected_output="Um relatório estruturado contendo 'Possíveis Diagnósticos', 'Causas Comuns', 'Descrição' e um aviso claro de que não é uma avaliação médica."
    )

    tarefa_sugestao_encaminhamento = Task(
        description="Com base no relatório de possíveis diagnósticos, recomende quais especialidades médicas o paciente deve procurar e explique o motivo.",
        agent=especialista_encaminhamento,
        context=[tarefa_pesquisa_diagnosticos],
        expected_output="Uma seção final chamada 'Próximos Passos e Encaminhamento' com uma lista de especialistas e a justificativa para cada um."
    )

    equipe_medica = Crew(
        agents=[analista_de_sintomas, pesquisador_diagnosticos, especialista_encaminhamento],
        tasks=[tarefa_analise_sintomas, tarefa_pesquisa_diagnosticos, tarefa_sugestao_encaminhamento],
        verbose=False
    )

    print("Iniciando análise de saúde com CrewAI (local)...")
    resultado_final = equipe_medica.kickoff()
    print("Análise concluída (local).")
    return resultado_final

# Bloco para testar este script isoladamente (opcional)
if __name__ == "__main__":
    sintomas_teste_local = """
    Febre alta há 2 dias, dor de garganta intensa e dificuldade para engolir.
    Também notei pequenas manchas vermelhas na pele.
    """
    print("Executando teste local do script CrewAI...")
    relatorio_teste = analisar_sintomas_com_crewai(sintomas_teste_local)
    print("\n\n##################################")
    print("## Relatório Final do Teste Local:")
    print("##################################\n")
    print(relatorio_teste)