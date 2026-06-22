# Pipeline principal de processamento de transações
# Executa o fluxo: extração -> transformação -> salvamento -> carga

import pandas as pd
from extract import ler_csv
from transform import tratar_transacoes
from load import carregar_transacoes_mysql


def main():
    # Caminhos dos arquivos
    camho_entrada = 'data/raw/transacoes_exemplo.csv'
    caminho_saida = 'data/processed/transacoes_tratadas.csv'
    
    try:
        # Início do pipeline
        print("=== Iniciando pipeline de processamento ===")
        
        # 1. Leitura do CSV bruto
        print(f"Lendo arquivo: {camho_entrada}")
        df_bruto = ler_csv(camho_entrada)
        print(f"Registros lidos: {len(df_bruto)}")
        
        # 2. Tratamento dos dados
        print("Tratando dados...")
        df_tratado = tratar_transacoes(df_bruto)
        print(f"Registros tratados: {len(df_tratado)}")
        
        # 3. Salvamento do arquivo tratado
        print(f"Salvando arquivo tratado em: {caminho_saida}")
        df_tratado.to_csv(caminho_saida, index=False)
        
        # 4. Carga dos dados no MySQL
        print("Carregando dados no MySQL...")
        carregar_transacoes_mysql(df_tratado)
        
        # Finalização com sucesso
        print("=== Pipeline finalizado com sucesso ===")
        
    except Exception as e:
        # Exibe mensagem de erro
        print("=== Pipeline falhou ===")
        print(f"Erro: {e}")


if __name__ == '__main__':
    main()
