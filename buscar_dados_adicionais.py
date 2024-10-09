#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from bs4 import BeautifulSoup
import argparse
import re
import sys
import time
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuração de Logging para mensagens detalhadas
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def limpar_cnpj(cnpj):
    """Remove caracteres não numéricos do CNPJ."""
    return re.sub(r'\D', '', str(cnpj))

def extrair_dados(html_content):
    """Extrai os dados de interesse do HTML retornado pela API."""
    soup = BeautifulSoup(html_content, 'html.parser')
    dados = {}
    
    # Função auxiliar para extrair texto após uma tag <strong>
    def get_text_after_strong(label):
        tag = soup.find('strong', text=label)
        if tag and tag.find_next_sibling('span'):
            return tag.find_next_sibling('span').get_text(strip=True)
        return None

    # Extrair campos de interesse
    dados['Número de inscrição'] = get_text_after_strong('Número de inscrição')
    dados['Data de abertura'] = get_text_after_strong('Data de abertura')
    dados['Endereço eletrônico'] = get_text_after_strong('Endereço eletrônico')
    dados['Telefone'] = get_text_after_strong('Telefone')
    dados['Nome empresarial'] = get_text_after_strong('Nome empresarial')
    dados['Nome de fantasia'] = get_text_after_strong('Nome de fantasia')
    dados['Natureza jurídica'] = get_text_after_strong('Natureza jurídica')
    dados['CNAE'] = get_text_after_strong('CNAE')
    dados['Logradouro'] = get_text_after_strong('Logradouro')
    dados['Número'] = get_text_after_strong('Número')
    dados['Complemento'] = get_text_after_strong('Complemento')
    dados['CEP'] = get_text_after_strong('CEP')
    dados['Bairro/Distrito'] = get_text_after_strong('Bairro/Distrito')
    dados['Município'] = get_text_after_strong('Município')
    dados['UF'] = get_text_after_strong('UF')

    return dados

def criar_sessao():
    """Cria uma sessão de requests com retries e headers para simular um navegador real."""
    session = requests.Session()
    
    # Definir retries para lidar com falhas temporárias
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Definir headers para simular um navegador real
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/112.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;' +
                  'q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,' +
                  'application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive'
    })
    
    return session

def processar_cnpjs(df, session):
    """Processa cada CNPJ no dataframe, faz requisição à API e extrai os dados."""
    # Listas para armazenar os novos dados
    novos_dados = {
        'Número de inscrição': [],
        'Data de abertura': [],
        'Endereço eletrônico': [],
        'Telefone': [],
        'Nome empresarial': [],
        'Nome de fantasia': [],
        'Natureza jurídica API': [],
        'CNAE API': [],
        'Logradouro API': [],
        'Número API': [],
        'Complemento API': [],
        'CEP API': [],
        'Bairro/Distrito API': [],
        'Município API': [],
        'UF API': []
    }

    total = len(df)
    for index, row in df.iterrows():
        cnpj_original = row['CNPJ']
        cnpj = limpar_cnpj(cnpj_original)
        logging.info(f"Processando CNPJ {index+1}/{total}: {cnpj_original} -> {cnpj}")

        url = f"https://portaldatransparencia.gov.br/busca/pessoa-juridica/{cnpj}"
        logging.info(f"    Fazendo requisição para URL: {url}")

        try:
            response = session.get(url, timeout=10, allow_redirects=True)
            # Verifica se houve redirecionamento
            if response.history:
                logging.info(f"    Redirecionado para {response.url}")
            if response.status_code == 200:
                logging.info("    Requisição bem-sucedida. Extraindo dados...")
                dados = extrair_dados(response.text)
                # Adiciona os dados extraídos às listas correspondentes
                novos_dados['Número de inscrição'].append(dados.get('Número de inscrição'))
                novos_dados['Data de abertura'].append(dados.get('Data de abertura'))
                novos_dados['Endereço eletrônico'].append(dados.get('Endereço eletrônico'))
                novos_dados['Telefone'].append(dados.get('Telefone'))
                novos_dados['Nome empresarial'].append(dados.get('Nome empresarial'))
                novos_dados['Nome de fantasia'].append(dados.get('Nome de fantasia'))
                novos_dados['Natureza jurídica API'].append(dados.get('Natureza jurídica'))
                novos_dados['CNAE API'].append(dados.get('CNAE'))
                novos_dados['Logradouro API'].append(dados.get('Logradouro'))
                novos_dados['Número API'].append(dados.get('Número'))
                novos_dados['Complemento API'].append(dados.get('Complemento'))
                novos_dados['CEP API'].append(dados.get('CEP'))
                novos_dados['Bairro/Distrito API'].append(dados.get('Bairro/Distrito'))
                novos_dados['Município API'].append(dados.get('Município'))
                novos_dados['UF API'].append(dados.get('UF'))
                logging.info("    Dados extraídos com sucesso.")
            else:
                logging.warning(f"    Falha na requisição. Status Code: {response.status_code}")
                # Adiciona valores nulos para os campos
                for key in novos_dados:
                    novos_dados[key].append(None)
        except requests.exceptions.RequestException as e:
            logging.error(f"    Ocorreu um erro durante a requisição: {e}")
            # Adiciona valores nulos para os campos
            for key in novos_dados:
                novos_dados[key].append(None)

        # Aguardar 5 segundos entre as requisições para evitar sobrecarga no servidor
        time.sleep(5)

    # Adiciona as novas colunas ao dataframe
    for key, value in novos_dados.items():
        df[key] = value

    return df

def main():
    parser = argparse.ArgumentParser(
        description='Script para complementar dados de empresas com informações da API do Portal da Transparência.'
    )
    parser.add_argument('input_csv', help='Caminho para o arquivo CSV de entrada')
    parser.add_argument('output_csv', help='Caminho para salvar o arquivo CSV de saída')
    parser.add_argument('--sep', default=',', help='Separador de campos do CSV de entrada (default: ",")')
    parser.add_argument('--encoding', default='utf-8', help='Codificação do arquivo CSV de entrada (default: "utf-8")')
    args = parser.parse_args()

    logging.info("Iniciando o processamento do CSV.")

    try:
        # Use o engine 'python' para suportar separadores complexos
        df = pd.read_csv(
            args.input_csv,
            sep=args.sep,
            engine='python',
            dtype=str,
            encoding=args.encoding,
            quotechar='"',
            escapechar='\\',
            on_bad_lines='warn'  # Substitui error_bad_lines e warn_bad_lines
        )
        logging.info(f"Arquivo CSV '{args.input_csv}' carregado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao carregar o arquivo CSV: {e}")
        sys.exit(1)

    # Verifica se a coluna 'CNPJ' existe
    if 'CNPJ' not in df.columns:
        logging.error("A coluna 'CNPJ' não foi encontrada no arquivo CSV.")
        sys.exit(1)

    logging.info("Formatando a coluna CNPJ para manter apenas números.")
    df['CNPJ'] = df['CNPJ'].apply(limpar_cnpj)
    logging.info("Coluna CNPJ formatada com sucesso.")

    # Criar uma sessão com configurações avançadas
    session = criar_sessao()

    logging.info("Iniciando a complementação dos dados através da API.")
    df_completo = processar_cnpjs(df, session)
    logging.info("Complementação dos dados concluída.")

    logging.info(f"Salvando o dataframe atualizado no arquivo '{args.output_csv}'.")
    try:
        # Use o mesmo separador para o arquivo de saída
        df_completo.to_csv(args.output_csv, index=False, sep=args.sep, encoding='utf-8')
        logging.info("Arquivo CSV salvo com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo CSV: {e}")
        sys.exit(1)

    logging.info("Processo concluído com sucesso.")

if __name__ == "__main__":
    main()
