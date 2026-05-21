"""
Módulo de Configuração de Registro (Logging).

Este módulo fornece funções para inicializar e configurar o comportamento
do Loguru, definindo saídas tanto para arquivos de log específicos da execução
quanto para o console, garantindo rastreabilidade no processo de scraping.
"""

from loguru import logger
import os
import sys

def setup_logger(run_folder: str, run_id: str, level="DEBUG"):
    """
    Configura o logger global da aplicação.

    Remove os manipuladores (handlers) padrão do Loguru e adiciona dois novos:
    1. Um arquivo de log persistente na pasta de execução, com rotação diária
       e retenção de 7 dias.
    2. Uma saída de console limpa que exibe as mensagens em tempo real.

    Args:
        run_folder (str): Caminho do diretório onde o arquivo de log será salvo.
        run_id (str): Identificador único da execução atual para nomeação do arquivo.

    Returns:
        loguru.Logger: A instância do logger global configurada.
    """
    log_file = os.path.join(
        run_folder,
        f"scraper_{run_id}.log"
    )

    logger.remove()

    logger.add(
        log_file,
        rotation="1 day",
        retention="7 days",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

    logger.add(
        sys.stdout,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

    return logger