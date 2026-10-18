"""Constantes compartilhadas por todos os módulos."""
from pathlib import Path

# Definir pastas do projeto
RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
PROCESSED = RAIZ / "data" / "processed"

# Definir ano de referência (último com composição setorial)
ANO_REF = "2021"

# Definir arquivos originais do IBGE (nomes exatos, com maiúsculas)
ARQ_MALHA_MUNICIPIOS = RAW / "malha" / "BR_Municipios_2021.zip"
ARQ_MALHA_UF = RAW / "malha" / "BR_UF_2021.zip"
ARQ_SEMIARIDO = RAW / "recortes" / "lista_municipios_Semiarido_2021.xls"
ARQ_MATOPIBA = RAW / "recortes" / "MATOPIBA_2021.xls"
ARQ_METROPOLES = RAW / "recortes" / "Composicao_RMs_RIDEs_AglomUrbanas_2021_v2.xls"
ORIGINAIS = [
    ARQ_MALHA_MUNICIPIOS,
    ARQ_MALHA_UF,
    ARQ_SEMIARIDO,
    ARQ_MATOPIBA,
    ARQ_METROPOLES,
]

# Definir parâmetros de validação do pipeline
N_MUNICIPIOS = 5570
TOLERANCIA_CONTABIL = 50  # mil reais (arredondamento do IBGE)
LIMITE_ESTABILIDADE = 0.9

# Listar colunas dos setores
SETORES = ["vab_agro", "vab_industria", "vab_servicos", "vab_adm_publica"]

# Listar colunas somáveis na agregação
SOMAVEIS = ["pib", "vab_total", "impostos", "populacao"] + SETORES

# Definir rótulos dos quadrantes (concentração setorial x renda)
QUADRANTE_CONC_BAIXA = "Concentrado, baixa renda"
QUADRANTE_CONC_ALTA = "Concentrado, alta renda"
QUADRANTE_DIV_BAIXA = "Diversificado, baixa renda"
QUADRANTE_DIV_ALTA = "Diversificado, alta renda"

# Definir o número de perfis econômicos e seus nomes
K_PERFIS = 4
PERFIL_AGRO = "Agropecuário"
PERFIL_PUBLICO = "Dependente do setor público"
PERFIL_INDUSTRIAL = "Industrial diversificado"
PERFIL_URBANO = "Urbano de serviços"


def arquivo_final(nome, extensao, ano=ANO_REF):
    """Devolver o caminho de um arquivo final em data/processed."""
    return PROCESSED / f"{nome}_{ano}.{extensao}"