"""Constantes visuais compartilhadas entre notebooks e dashboard."""
from src.config import (
    PERFIL_AGRO,
    PERFIL_INDUSTRIAL,
    PERFIL_PUBLICO,
    PERFIL_URBANO,
    QUADRANTE_CONC_ALTA,
    QUADRANTE_CONC_BAIXA,
    QUADRANTE_DIV_ALTA,
    QUADRANTE_DIV_BAIXA,
    SETORES,
)
from src.territorio import REGIOES

# Mapear cada setor para o seu rótulo
ROTULO_SETOR = {
    "vab_agro": "Agropecuária",
    "vab_industria": "Indústria",
    "vab_servicos": "Serviços",
    "vab_adm_publica": "Adm. pública",
}

# Listar os rótulos na ordem dos setores
NOMES_SETORES = [ROTULO_SETOR[s] for s in SETORES]

# Definir cores fixas dos setores
CORES_SETORES = {
    ROTULO_SETOR["vab_agro"]: "#2E8B57",
    ROTULO_SETOR["vab_industria"]: "#4682B4",
    ROTULO_SETOR["vab_servicos"]: "#F4A261",
    ROTULO_SETOR["vab_adm_publica"]: "#8E44AD",
}

# Definir ordem das regiões
ORDEM_REGIOES = REGIOES

# Definir ordem e cores fixas dos quadrantes
ORDEM_QUADRANTES = [
    QUADRANTE_CONC_BAIXA,
    QUADRANTE_CONC_ALTA,
    QUADRANTE_DIV_BAIXA,
    QUADRANTE_DIV_ALTA,
]
CORES_QUADRANTES = {
    QUADRANTE_CONC_BAIXA: "#C0392B",
    QUADRANTE_CONC_ALTA: "#E67E22",
    QUADRANTE_DIV_BAIXA: "#7F8C8D",
    QUADRANTE_DIV_ALTA: "#2980B9",
}

# Definir cores fixas dos perfis (as mesmas dos setores dominantes)
CORES_PERFIS = {
    PERFIL_PUBLICO: "#8E44AD",
    PERFIL_AGRO: "#2E8B57",
    PERFIL_INDUSTRIAL: "#4682B4",
    PERFIL_URBANO: "#F4A261",
}