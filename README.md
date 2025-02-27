#   _KINE(MA)TICS_

## Documentação Kinem(ma)tics, aplicação para análise de arquivos de dados Cinéticos e Cinemáticos
---
## **Objetivos**
Realizar análise, processamento e comparação de dados biomecânicos de movimento extraídos por software de captura de movimento e dados de força extraídos por plataforma de força.

As principais funcionalidades incluem:
1. Análise de arquivos de aceleração (acp) gerados pela aplicação jumpy com coleta de dados por plataforma de força.
2. Análise de arquivos de movimento (.mot) gerados pelo OpenCap utilizando ferramentas do OpenSim.
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

## **Coleta**
Durante a coleta de dados, é necessário que o voluntário permaneça com o corpo completamente estático por um segundo e meio. Edite o vídeo OpenCap e dados Jumpy para que esse momento estático ocorra no início dos dados.

## **Utilização**

### 1. **Instalação**:
*A. Pré-requisitos:*

- OpenSim: [Manual de instalação OpenSim](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53088790/Installing+OpenSim)
    
- Python 3.8: [Windows store - Python 3.8](https://apps.microsoft.com/detail/9mssztt1n39l?hl=pt-BR&gl=BR). 

*B. Aplicação:*

- Ambiente virtual e numpy:
  
    Trabalharemos com um ambiente virtual, garantindo isolamento e consistência nas versões utilizadas na aplicação.

    No diretório principal `Kine-ma-tics/`

    ``` bash
    python3.8 -m pip install virtualenv
    python3.8 -m venv kmt
    .\kmt\Scripts\activate
    python -m pip install -U pip==24.0
    pip install numpy==1.24.4
    pip install setuptools==56.0.0
    ```

- Instalação das dependências do python para opensim:

    Para esse passo é necessário localizar o diretório onde foi instalado o OpenSim, substitua de acordo com a sua máquina.
  
    Exemplo: substitua a primeira linha por ```cd 'D:\OpenSim 4.5\sdk\Python'```

    ```bash
    cd <DIRETÓRIO OPENSIM PYTHON>
    python setup_win_python38.py
    python -m pip install .
    ```

- Instalação de bibliotecas adicionais:
    **Volte ao diretório Kine-ma-tics:**
    ```bash
    pip install -r requirements.txt
    ```

ATENÇÃO: Para garantir o funcionamento da aplicação, é realizar os passos nessa ordem. Em caso de problemas, consulte o manual [Instalação de bindings python](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53085346/Scripting+in+Python)

### 2. **Estrutura de Diretórios**:
Para funcionamento correto, a aplicação espera certos padrões de organização de arquivos e pastas

   - Certifique-se de organizar os dados na seguinte estrutura:
     ```
     Kine-ma-tics/
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
        - *A. Diretório `opencap/`*
          
            Cada voluntário deve ter seu próprio diretório opencap. Para ele deve ser copiado o diretório `OpenSimData` recebido após processamento no OpenCap.
            Os arquivos do tipo `.mot` podem ter qualquer nome, desde que o **último caracter seja numérico** .

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

        - *B. Diretório `jumpy/`*
          
            Cada voluntário deve ter seu próprio diretório jumpy. Ele deve conter arquivos `.acp` adquiridos com o a aplicação jumpy. O número de arquivos nesse diretório deve ser igual ao número de arquivos de movimento do diretório `opencap`.
            Os arquivos do tipo `.acp` podem ter qualquer nome, desde que o **último caracter seja numérico**.



                ```
                jumpy/
                 ├── jumpy_salto_1.acp
                 ├── jumpy_salto_2.acp
                 ├── jumpy_salto_3.acp   

                ```

      - *ATENÇÃO* : O pareamento de dados de movimento e de aceleração para comparação é realizado com base no sufixo numérico do nome do arquivo. No exemplo, o arquivo opencap_salto_1.acp seria pareado com jumpy_salto_1.mot pois ambos tem seu nome terminado em "1".
    

### 3. **Execução do Código**:
   - Abra o diretório `Kine-ma-tics/` no terminal:
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

## **Processamento**:

*A. Processamento de posição*:

- Os arquivo de movimento (`.mot`) gerados pelo OpenCap serão processados utilizando uma adaptação da classe Kinematics de [OpenCap-Processing](https://github.com/stanfordnmbl/opencap-processing), os dados tratados por filtro butterworth de quarta ordem com frequência de corte de 10Hz. A velocidade e aceleração são derivadas a partir da posição.
São gerados gráficos desse conjunto na pasta específica no diretório `output/`
    
*B. Processamento de aceleração*:
- Baseado no processamento realizado pela aplicação jumpy, os dados de aceleração são tratados com filtro Butterworth de quarta ordem e frequência de corte de 30Hz, posteriormente, são integrados para obter os sinais de velocidade e deslocamento.
São gerados gráficos desse conjunto na pasta específica no diretório `output/`
    

*C. Comparação de dados*
- Os dados de posição, velocidade e aceleração são alinhados em um mesmo ponto, dado pelo melhor índice de correlação entre as curvas de posição das diferentes fontes.
- Os dados com maior taxa de amostragem (adquiridos pela plataforma de força) sofrem downsample para a taxa de amostragem dos dados adquiridos pelo opencap (60 Hz).
- A partir dos sinais gerados pelas análises anteriores, são traçados gráficos de comparação entre o aceleração, velocidade e posição entre métodos de aquisição (OpenCap e Jumpy)
- É calculado o erro médio absoluto normalizado pela amplitude máxima para todos as comparações.




## **Referências**
- [OpenCap-Processing](https://github.com/stanfordnmbl/opencap-processing)
- [OpenSim](https://simtk.org/projects/opensim)
- Jumpy


---