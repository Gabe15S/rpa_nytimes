"""

Módulo de gerenciamento e inicialização do WebDriver do Selenium.
Este módulo encapsula as configurações de diferentes navegadores (Chrome, Firefox,
Edge) permitindo execuções flexíveis, parametrização do modo headless (segundo plano)
e aplicação de argumentos de segurança necessários para ambientes de container (Docker).
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from src.utils.logger import logger


def _is_running_in_docker() -> bool:
    """Verifica se o código está rodando dentro de um container Docker."""
    return os.path.exists('/.dockerenv')


def create_driver(
    browser: str = "chrome",
    headless: bool = False,
):
    """
    Inicializa o driver do Selenium com boas práticas, mais robusto e configurável.
    Args:
        browser (str): Nome do navegador a ser iniciado (chrome, firefox, edge).
        headless (bool): Se Verdadeiro, inicia o navegador em modo oculto.
    Returns:
        webdriver: Instância configurada do WebDriver correspondente.
    Raises:
        ValueError: Se o nome do navegador informado não for suportado.

    """

    if _is_running_in_docker() and not headless:
        mensagem_erro = (
            "ERRO DE AMBIENTE: O robô está rodando dentro de um container Docker, "
            "mas a execução em segundo plano (headless) está desativada. "
            "Containers Linux não possuem interface gráfica. Por favor, altere "
            "o arquivo de configuração para rodar com headless = True."
        )
        logger.critical(mensagem_erro)
        sys.exit(mensagem_erro)
    logger.info(f"Iniciando configuracao do WebDriver para o navegador: {browser}")

    browser = browser.lower()

    if browser == "chrome":
        logger.debug("Configurando opcoes para o Google Chrome")

        options = ChromeOptions()

        if headless:
            logger.debug("Aplicando argumentos para modo Headless no Chrome")
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-software-rasterizer")
        else:
            logger.debug("Aplicando argumentos para modo de interface grafica no Chrome")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")

        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        logger.info("Instanciando o WebDriver do Google Chrome")

        driver = webdriver.Chrome(
            service=ChromeService(),
            options=options
        )

    elif browser == "firefox":
        logger.debug("Configurando opcoes para o Mozilla Firefox")
        options = FirefoxOptions()

        if headless:
            logger.debug("Aplicando argumentos para modo Headless no Firefox")
            options.add_argument("-headless")

        logger.info("Instanciando o WebDriver do Mozilla Firefox")

        driver = webdriver.Firefox(
            service=FirefoxService(),
            options=options
        )

    elif browser == "edge":
        logger.debug("Configurando opcoes para o Microsoft Edge")
        options = EdgeOptions()

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
        else:
            logger.debug("Aplicando argumentos para modo de interface grafica no Edge")
            options.add_argument("--start-maximized")

        logger.info("Instanciando o WebDriver do Microsoft Edge")

        driver = webdriver.Edge(
            service=EdgeService(),
            options=options
        )
    else:
        logger.error(f"Tentativa de inicializacao falhou: Navegador '{browser}' nao e suportado.")
        raise ValueError("Navegador invalido. Use: chrome, firefox, edge")


    logger.debug("Aplicando limites de timeout padrao do sistema")
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(20)
    driver.implicitly_wait(10)
    logger.success(f"WebDriver para {browser} inicializado e pronto para uso")

    return driver