import pandas as pd
from chatMed import rodar_analise_completa
import time

def executar_testes_automaticos(caminho_dataset):
    """
    Lê um dataset de personas, executa a análise para cada caso e gera um relatório.
    """
    print(f"Carregando dataset de testes de '{caminho_dataset}'...")
    try:
        df = pd.read_csv(caminho_dataset)
    except FileNotFoundError:
        print(f"ERRO: Dataset não encontrado. Verifique se o arquivo '{caminho_dataset}' está na pasta correta.")
        return

    print(f"Dataset carregado. {len(df)} personas para analisar.")
    
    resultados = []

    for index, linha in df.iterrows():
        id_caso = linha['id_caso']
        diagnostico_esperado = linha['diagnostico_esperado']
        descricao_clinica = linha['descricao_clinica']
        
        print(f"\n[TESTE {id_caso}/{len(df)}] Iniciando análise para: {diagnostico_esperado}")

        try:
            # Passamos a descrição clínica diretamente para a nossa função principal
            relatorio_ia = rodar_analise_completa(descricao_clinica)
            
            print(f"  - Análise do caso '{diagnostico_esperado}' concluída com sucesso.")
            resultados.append({
                'id_caso': id_caso,
                'diagnostico_esperado': diagnostico_esperado,
                'relatorio_da_ia': relatorio_ia
            })
        except Exception as e:
            print(f"  - ERRO na análise do caso '{diagnostico_esperado}': {e}")
            resultados.append({
                'id_caso': id_caso,
                'diagnostico_esperado': diagnostico_esperado,
                'relatorio_da_ia': f"FALHA NA ANÁLISE: {e}"
            })
        print("  - Aguardando 20 segundos para a próxima requisição...")
        time.sleep(20)

    # Salva todos os resultados no relatório final
    df_resultados = pd.DataFrame(resultados)
    caminho_saida = 'relatorio_precisao_ia.csv'
    df_resultados.to_csv(caminho_saida, index=False, encoding='utf-8-sig')
    
    print(f"\nTestes automáticos finalizados. O relatório foi salvo em '{caminho_saida}'.")

# --- Ponto de entrada do script ---
if __name__ == "__main__":
    executar_testes_automaticos('dataset.csv')