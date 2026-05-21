"""
Módulo de Download e Armazenamento de Mídias.

Este módulo fornece funcionalidades para realizar o download de imagens de forma
síncrona a partir de URLs públicas, salvando-as localmente com nomes gerados via
hashing (MD5) para evitar duplicidade ou conflitos no sistema de arquivos.
"""

import os
import hashlib
import requests
from src.utils.logger import logger


def download_image(img_url: str, images_dir: str) -> str:
    """
    Realiza o download de uma imagem a partir de uma URL e a salva localmente.

    O nome do arquivo gerado corresponde ao hash MD5 da própria URL para garantir
    unicidade. Caso ocorra qualquer falha durante a requisição ou escrita em disco,
    o erro é registrado no log e uma string vazia é retornada.

    Args:
        img_url (str): A URL pública da imagem que será baixada.
        images_dir (str): O diretório local onde a imagem baixada deve ser salva.

    Returns:
        str: O caminho completo do arquivo salvo localmente ou uma string vazia
            em caso de falha.
    """
    if not img_url:
        logger.warning("URL de imagem vazia ou invalida fornecida para download.")
        return ""

    try:
        os.makedirs(images_dir, exist_ok=True)

        response = requests.get(img_url, timeout=10)
        response.raise_for_status()

        filename = hashlib.md5(img_url.encode()).hexdigest() + ".jpg"

        full_path = os.path.join(images_dir, filename)

        with open(full_path, "wb") as f:
            f.write(response.content)

        logger.info(f"Imagem baixada com sucesso e salva em: {full_path}")
        return full_path  # 👈 AQUI é o ponto principal

    except Exception as e:
        logger.error(f"Erro ao baixar imagem: {e}")
        return ""