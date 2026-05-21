"""
Modulo de gerenciamento de configuracoes do sistema de automacao.

Este script e responsavel por localizar, validar e carregar parametros operacionais
estruturados a partir de arquivos de configuracao no formato YAML.
"""

import os
import yaml
from utils.logger import logger

CONFIG_PATH = os.path.join("config", "config.yaml")

def load_config(path: str = CONFIG_PATH) -> dict:
    """
    Carrega e faz o parse do arquivo de configuracao YAML do projeto.

    Verifica a existencia do arquivo no caminho especificado e realiza a leitura
    segura dos parametros operacionais da automacao.

    Args:
        path (str): Caminho relativo ou absoluto para o arquivo de configuracao.
            Por padrao, utiliza a constante CONFIG_PATH.

    Returns:
        dict: Dicionario contendo as chaves e valores mapeados do arquivo YAML.

    Raises:
        FileNotFoundError: Se o arquivo de configuracao nao for localizado no caminho informado.
        RuntimeError: Se o arquivo YAML contiver erros de sintaxe ou falhas de leitura.
    """
    logger.info(f"Tentando carregar o arquivo de configuracao: {path}")

    if not os.path.exists(path):
        logger.error(f"Arquivo de configuracao nao encontrado no caminho especificado: {path}")
        raise FileNotFoundError(f"Arquivo de configuracao nao encontrado: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        
        logger.info("Arquivo de configuracao carregado e parseado com sucesso.")
        return config

    except yaml.YAMLError as e:
        logger.error(f"Erro de sintaxe ou mapeamento ao ler o arquivo YAML {path}: {e}")
        raise RuntimeError(f"Falha ao interpretar o arquivo de configuracao YAML: {e}") from e
    except Exception as e:
        logger.error(f"Erro inesperado ao abrir o arquivo de configuracao {path}: {e}")
        raise RuntimeError(f"Falha critica na leitura do arquivo de configuracao: {e}") from e