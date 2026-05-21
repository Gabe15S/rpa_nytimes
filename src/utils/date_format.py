"""
Modulo de utilitarios cronologicos para processamento de metadados.

Este script fornece funcoes de tratamento, normalizacao e conversao de strings
de data extraidas de portais de noticias internacionais para formatos padronizados.
"""

from datetime import datetime
from src.utils.logger import logger

def convert_nyt_date(date_str: str) -> str:
    """
    Converte datas no formato 'MAY 19' para '19/05/2026'.

    Realiza o parse de strings textuais curtas baseadas no padrao norte-americano
    e injeta o ano corrente de forma automatica para gerar o padrao brasileiro (DD/MM/AAAA).
    Caso nao consiga interpretar, retorna uma string vazia.

    Args:
        date_str (str): Texto bruto da data capturado no portal (ex: "MAY 19").

    Returns:
        str: Data formatada em padrao 'dd/mm/aaaa' ou string vazia em caso de falha.

    Raises:
        ValueError: Caso ocorra uma falha estrutural critica que impeca a validacao basica.
    """
    logger.debug(f"Processando conversao da string de data: '{date_str}'")

    if not date_str or len(date_str.split()) != 2:
        logger.warning(f"String de data invalida ou fora do padrao esperado: '{date_str}'")
        return ""

    try:
        month_str, day_str = date_str.split()

        month_map = {
            "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
            "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
            "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
        }

        month_str = month_str.strip().upper()

        if month_str not in month_map:
            logger.warning(f"Mes textual nao mapeado ou desconhecido: '{month_str}'")
            return ""

        month = month_map[month_str]
        day = int(day_str)

        year = datetime.now().year

        date_obj = datetime(year, month, day)
        formatted_date = date_obj.strftime("%d/%m/%Y")
        
        logger.debug(f"Data convertida com sucesso: '{date_str}' -> '{formatted_date}'")
        return formatted_date

    except Exception as e:
        logger.error(f"Erro inesperado ao converter a string de data '{date_str}': {e}")
        return ""