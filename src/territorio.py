"""Referências territoriais do Brasil."""
from typing import NamedTuple


class Uf(NamedTuple):
    """Dados de uma unidade da federação."""

    sigla: str
    nome: str
    regiao: str


# Listar as regiões na ordem de exibição
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

# Mapear código da UF para seus dados
UF = {
    "11": Uf("RO", "Rondônia", "Norte"),
    "12": Uf("AC", "Acre", "Norte"),
    "13": Uf("AM", "Amazonas", "Norte"),
    "14": Uf("RR", "Roraima", "Norte"),
    "15": Uf("PA", "Pará", "Norte"),
    "16": Uf("AP", "Amapá", "Norte"),
    "17": Uf("TO", "Tocantins", "Norte"),
    "21": Uf("MA", "Maranhão", "Nordeste"),
    "22": Uf("PI", "Piauí", "Nordeste"),
    "23": Uf("CE", "Ceará", "Nordeste"),
    "24": Uf("RN", "Rio Grande do Norte", "Nordeste"),
    "25": Uf("PB", "Paraíba", "Nordeste"),
    "26": Uf("PE", "Pernambuco", "Nordeste"),
    "27": Uf("AL", "Alagoas", "Nordeste"),
    "28": Uf("SE", "Sergipe", "Nordeste"),
    "29": Uf("BA", "Bahia", "Nordeste"),
    "31": Uf("MG", "Minas Gerais", "Sudeste"),
    "32": Uf("ES", "Espírito Santo", "Sudeste"),
    "33": Uf("RJ", "Rio de Janeiro", "Sudeste"),
    "35": Uf("SP", "São Paulo", "Sudeste"),
    "41": Uf("PR", "Paraná", "Sul"),
    "42": Uf("SC", "Santa Catarina", "Sul"),
    "43": Uf("RS", "Rio Grande do Sul", "Sul"),
    "50": Uf("MS", "Mato Grosso do Sul", "Centro-Oeste"),
    "51": Uf("MT", "Mato Grosso", "Centro-Oeste"),
    "52": Uf("GO", "Goiás", "Centro-Oeste"),
    "53": Uf("DF", "Distrito Federal", "Centro-Oeste"),
}


def adicionar_territorio(df):
    """Adicionar UF, sigla e região a partir do código do município."""
    # Copiar para preservar o original
    out = df.copy()

    # Extrair código da UF (2 primeiros dígitos)
    out["uf_cod"] = out["cod"].str[:2]

    # Recusar códigos de UF desconhecidos
    desconhecidos = set(out["uf_cod"]) - set(UF)
    if desconhecidos:
        raise ValueError(f"Códigos de UF desconhecidos: {sorted(desconhecidos)}")

    # Mapear sigla, nome e região
    out["uf_sigla"] = out["uf_cod"].map(lambda c: UF[c].sigla)
    out["uf_nome"] = out["uf_cod"].map(lambda c: UF[c].nome)
    out["regiao"] = out["uf_cod"].map(lambda c: UF[c].regiao)
    return out