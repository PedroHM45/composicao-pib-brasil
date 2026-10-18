"""Funções de montagem dos recortes econômicos."""

# Definir limite de população das metrópoles
LIMITE_METROPOLE = 1_000_000


def _validar_lista(codigos, base, nome, unicos=True):
    """Conferir se os códigos existem na base e, se pedido, não se repetem."""
    if unicos and codigos.duplicated().any():
        raise ValueError(f"Lista '{nome}' com municípios repetidos")

    # Listar códigos ausentes da base
    fora = set(codigos) - set(base)
    if fora:
        raise ValueError(f"Lista '{nome}' com {len(fora)} códigos fora da base")


def metropoles(rm, mun, limite=LIMITE_METROPOLE):
    """Selecionar municípios de recortes metropolitanos acima do limite."""
    # Remover repetições dentro do mesmo recorte
    pares = rm[["COD_RECMETROPOL", "NOME_RECMETROPOL", "COD_MUN"]].drop_duplicates()

    # Juntar a população de cada município
    pares = pares.merge(
        mun[["cod", "populacao"]],
        left_on="COD_MUN",
        right_on="cod",
        validate="many_to_one",
    )

    # Somar população por recorte
    total = pares.groupby("COD_RECMETROPOL")["populacao"].transform("sum")

    # Manter recortes acima do limite
    grandes = pares[total > limite].copy()

    # Simplificar o nome do recorte
    grandes["NOME_RECMETROPOL"] = grandes["NOME_RECMETROPOL"].str.replace(
        r"^Recorte Metropolitano (?:de|da|do|dos|das) ", "", regex=True
    )

    # Reunir os nomes dos recortes de cada município
    return (
        grandes.groupby("cod")["NOME_RECMETROPOL"]
        .agg(lambda s: "; ".join(sorted(s)))
        .rename("metropole")
        .reset_index()
    )


def montar_recortes(mun, semi, mato, rm):
    """Montar tabela de recortes por município."""
    # Validar as listas contra a base de municípios
    _validar_lista(mato["CD_MUN"], mun["cod"], "MATOPIBA")
    _validar_lista(semi["CD_MUN"], mun["cod"], "Semiárido")
    _validar_lista(rm["COD_MUN"], mun["cod"], "Metropolitanos", unicos=False)

    # Criar base com todos os municípios
    out = mun[["cod"]].copy()

    # Marcar MATOPIBA e semiárido
    out["matopiba"] = out["cod"].isin(mato["CD_MUN"])
    out["semiarido"] = out["cod"].isin(semi["CD_MUN"])

    # Nomear a metrópole de cada município
    out = out.merge(metropoles(rm, mun), on="cod", how="left", validate="one_to_one")

    # Marcar municípios em metrópoles
    out["em_metropole"] = out["metropole"].notna()

    # Marcar municípios fora de qualquer recorte
    out["fora"] = ~(out["matopiba"] | out["semiarido"] | out["em_metropole"])

    return out
