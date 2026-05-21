"""
Módulo de Utilidades de Texto para Extração de Dados.

Este módulo fornece funções auxiliares baseadas em expressões regulares
para contar termos de busca e identificar a presença de menções a valores
monetários em blocos de texto.
"""

import re
from src.utils.logger import logger


def count_search_phrases(text: str, phrases: list[str]) -> int:
    """
    Conta quantas vezes qualquer frase de busca aparece no texto.

    A busca é realizada de forma insensível a maiúsculas e minúsculas
    (case-insensitive) e utiliza escape de caracteres especiais para
    garantir a precisão da busca literal.

    Args:
        text (str): O texto completo onde a busca será realizada.
        phrases (list[str]): Lista de frases ou palavras-chave a serem contadas.

    Returns:
        int: O somatório total de ocorrências de todas as frases no texto.
    """
    if not text:
        logger.debug("Texto vazio ou nulo fornecido para contagem de frases.")
        return 0

    text_lower = text.lower()
    count = 0

    logger.debug(f"Iniciando contagem de {len(phrases)} frases de busca no texto.")

    for phrase in phrases:
        phrase_lower = phrase.lower()
        matches = len(re.findall(re.escape(phrase_lower), text_lower))
        count += matches
        if matches > 0:
            logger.debug(f"Frase '{phrase}' encontrada {matches} vez(es).")

    logger.info(f"Contagem de frases concluida. Total de ocorrencias: {count}")
    return count


def contains_money(text: str) -> bool:
    """
    Verifica se um texto contém valores monetários.

    A varredura suporta múltiplos formatos e símbolos internacionais e locais,
    incluindo $, €, £, R$, além de termos extensos como dólares, euros,
    pounds e reais.

    Args:
        text (str): O texto a ser analisado.

    Returns:
        bool: True se qualquer padrão monetário for identificado, False caso contrário.
    """
    if not text:
        logger.debug("Texto vazio ou nulo fornecido para verificacao monetaria.")
        return False

    patterns = [
        r"\$\s?\d+(?:[\.,]\d+)?", # $10 / $ 10 / $10.50
        r"€\s?\d+(?:[\.,]\d+)?", # €10
        r"£\s?\d+(?:[\.,]\d+)?", # £10
        r"R\$\s?\d+(?:[\.,]\d+)?", # R$ 10
        r"\d+(?:[\.,]\d+)?\s?(dollars?|bucks)", # 10 dollars
        r"\d+(?:[\.,]\d+)?\s?(euros?)", # 10 euros
        r"\d+(?:[\.,]\d+)?\s?(pounds?)", # 10 pounds
        r"\d+(?:[\.,]\d+)?\s?(reais?)", # 10 reais
    ]

    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            logger.info("Padrao de valor monetario identificado no texto.")
            return True

    logger.debug("Nenhum valor monetario foi encontrado no texto analisado.")
    return False