"""
Módulo principal da aplicação de scraping do NYTimes.

Este módulo é responsável por orquestrar todo o fluxo de execução do sistema,
incluindo carregamento de configurações, inicialização do WebDriver Selenium,
execução do scraping e persistência dos dados extraídos em arquivo Excel.

Responsabilidades principais:
- Carregar configurações da aplicação
- Inicializar driver Selenium
- Executar fluxo de scraping no NYTimes
- Extrair artigos encontrados
- Persistir dados em Excel
"""

from time import sleep
import os
from datetime import datetime
from src.utils.logger import logger, setup_logger

from src.utils.config_loader import load_config
from src.services.selenium_driver import create_driver
from src.services.nyt_scraper import NYTimesScraper
from src.output.excel.excel_writer import save_articles_to_excel


def main():
    """
    Executa o fluxo principal da aplicação de scraping.

    Etapas do fluxo:
    1. Carregamento de configurações
    2. Inicialização do WebDriver
    3. Instanciação do scraper
    4. Execução do processo de busca e filtragem
    5. Extração de artigos
    6. Salvamento dos dados em Excel
    7. Encerramento do WebDriver
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_folder = os.path.join("output", timestamp)

    images_dir = os.path.join(run_folder, "images")
    excel_dir = os.path.join(run_folder, "excel")
    logs_dir = os.path.join(run_folder, "logs")

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(excel_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    setup_logger(logs_dir, run_id=timestamp, level="DEBUG")

    config = load_config()

    logger.info("Configuracoes carregadas com sucesso")
    logger.info(f"Frase de pesquisa: {config.get('search_phrase')}")
    logger.info(f"Categorias: {config.get('categories')}")
    logger.info(f"Meses: {config.get('months_range')}")
    logger.info(f"Execução em segundo plano: {config.get('browser_headless')}")

    driver = create_driver(
        browser=config.get("browser", "chrome"),
        headless=config.get("browser_headless")
    )

    try:
        scraper = NYTimesScraper(
            driver=driver,
            config=config,
            images_dir=images_dir
        )

        scraper.open_home()
        scraper.perform_search()
        scraper.apply_filters()
        scraper.apply_date_filter_to_current_url()
        articles = scraper.extract_results()

        logger.info(f"Total de artigos encontrados: {len(articles)}")

        if articles:
            logger.debug(f"Exemplo de artigo: {articles[0]}")

        logger.info(f"Salvando Excel em: {excel_dir}")

        save_articles_to_excel(
            articles,
            output_dir=excel_dir
        )

        logger.success("Arquivo Excel salvo com sucesso")
    finally:
        driver.quit()
        logger.info("Driver encerrado com sucesso")


if __name__ == "__main__":
    main()