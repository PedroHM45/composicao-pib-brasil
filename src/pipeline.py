"""Pipeline reprodutível: do SIDRA aos arquivos finais."""
import logging

import geopandas as gpd
import pandas as pd
from sklearn.metrics import adjusted_rand_score

from src.agrupamento import agrupar, nomear_grupos
from src.coleta import NIVEL_MUNICIPIO, NIVEL_UF, baixar_pib, baixar_populacao
from src.config import (
    ARQ_MALHA_MUNICIPIOS,
    ARQ_MALHA_UF,
    ARQ_MATOPIBA,
    ARQ_METROPOLES,
    ARQ_SEMIARIDO,
    K_PERFIS,
    LIMITE_ESTABILIDADE,
    N_MUNICIPIOS,
    ORIGINAIS,
    PROCESSED,
    RAIZ,
    SETORES,
    TOLERANCIA_CONTABIL,
    arquivo_final,
)
from src.malha import (
    preparar_malha_municipal,
    preparar_malha_regional,
    preparar_malha_uf,
)
from src.recortes import montar_recortes
from src.tratamento import agregar, integrar

# Definir o nome do registrador (fixo, pois o módulo roda como "__main__")
logger = logging.getLogger("src.pipeline")


def conferir_originais():
    """Conferir se os arquivos originais existem, com o nome exato."""
    ausentes = []
    for arq in ORIGINAIS:
        # Comparar com a listagem da pasta (distingue maiúsculas também no Windows)
        existentes = {p.name for p in arq.parent.iterdir()} if arq.parent.exists() else set()
        if arq.name not in existentes:
            ausentes.append(str(arq.relative_to(RAIZ)))

    if ausentes:
        raise FileNotFoundError(f"Arquivos originais ausentes: {ausentes}")


def validar(mun, uf_sidra):
    """Validar consistência dos dados integrados."""
    # Conferir quantidade de municípios
    if len(mun) != N_MUNICIPIOS:
        raise ValueError(f"Municípios: {len(mun)} (esperado {N_MUNICIPIOS})")

    # Separar colunas de participação (vazias onde há VAB negativo)
    cols_part = [c for c in mun.columns if c.startswith("part_")]

    # Conferir ausentes fora das participações
    if mun.drop(columns=cols_part).isna().any().any():
        raise ValueError("Há valores ausentes na base integrada")

    # Conferir ausentes nas participações (aceitos só com VAB negativo)
    if mun.loc[~mun["vab_negativo"], cols_part].isna().any().any():
        raise ValueError("Participações ausentes sem VAB negativo")

    # Avisar sobre municípios com VAB setorial negativo
    negativos = mun.loc[mun["vab_negativo"], "nome"].tolist()
    if negativos:
        logger.warning("  aviso: VAB setorial negativo em %s", negativos)

    # Calcular diferenças contábeis
    soma_uf = mun.groupby("uf_cod")["pib"].sum()
    testes = {
        "setores x VAB": (mun[SETORES].sum(axis=1) - mun["vab_total"]).abs().max(),
        "VAB + impostos x PIB": (
            mun["vab_total"] + mun["impostos"] - mun["pib"]
        ).abs().max(),
        "municípios x estados": (
            soma_uf - uf_sidra.set_index("cod")["pib"]
        ).abs().max(),
    }

    # Rejeitar diferenças acima da tolerância
    for nome, dif in testes.items():
        if dif > TOLERANCIA_CONTABIL:
            raise ValueError(f"Teste '{nome}' falhou: diferença {dif}")
        logger.info("  ok: %s (diferença máxima %.0f)", nome, dif)


def etapa_dados():
    """Coletar, integrar, agregar, validar e salvar os dados."""
    logger.info("1/4 Dados")

    # Coletar PIB e população
    pib_mun = baixar_pib(NIVEL_MUNICIPIO)
    pib_uf = baixar_pib(NIVEL_UF)
    pop_mun = baixar_populacao(NIVEL_MUNICIPIO)

    # Integrar e validar
    mun = integrar(pib_mun, pop_mun)
    validar(mun, pib_uf)

    # Agregar por estado e região
    uf = agregar(mun, ["uf_cod", "uf_sigla", "uf_nome"])
    reg = agregar(mun, "regiao")

    # Salvar bases finais
    mun.to_csv(arquivo_final("pib_municipios", "csv"), index=False)
    uf.to_csv(arquivo_final("pib_uf", "csv"), index=False)
    reg.to_csv(arquivo_final("pib_regioes", "csv"), index=False)

    return mun


def etapa_malhas(mun):
    """Preparar e salvar as malhas territoriais."""
    logger.info("2/4 Malhas")

    # Ler malhas originais
    bruta_mun = gpd.read_file(ARQ_MALHA_MUNICIPIOS)
    bruta_uf = gpd.read_file(ARQ_MALHA_UF)

    # Preparar malhas
    malhas = {
        "municipios": preparar_malha_municipal(bruta_mun),
        "uf": preparar_malha_uf(bruta_uf),
        "regioes": preparar_malha_regional(bruta_uf),
    }

    # Validar códigos da malha municipal contra a base
    if set(malhas["municipios"]["cod"]) != set(mun["cod"]):
        raise ValueError("Códigos da malha municipal diferem da base")
    logger.info("  ok: códigos da malha iguais aos da base")

    # Salvar malhas
    for nome, gdf in malhas.items():
        gdf.to_file(arquivo_final(f"malha_{nome}", "geojson"), driver="GeoJSON")


def etapa_recortes(mun):
    """Montar e salvar a tabela de recortes."""
    logger.info("3/4 Recortes")

    # Ler listas dos recortes
    semi = pd.read_excel(ARQ_SEMIARIDO, dtype=str)
    mato = pd.read_excel(ARQ_MATOPIBA, dtype=str)
    rm = pd.read_excel(ARQ_METROPOLES, sheet_name=0, dtype=str)

    # Montar e salvar tabela de recortes
    rec = montar_recortes(mun, semi, mato, rm)
    rec.to_csv(arquivo_final("recortes", "csv"), index=False)

    # Exibir contagens
    contagem = rec[["matopiba", "semiarido", "em_metropole"]].sum().to_dict()
    logger.info("  ok: %s", contagem)


def etapa_perfis(mun):
    """Agrupar municípios por perfil econômico e salvar."""
    logger.info("4/4 Perfis")

    # Agrupar e devolver rótulos para todos os municípios
    rotulos = agrupar(mun, k=K_PERFIS).reindex(mun.index).astype("Int64")

    # Nomear os grupos pelo perfil
    nomes = nomear_grupos(mun.assign(grupo=rotulos))
    perfis = pd.DataFrame(
        {"cod": mun["cod"], "grupo": rotulos, "perfil": rotulos.map(nomes)}
    )

    # Testar estabilidade com outra semente
    outro = agrupar(mun, k=K_PERFIS, semente=7)
    ari = adjusted_rand_score(rotulos.loc[outro.index].astype(int), outro)
    if ari < LIMITE_ESTABILIDADE:
        logger.warning("  aviso: agrupamento instável (ARI %.3f)", ari)
    else:
        logger.info("  ok: estabilidade com outra semente (ARI %.3f)", ari)

    # Salvar perfis e exibir contagens
    perfis.to_csv(arquivo_final("perfis", "csv"), index=False)
    logger.info("  ok: %s", perfis["perfil"].value_counts().to_dict())


def rodar():
    """Executar o pipeline completo."""
    # Exibir só a mensagem (avisos de terceiros continuam visíveis)
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    # Mostrar as mensagens de informação apenas dos módulos do projeto
    logging.getLogger("src").setLevel(logging.INFO)

    # Conferir os originais antes de consultar o SIDRA
    conferir_originais()

    # Criar a pasta de saída, se preciso
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # Executar as etapas
    mun = etapa_dados()
    etapa_malhas(mun)
    etapa_recortes(mun)
    etapa_perfis(mun)
    logger.info("Pipeline concluído")


if __name__ == "__main__":
    rodar()