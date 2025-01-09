#   _KINE(MA)TICS_

## Documentação Técnica da aplicação de Análise de Arquivos OpenSim e Jumpy
---
## **Objetivos**
Realizar análise, processamento e comparação de dados biomecânicos de movimento gerados pelo open cap e dados de força extraídos da plataforma de força.

As principais funcionalidades incluem:
1. Análise de arquivos de aceleração (acp) gerados pela aplicação jumpy.
2. Análise de arquivos de movimento (.mot) gerados pelo open cap
3. Comparação entre sinais biomecânicos sincronizados e alinhados temporalmente.
4. Geração de gráficos e arquivos de saída com resultados analisados.

---

## **Bibliotecas Utilizadas**
- **`os`** e **`pathlib`**: Manipulação de caminhos e arquivos no sistema operacional.
- **`opensim`**: Análise de dados biomecânicos utilizando a biblioteca OpenSim.
- **`json`**: Manipulação de arquivos de configuração no formato JSON.
- **`time`**: Medição do tempo de execução.
- **`re`**: Uso de expressões regulares para extração de padrões em nomes de arquivos.
- **`resampy`**: Reamostragem de sinais para ajuste das taxas de amostragem.
- **`numpy`**: Estrutura e manipulação de conjuntos de dados
- **`matplotlib`**: Criação de gráficos


- **Módulos personalizados**:
- **`osim_functions`**:Funções para operação da API Open Sim por python
- **`post_process_functions`**: Funções de pós processamento para diferentes análises
- **`jumpy_functions`**: Funções retiradas e modificadas a partir da aplicação jumpy
- **`kinematic_class`**: Classe kinematic retirada da aplicação opencap-processing

As funções dos arquivos jumpy_functions e kinematic_class foram criadas por outros autores e adaptadas para esse projeto. Para as aplicações completas consulte as referências.


---

## **Utilização**

### 1. **Instalação**:
    - Existem diversos métodos para instalação python, para evitar complicações de permissões e variáveis de ambiente podemos realizar o download diretamente da [Windows store (Python 3.8)](https://apps.microsoft.com/detail/9mssztt1n39l?hl=pt-BR&gl=BR).

    - Para essa instalação, trabalharemos com um ambiente virtual, garantindo isolamento e consistência nas versões que serão utilizadas na aplicação,

- Ambiente virtual e numpy:
    
    Na pasta `\kmt`

    ```bash
    python3.8 -m pip install virtualenv
    python3.8 -m venv kmt

    .\kmt\Scripts\activate
    python -m pip install -U pip==24.0
    pip install numpy
    pip install setuptools==56.0.0
    ```

- Instalação das dependências do python para opensim:

    Para esse passo é necessário localizar o diretório onde foi instalado o OpenSim, substitua de acordo com a sua máquina.
    Exemplo: substitua a primeira linha por ```cd 'D:\OpenSim 4.5\sdk\Python'```

    ```bash
    cd <DIRETÓRIO OPENSIM>
    python setup_win_python38.py
    python -m pip install .
    ```

- Instalação de bibliotecas adicionais:
        ```bash
    pip install -r requirements.txt
    ```

ATENÇÃO: Para garantir o funcionamento da aplicação, é realizar os passos nessa ordem

### 2. **Estrutura de Diretórios**:
Para funcionamento correto, a aplicação espera certos padrões de organização de arquivos e pastas

   - Certifique-se de organizar os dados na seguinte estrutura:
     ```
     kmt/
     ├── data/
     │   ├── voluntario_1/
     │   │    ├── opencap/
     │   │    ├── jumpy/
     │   │    
     |   |
     │   └── voluntario_2/
     │        ├── opencap/
     │        ├── jumpy/
     │        

     ```
        - A. Diretório `opencap/` 
            Cada voluntário deve ter seu próprio diretório opencap. Para ele deve ser copiado o diretório `OpenSimData` recebido após processamento no OpenCap.
            Os arquivos do tipo `.mot` podem ter qualquer nome, desde que o *último caracter seja numérico* .

                ```
                opencap/
                ├── OpenSimData/
                │   ├── 
                │   │    ├──  Model/
                │   │    ├──  Kinematics/
                │   │         ├── opencap_salto_1.mot
                |   |         ├── opencap_salto_2.mot
                |   |         ├── opencap_salto_3.mot

                ```

        - B. Diretório `jumpy/` 
            Cada voluntário deve ter seu próprio diretório jumpy. Ele deve conter arquivos `.acp` adquiridos com o a aplicação jumpy. O número de arquivos nesse diretório deve ser igual ao número de arquivos de movimento do diretório `opencap`.
            Os arquivos do tipo `.acp` podem ter qualquer nome, desde que o *último caracter seja numérico*.



                ```
                jumpy/
                 ├── jumpy_salto_1.acp
                 ├── jumpy_salto_2.acp
                 ├── jumpy_salto_3.acp   

                ```

      - *ATENÇÃO* : O pareamento de arquivos Portanto, no exemplo, o arquivo opencap_salto_1.acp seria pareado com 
    jumpy_salto_1.mot pois ambos tem seu noé feito com base no último caracter no nome do arquivo (o número). me 
    terminado em "1".
    

### 3. **Execução do Código**:
   - Execute o script principal dentro da pasta `kmt/`:
     ```bash
     .\kmt\Scripts\activate
     python main.py
     ```

### 4. **Resultados**:
   - Os resultados das análises e comparações serão salvos no diretório de cada voluntário em um subdiretório `output/`:
     ```
     output/
     ├── oc_com/
     ├── jumpy_cmj/
     ├── compare/
     ```




---

## **Estrutura do Código**


### **Funções Principais**
#### 1. `opencap_file_analisys(mot_file_list, oc_directory, output_directory)`
Realiza análise dos arquivos `.mot` do OpenSim.
- **Entradas**:
  - `mot_file_list`: Lista de arquivos `.mot`.
  - `oc_directory`: Diretório com dados do OpenCap.
  - `output_directory`: Diretório para salvar os resultados.
- **Saídas**:
  - Gráficos e arquivos processados no diretório de saída.

#### 2. `jumpy_file_analisys(acp_file_list, output_directory)`
Realiza análise dos arquivos `.acp` do Jumpy.
- **Entradas**:
  - `acp_file_list`: Lista de arquivos `.acp`.
  - `output_directory`: Diretório para salvar os resultados.
- **Saídas**:
  - Gráficos e arquivos processados no diretório de saída.

#### 3. `plot_signals(oc_data, jp_data, cp_directory, file_name)`
Compara e cria gráficos dos dados biomecânicos sincronizados entre OpenSim e Jumpy.
- **Entradas**:
  - `oc_data`: Dados do OpenSim.
  - `jp_data`: Dados do Jumpy.
  - `cp_directory`: Diretório para salvar os resultados comparados.
  - `file_name`: Nome do arquivo de saída.
- **Saídas**:
  - Gráficos comparativos e métricas de erro.

#### 4. `main()`
Função principal que:
1. Configura diretórios e parâmetros.
2. Executa as análises e comparações.
3. Organiza os resultados em diretórios específicos.

---

## **Métodos**
- **Sincronização dos Dados**:
  A função `compare_signals` sincroniza os dados de posição, velocidade e aceleração com base no índice de altura máxima de cada conjunto de dados. 
- **Análise Opencap**:
  A análise dos dados recebidos pela captura de movimento é realizada utilizando métodos da classe Kinematics
  pertencente ao projeto opencap-processing

---

## **Referências**
- [OpenCap-Processing](https://github.com/stanfordnmbl/opencap-processing)
- [OpenSim](https://simtk.org/projects/opensim)
- Jumpy

---