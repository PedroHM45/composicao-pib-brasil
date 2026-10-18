"""Funções de preparo da malha territorial."""
from src.territorio import UF

# Definir códigos das áreas especiais (lagoas)
AREAS_ESPECIAIS = ["4300001", "4300002"]

# Definir CRS de destino (padrão web)
CRS_WEB = "EPSG:4326"

# Definir tolerância de simplificação (graus; 0,005 = cerca de 500 m)
TOLERANCIA = 0.005


def _padronizar(gdf, tolerancia):
    """Reprojetar, simplificar e validar geometrias."""
    # Converter para o CRS de destino
    gdf = gdf.to_crs(CRS_WEB)

    # Simplificar geometrias
    gdf["geometry"] = gdf.geometry.simplify(tolerancia, preserve_topology=True)

    # Recusar geometrias vazias ou inválidas
    if gdf.geometry.is_empty.any() or not gdf.geometry.is_valid.all():
        raise ValueError("A simplificação gerou geometrias vazias ou inválidas")

    return gdf.reset_index(drop=True)


def _atributo(codigos, campo):
    """Mapear código da UF para um campo do dicionário UF."""
    return codigos.map(lambda c: getattr(UF[c], campo))


def preparar_malha_municipal(malha, tolerancia=TOLERANCIA):
    """Limpar, reprojetar e simplificar a malha municipal."""
    # Remover áreas especiais
    gdf = malha[~malha["CD_MUN"].isin(AREAS_ESPECIAIS)].copy()

    # Renomear colunas
    gdf = gdf.rename(
        columns={
            "CD_MUN": "cod",
            "NM_MUN": "nome",
            "SIGLA": "uf_sigla",
            "AREA_KM2": "area_km2",
        }
    )

    return _padronizar(gdf, tolerancia)


def preparar_malha_uf(malha, tolerancia=TOLERANCIA):
    """Padronizar atributos, reprojetar e simplificar a malha de estados."""
    # Manter só código e geometria
    gdf = malha[["CD_UF", "geometry"]].rename(columns={"CD_UF": "uf_cod"}).copy()

    # Padronizar sigla, nome e região pelo dicionário
    gdf["uf_sigla"] = _atributo(gdf["uf_cod"], "sigla")
    gdf["uf_nome"] = _atributo(gdf["uf_cod"], "nome")
    gdf["regiao"] = _atributo(gdf["uf_cod"], "regiao")

    return _padronizar(gdf, tolerancia)


def preparar_malha_regional(malha, tolerancia=TOLERANCIA):
    """Unir estados por região e simplificar."""
    # Derivar região a partir do código do estado
    gdf = malha[["CD_UF", "geometry"]].copy()
    gdf["regiao"] = _atributo(gdf["CD_UF"], "regiao")

    # Unir os estados de cada região
    gdf = gdf[["regiao", "geometry"]].dissolve(by="regiao", as_index=False)

    return _padronizar(gdf, tolerancia)