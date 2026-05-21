"""
Módulo do Web Scraper do New York Times.

Este módulo contém a classe NYTimesScraper, responsável por orquestrar
a automação do navegador web utilizando Selenium para realizar buscas,
aplicar filtros e extrair metadados de artigos no site do NYT.
"""

import os
from datetime import datetime, timedelta
from time import sleep
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from dateutil.relativedelta import relativedelta
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.date_format import convert_nyt_date
from src.utils.images_download import download_image
from src.utils.logger import logger
from src.utils.text_utils import contains_money, count_search_phrases


class NYTimesScraper:
    """
    Classe responsável por realizar o scraping de artigos do New York Times.

    Automatiza o fluxo de interações com o portal do NYT desde a aceitação
    de cookies, execução de termos de busca, filtragem por categorias e
    extração detalhada dos cards de notícias retornados.
    """

    def __init__(self, driver: WebDriver, config: dict, images_dir: str):
        """
        Inicializa o NYTimesScraper com o driver e as configurações necessárias.

        Args:
            driver (WebDriver): Instância activa do WebDriver do Selenium.
            config (dict): Dicionário contendo as diretrizes de busca e execução.
            images_dir (str): Caminho do diretório para armazenamento de imagens baixadas.
        """
        logger.info("Inicializando a classe NYTimesScraper")
        
        self.driver = driver
        self.config = config

        logger.debug("Configurando WebDriverWait com timeout de 12 segundos")
        self.wait = WebDriverWait(self.driver, 12)

        self.site_url = config.get("site_url", "https://www.nytimes.com/")
        self.search_phrase = config.get("search_phrase", "")
        self.categories = config.get("categories", [])
        self.months_range = config.get("months_range", 1)

        self.images_dir = images_dir

        logger.debug(f"Instancia criada com URL: {self.site_url}, Termo: '{self.search_phrase}', Meses: {self.months_range}")


    def safe_click(self, by: By, locator: str, retries: int = 3, delay: float = 1.0) -> bool:
        """
        Tenta clicar em um elemento capturando falhas de Stale Element.

        Se o elemento ficar obsoleto, realiza uma nova busca no DOM.

        Args:
            by (By): Tipo de localizador (ex: By.XPATH, By.ID).
            locator (str): String de identificação do elemento.
            retries (int): Número de tentativas de clique antes de falhar.
            delay (float): Tempo de espera em segundos entre as tentativas.

        Returns:
            bool: Verdadeiro se o clique ocorreu com sucesso, Falso caso contrário.
        """
        for tentativa in range(1, retries + 1):
            try:
                logger.debug(f"Tentativa {tentativa}/{retries} de clicar no elemento: {locator}")
                
                element = self.wait.until(
                    EC.element_to_be_clickable((by, locator))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                sleep(0.2)
                element.click()
                
                return True
                
            except StaleElementReferenceException as e:
                logger.warning(
                    f"Elemento {locator} ficou obsoleto (stale) na tentativa {tentativa}. "
                    f"Aguardando {delay}s antes de redefinir a busca no DOM..."
                )
                if tentativa == retries:
                    raise RuntimeError(f"Elemento {locator} ficou obsoleto permanentemente apos {retries} tentativas.") from e
                sleep(delay)
                
            except TimeoutException as e:
                logger.warning(f"Timeout ao tentar localizar elemento clicavel: {locator} na tentativa {tentativa}.")
                if tentativa == retries:
                    raise TimeoutException(f"Nao foi possivel localizar o elemento clicavel {locator} dentro do tempo limite.") from e
                sleep(delay)
                
            except Exception as e:
                logger.error(f"Erro inesperado ao clicar no elemento {locator}: {e}")
                if tentativa == retries:
                    raise RuntimeError(f"Falha critica e inesperada ao interagir com o elemento {locator}.") from e
                sleep(delay)

        logger.error(f"Falha definitiva: Nao foi possivel clicar no elemento {locator} apos {retries} tentativas.")
        raise RuntimeError(f"Nao foi possivel clicar no elemento {locator} apos {retries} tentativas.")


    def open_home(self):
        """
        Abre a página inicial do New York Times e tenta aceitar os termos de cookies.
        """
        logger.info(f"Navegando para a URL inicial: {self.site_url}")
        try:
            self.driver.get(self.site_url)
        except Exception as e:
            logger.error(f"Erro ao carregar a URL inicial {self.site_url}: {e}")
            raise RuntimeError(f"Nao foi possivel carregar o site: {self.site_url}") from e

        try:
            self.safe_click(By.XPATH, '(//button[@id="fides-accept-all-button"])[2]', retries=2, delay=1.0)
            logger.info("Cookies aceitos ou validados com safe_click!")
        except Exception as e:
            logger.info("Popup de cookies nao encontrado - seguindo fluxo.")
            raise RuntimeError("Falha ao aceitar os cookies do site.") from e


    def perform_search(self):
        """
        Aciona o botão de busca da interface e submete a frase de pesquisa configurada.
        """
        logger.info(f"Iniciando pesquisa com o termo: '{self.search_phrase}'")
        try:
            self.safe_click(By.XPATH, '//button[@data-testid="search-button"]')

            input_field = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="search-input"]//input[@data-testid="search-input"]')
                )
            )
            input_field.send_keys(self.search_phrase)
            input_field.send_keys(Keys.ENTER)
            logger.info("Termo de busca enviado com sucesso.")

        except Exception as e:
            logger.error(f"Erro ao realizar a pesquisa: {e}")
            raise RuntimeError(f"Falha ao realizar a busca pelo termo '{self.search_phrase}'") from e
        

    def apply_filters(self):
        """
        Abre os menus rapidamente para capturar os IDs reais do NYT (como o hash de Business),
        constrói a URL final e navega diretamente, evitando cliques que recarregam a página.

        Returns:
            str: A nova URL gerada com os filtros aplicados.

        Raises:
            RuntimeError: Caso ocorra alguma falha crítica no mapeamento de categorias ou na montagem da URL.
        """
        logger.info("Iniciando mapeamento dos IDs do NYT para aplicacao via URL...")

        sections_to_apply = []

        try:
            sleep(6)
            self.safe_click(By.XPATH, '//button[@id="search-sections"]')

            filters_list = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//li[@data-testid='facet-filter-option']")
                )
            )

            ui_category_map = {}
            for item in filters_list:
                try:
                    label = item.find_element(By.TAG_NAME, "span").text.strip().lower()
                    real_value = item.get_attribute("data-value") 
                    
                    if label and real_value:
                        ui_category_map[label] = real_value
                except Exception:
                    continue

            for category in self.categories:
                category_normalized = category.strip().lower()
                if category_normalized in ui_category_map:
                    real_val = ui_category_map[category_normalized]
                    sections_to_apply.append(real_val)
                    logger.info(f"ID encontrado para '{category}': {real_val}")
                else:
                    logger.warning(f"Categoria '{category}' nao encontrada nas opcoes do HTML.")

            self.safe_click(By.XPATH, '//button[@id="search-sections"]')

        except Exception as e:
            logger.error(f"Erro ao mapear os IDs das categorias no HTML: {e}")
            raise RuntimeError("Falha critica ao mapear categorias no DOM do NYTimes.") from e

        try:
            current_url = self.driver.current_url
            url_parts = list(urlparse(current_url))
            query_params = parse_qs(url_parts[4])

            query_params["sort"] = ["newest"]

            if sections_to_apply:
                query_params["sections"] = sections_to_apply
                logger.info(f"Injetando as secoes capturadas na URL: {sections_to_apply}")

            url_parts[4] = urlencode(query_params, doseq=True)
            new_url = urlunparse(url_parts)

            logger.info(f"Navegando para a URL final do NYT: {new_url}")
            self.driver.get(new_url)

            logger.info("Aguardando 5 segundos para validacao visual na tela...")
            sleep(5)

            return new_url

        except Exception as e:
            logger.error(f"Erro ao aplicar os parametros na URL final: {e}")
            raise RuntimeError(f"Nao foi possivel construir ou navegar para a URL filtrada: {e}") from e


    def apply_date_filter_to_current_url(self):
        """
        Aplica filtros de data conforme a regra de range de meses definida no desafio:
        - months_range 0 ou 1 -> mes atual
        - months_range >= 2 -> inclui meses anteriores, contando sempre
            a partir do 1o dia do mes (N-1) meses atras.

        Returns:
            str: A URL modificada com os parâmetros de data injetados.

        Raises:
            RuntimeError: Se houver falha ao ler a URL atual ou parsear as datas de corte.
        """
        logger.info("Iniciando calculo e aplicacao dos filtros de data via URL...")

        try:
            current_url = self.driver.current_url

            today = datetime.today()
            months = int(self.months_range)

            if months <= 1:
                start_date_dt = today.replace(day=1)
                logger.info("Filtro de data configurado apenas para o mes atual.")
            else:
                start_date_dt = today.replace(day=1) - relativedelta(months=(months - 1))
                logger.info(f"Filtro de data configurado para os ultimos {months} meses.")

            start_date = start_date_dt.strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")

            logger.debug(f"Intervalo de busca definido: de {start_date} ate {end_date}")

            url_parts = list(urlparse(current_url))
            query_params = parse_qs(url_parts[4])

            query_params["startDate"] = [start_date]
            query_params["endDate"] = [end_date]

            url_parts[4] = urlencode(query_params, doseq=True)
            new_url = urlunparse(url_parts)

            logger.info(f"Navegando para URL com filtro cronologico: {new_url}")
            self.driver.get(new_url)

            return new_url

        except Exception as e:
            logger.error(f"Erro ao calcular ou aplicar o filtro de data na URL: {e}")
            raise RuntimeError(f"Falha ao injetar parametros de data na busca: {e}") from e

 
    def extract_results(self) -> list:
        """
        Varre os elementos de resultado na tela e extrai os metadados dos artigos.

        Processa os dados coletados de titulos e descricoes para realizar contagem
        de palavras-chave, validacao financeira e download estruturado de midias associadas.

        Returns:
            list: Uma lista de dicionarios contendo as informacoes de cada artigo mapeado.

        Raises:
            RuntimeError: Se houver falha critica ao carregar a lista de cards ou ao processar o DOM.
        """
        logger.info("Iniciando processo de carregamento e extracao...")

        logger.info("Carregando mais resultados (clicando em 'Show More')...")
        sleep(6)
        while True:
            botao_clicado = self.safe_click(By.XPATH, "//button[contains(text(), 'Show More')]", retries=1, delay=0)
            
            if not botao_clicado:
                logger.info("Todos os resultados foram carregados (botao 'Show More' nao esta mais disponivel).")
                break
                
            logger.debug("Botao 'Show More' clicado. Aguardando novos resultados...")
            sleep(2)

        try:
            cards = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@data-testid='search-bodega-result']")
                )
            )

            logger.info(f"Encontrados {len(cards)} resultados no total.")

            results = []

            for index, card in enumerate(cards, start=1):
                logger.info(f"Extraindo card {index}/{len(cards)}...")
                article_id = f"art_{index:04d}"
                image_id   = f"art_{index:04d}"
                final_path = "" 

                try:
                    try:
                        category = card.find_element(By.XPATH, ".//div[@data-tpl='la']").text.strip()
                        logger.debug(f"Categoria encontrada: {category}")
                    except:
                        category = ""
                        logger.debug("Categoria nao encontrada para este card.")

                    try:
                        title_element = card.find_element(By.XPATH, ".//div[@data-tpl='h']/a")
                        title = title_element.text.strip()
                        link = title_element.get_attribute("href")
                        logger.debug(f"Titulo: {title} | Link: {link}")
                    except:
                        title = ""
                        link = ""
                        logger.warning(f"Titulo/Link nao encontrados no card {index}")

                    try:
                        description = card.find_element(By.XPATH, ".//div[@data-tpl='bo']").text.strip()
                        logger.debug(f"Descricao: {description}")
                    except:
                        description = ""
                        logger.debug("Descricao nao encontrada para este card.")

                    search_phrases = self.config.get("search_phrase").split(",")

                    phrase_count = count_search_phrases(
                        f"{title} {description}",
                        search_phrases
                    )

                    has_money = contains_money(title) or contains_money(description)
                    logger.debug(f"Contagem de frases: {phrase_count} | Contem valor monetario: {has_money}")

                    try:
                        date = card.find_element(By.XPATH, ".//span").text.strip()
                        logger.debug(f"Data encontrada: {date}")
                    except:
                        date = ""
                        logger.debug("Data nao encontrada para este card.")

                    try:
                        img = card.find_element(By.XPATH, ".//img")
                        img_alt = img.get_attribute("alt")
                        img_src = img.get_attribute("src")

                        logger.debug(f"Imagem localizada. SRC: {img_src}")

                        # 1 Baixar a imagem com o nome padrao (hash)
                        downloaded_path = download_image(img_src, self.images_dir)

                        if downloaded_path:
                            # 2 Criar caminho final com o ID
                            final_path = os.path.join(self.images_dir, f"{image_id}.jpg")

                            # 3 Renomear
                            os.rename(downloaded_path, final_path)
                            image_filename = f"{image_id}.jpg"
                        else:
                            image_filename = ""

                    except:
                        img_alt = ""
                        img_src = ""
                        image_filename = ""
                        logger.debug("Imagem nao encontrada no bloco HTML do card.")

                    results.append(
                        {
                            "id": article_id,
                            "title": title,
                            "description": description,
                            "date": date,
                            "image_filename": final_path,
                            "phrase_count": phrase_count,
                            "contains_money": has_money,
                        }
                    )

                    logger.info(f"Card {index} extraido com sucesso!")

                except Exception as e:
                    logger.error(f"Erro ao ler o card {index}: {e}")

            logger.info("Extracao concluida!")
            return results

        except Exception as e:
            logger.error(f"Erro critico ao extrair resultados do DOM: {e}")
            raise RuntimeError(f"Falha severa ao varrer ou carregar elementos da pesquisa: {e}") from e