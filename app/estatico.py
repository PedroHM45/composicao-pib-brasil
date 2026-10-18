"""Exportar as malhas como arquivos estáticos servidos pelo Streamlit."""
from pathlib import Path

import orjson

import dados
from dados import ANO_REF, NIVEIS, PROCESSED, carregar_malha

PASTA = Path(__file__).parent / "static"


def garantir_malha(nivel):
    """Gravar a malha do nível (se faltar ou estiver velha) e devolver a URL."""
    cfg = NIVEIS[nivel]
    nome = f"malha_{cfg['malha']}.geojson"
    arquivo = PASTA / nome

    # Listar as fontes que, se mudarem, invalidam o arquivo
    origem = Path(PROCESSED) / f"malha_{cfg['malha']}_{ANO_REF}.geojson"
    fontes = [Path(dados.__file__), origem]

    # Regravar quando o arquivo faltar ou for mais antigo que as fontes
    velho = arquivo.exists() and any(
        f.stat().st_mtime > arquivo.stat().st_mtime for f in fontes if f.exists()
    )
    if velho or not arquivo.exists():
        PASTA.mkdir(exist_ok=True)
        arquivo.write_bytes(
            orjson.dumps(carregar_malha(nivel), option=orjson.OPT_SERIALIZE_NUMPY)
        )

    # Devolver o caminho público (relativo à raiz do app)
    return f"app/static/{nome}"
