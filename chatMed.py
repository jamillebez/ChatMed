import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.chat_models.litellm import ChatLiteLLM

# ==============================================================================
# CARREGAR VARIÁVEIS DE AMBIENTE E INSTANCIAR LLM
# (Nenhuma mudança aqui)
# ==============================================================================
load_dotenv()
my_google_api_key = os.getenv("GOOGLE_API_KEY")

if not my_google_api_key:
    raise ValueError("Chave de API do Google (GOOGLE_API_KEY) não encontrada.")

llm = ChatLiteLLM(
    model="gemini/gemini-1.5-flash",
    api_key=my_google_api_key
)

# ==============================================================================
# AGENTE CONVERSACIONAL
# ==============================================================================
assistente_medico_conversacional = Agent(
    role="Assistente Médico Conversacional de IA",
    goal="""Conduzir uma conversa amigável e empática com o usuário para entender seus sintomas. 
    Fazer perguntas de acompanhamento claras e relevantes.
    
    ***NOVA HABILIDADE: Se o usuário fornecer o conteúdo de um documento (como um exame de sangue), analise os dados contidos nele, correlacione com os sintomas descritos e responda às perguntas sobre eles.***

    Quando tiver informações suficientes, fornecer uma análise preliminar, possíveis condições (deixando claro que não é um diagnóstico) e sugerir os próximos passos, como procurar um especialista.
    Manter um tom tranquilizador e sempre, SEMPRE, reforçar que não é um médico real e que a consulta com um profissional de saúde é indispensável.""",
    backstory="""Você é um assistente de IA avançado... (o resto do backstory continua igual)""",
    verbose=False,
    allow_delegation=False,
    llm=llm
)

# ==============================================================================
# NOVA FUNÇÃO PARA O CHAT INTERATIVO
# Esta função gerencia uma única troca na conversa.
# ==============================================================================
def obter_resposta_conversacional(historico_conversa: list) -> str:
    """
    Processa o histórico da conversa e a última mensagem do usuário para gerar uma resposta.

    Args:
        historico_conversa: Uma lista de dicionários representando a conversa até agora.
                            Ex: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    Returns:
        A resposta do agente de IA como uma string.
    """
    print("Analisando o histórico da conversa para gerar uma nova resposta...")

    # Converte o histórico da conversa para um formato de string que a Task entenda
    contexto_conversa = "\n".join([f"{msg['role']}: {msg['content']}" for msg in historico_conversa])

    tarefa_conversacional = Task(
        description=f"""Continue esta conversa de forma útil e segura. Aqui está o histórico até agora:
        ---
        {contexto_conversa}
        ---
        Baseado no histórico, sua função e a última mensagem do usuário, gere a próxima resposta apropriada.
        Se o usuário acabou de cumprimentar, apresente-se e explique seu propósito.
        Se o usuário descreveu sintomas, faça perguntas de acompanhamento (Ex: 'Há quanto tempo você tem isso?', 'A dor é constante ou vai e vem?', 'Você tem outros sintomas?').
        Se você já coletou informações suficientes, resuma os sintomas, sugira possíveis áreas de investigação (sem diagnosticar) e recomende fortemente a busca por um especialista específico (ex: Clínico Geral, Cardiologista).
        """,
        agent=assistente_medico_conversacional,
        expected_output="Uma única resposta em texto, formatada em markdown, para continuar a conversa com o usuário."
    )

    # Para um único agente executando uma tarefa, não precisamos de um 'Crew'.
    # Usamos diretamente o executor da tarefa.
    resultado = assistente_medico_conversacional.execute_task(tarefa_conversacional)
    
    print("Resposta gerada.")
    return resultado