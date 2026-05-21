# NYTimes RPA Search Scraper

Este é um robô de automação web (RPA) desenvolvido em Python e Selenium para extrair dados estruturados de artigos do portal **The New York Times**. O projeto foi projetado seguindo práticas consolidadas de engenharia de software e backend, apresentando isolamento de módulos, tratamento de erros resiliente, gerenciamento avançado de logs e suporte total à conteinerização.



## 🛠️ Guia de Configuração e Execução via Docker

O comportamento do robô é totalmente dinâmico e controlado por um arquivo de configuração centralizado. Usando o Docker, o ambiente é totalmente isolado e configurado de forma automatizada (instalação do Linux, Google Chrome e ChromeDriver compatível), rodando sem interface visual (`--headless`).

---

### 1. Parametrizando a Automação (`config/config.yaml`)

Antes de rodar o container, abra o arquivo `config/config.yaml` na sua máquina local e ajuste os parâmetros de busca. O Docker lerá esse arquivo dinamicamente antes de iniciar o robô:

```yaml
search_phrase: "Economy"   # Termos ou frases para pesquisar no portal (separe por vírgula se houver mais de um)
months_range: 2                      # Intervalo de meses para busca (0 ou 1 = mês atual; >= 2 = meses retroativos)
categories:                          # Lista de seções/categorias do jornal desejadas para filtragem
  - Business
  - Technology
```
---

### 2.Passo a Passo de Execução com Docker Compose

Pré-requisitos:
Docker instalado e rodando.

Docker Compose instalado.

Comandos para Execução:
1 - Acesse a pasta raiz do projeto no seu terminal:
```bash
    cd rpa_nytimes
```
2 - Construa a imagem e suba o ambiente conteinerizado:
```bash
    docker-compose up --build
```

3 - Acompanhe o processamento:
O terminal exibirá o fluxo detalhado de logs gerados em tempo real pelo Loguru dentro do container.

4 - Coleta de Resultados:
Assim que o container finalizar a extração e se encerrar automaticamente, todos os artefatos gerados estarão disponíveis diretamente na pasta local output/ do seu computador, graças ao mapeamento de volumes:

- output/: Planilha Excel gerada com os dados dos artigos.

- output/images/: Todas as imagens dos cards de notícias baixadas e renomeadas.

- output/logs/: Arquivos de log detalhados salvos pelo Loguru.


## 📂 Estrutura do Projeto

```text
rpa_nytimes/
├── config/
│   └── config.yaml               # Arquivo central de parametrização (termo de busca, meses, categorias)
├── output/                       # Diretório gerado para armazenar os relatórios e imagens extraídas
├── src/
│   ├── app/
│   │   └── main.py               # Ponto de entrada (Orquestrador do Fluxo)
│   ├── output/
│   │   └── excel/
│   │       └── excel_writer.py   # Componente de escrita de dados em planilhas
│   ├── services/
│   │   ├── nyt_scraper.py        # Logica de negócios e extração de dados do portal
│   │   └── selenium_driver.py    # Gerenciamento de inicialização e ciclo de vida do WebDriver
│   └── utils/
│       ├── config_loader.py      # Carregamento e parse seguro do arquivo YAML
│       ├── date_format.py        # Normalização cronológica do portal para o formato brasileiro
│       ├── images_download.py    # Gestão de requisições HTTP e salvamento de mídias
│       ├── logger.py             # Configuração centralizada de logs (Loguru)
│       └── text_utils.py         # Análise textual (contagem de termos e verificação monetária)
├── Dockerfile                    # Configuração da imagem do container (Instalação de dependências e Chrome)
├── docker-compose.yml            # Orquestração do ambiente conteinerizado em modo Headless
├── requirements.txt              # Dependências fixadas do projeto
└── README.md                     # Documentação do sistema