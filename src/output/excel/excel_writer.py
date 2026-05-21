"""
Módulo de Persistência de Dados em Excel.

Este módulo concentra as rotinas necessárias para salvar e complementar
arquivos do Excel com as informações estruturadas obtidas a partir
dos processos de scraping do New York Times.
"""

import os
from datetime import datetime
import pandas as pd
from src.utils.logger import logger


def save_articles_to_excel(articles: list, output_dir: str, filename: str = None):
    """
    Salva a lista de artigos extraídos em um arquivo Excel dentro da pasta fornecida.

    Caso o arquivo já exista no diretório especificado, o método realiza a leitura dos
    dados antigos, equaliza as colunas necessárias e anexa os novos registros no fim
    do arquivo (append). Se o arquivo não existir, um novo é gerado com a ordenação
    padrão das colunas.

    Args:
        articles (list): Lista de dicionários contendo os dados estruturados dos artigos.
        output_dir (str): Caminho do diretório onde o arquivo Excel deve ser guardado.
        filename (str, optional): Nome específico do arquivo. Se omitido, um nome padrão
            com timestamp será gerado automaticamente.

    Returns:
        str: O caminho completo (full path) do arquivo Excel gerado ou modificado.
    """
    os.makedirs(output_dir, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nyt_articles_{timestamp}.xlsx"

    full_path = os.path.join(output_dir, filename)

    for art in articles:
        if not art.get("date"):
            art["date"] = None

    new_df = pd.DataFrame(articles)

    column_order = [
        "id",
        "title",
        "description",
        "date",
        "image_filename",
        "phrase_count",
        "contains_money"
    ]

    if not os.path.exists(full_path):
        for col in column_order:
            if col not in new_df.columns:
                new_df[col] = None

        new_df = new_df[column_order]
        new_df.to_excel(full_path, index=False)

        logger.info(f"Arquivo Excel criado: {full_path}")
        return full_path

    existing_df = pd.read_excel(full_path)

    for col in new_df.columns:
        if col not in existing_df.columns:
            existing_df[col] = None

    for col in existing_df.columns:
        if col not in new_df.columns:
            new_df[col] = None

    final_df = pd.concat([existing_df, new_df], ignore_index=True)
    final_df = final_df[[c for c in column_order if c in final_df.columns]]

    final_df.to_excel(full_path, index=False)

    logger.info(f"Dados adicionados ao Excel: {full_path}")
    return full_path