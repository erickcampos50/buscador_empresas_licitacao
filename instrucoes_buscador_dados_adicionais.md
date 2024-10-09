### `requirements.txt`

To run the script successfully, the following Python packages are required. You can install them using `pip` with the command:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
pandas==2.0.0
requests==2.31.0
beautifulsoup4==4.12.2
argparse
```

### Manual de Uso

#### Descrição
Este script processa um arquivo CSV contendo CNPJs, acessa informações da API do Portal da Transparência e adiciona dados extraídos ao CSV original. Ele gera um novo arquivo CSV com as informações complementares.

#### Pré-requisitos

1. **Python 3.x** instalado.
2. Instalar os pacotes necessários listados em `requirements.txt` usando o comando:
   
   ```bash
   pip install -r requirements.txt
   ```

#### Instruções de Execução

1. **Entrada**:
   Prepare um arquivo CSV com uma coluna chamada `CNPJ` contendo os CNPJs a serem processados.

2. **Execução do Script**:
   Execute o script usando o terminal da seguinte forma:

   ```bash
   python script.py <caminho_arquivo_csv_entrada> <caminho_arquivo_csv_saida> [opções]
   ```

   Onde:
   - `<caminho_arquivo_csv_entrada>`: caminho para o arquivo CSV de entrada.
   - `<caminho_arquivo_csv_saida>`: caminho onde o arquivo CSV de saída será salvo.

   **Exemplo**:

   ```bash
   python script.py input.csv output.csv
   ```

3. **Opções**:
   - `--sep`: Define o separador de campos do CSV de entrada. O padrão é `,`.
   - `--encoding`: Define a codificação do arquivo CSV de entrada. O padrão é `utf-8`.

   **Exemplo com opções**:

   ```bash
   python script.py input.csv output.csv --sep ";" --encoding "latin1"
   ```

#### Logs e Monitoramento

Durante a execução, o script fornece mensagens detalhadas sobre o progresso e possíveis erros. As mensagens são exibidas no terminal e incluem:
- Informações sobre o processamento de cada CNPJ.
- Resultados das requisições à API.
- Erros ou problemas durante o processamento.

#### Cuidados e Limitações
- A API do Portal da Transparência pode impor limites de requisição ou bloquear acessos excessivos. Para evitar isso, o script faz uma pausa de 5 segundos entre as requisições.
- O script não lida com CNPJs inválidos ou mal formatados no arquivo de entrada. O arquivo deve conter CNPJs válidos na coluna especificada.
