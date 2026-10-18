# Fontes e dados

O ano de referência é **2021**, o último com composição setorial do PIB dos municípios.

## 1. De onde vêm os dados

| Dado | Fonte | Onde |
|---|---|---|
| PIB e valor adicionado por setor | IBGE, PIB dos Municípios | [SIDRA, tabela 5938](https://sidra.ibge.gov.br/tabela/5938) |
| População | IBGE, Estimativas da População | [SIDRA, tabela 6579](https://sidra.ibge.gov.br/tabela/6579) |
| Malhas (limites de municípios e estados) | IBGE, Malhas Territoriais | [Página das malhas](https://ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/15774-malhas.html) |
| Semiárido | Delimitação da Sudene (Resolução CONDEL/Sudene nº 150, de 13/12/2021), divulgada pelo IBGE | [Semiárido brasileiro](https://www.ibge.gov.br/geociencias/cartas-e-mapas/redes-geograficas/15974-semiarido-brasileiro.html) |
| MATOPIBA | Portaria nº 244/2015 do Ministério da Agricultura, divulgada pelo IBGE | [MATOPIBA](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/34329-matopiba.html) |
| Regiões metropolitanas, RIDEs e aglomerações urbanas | IBGE, edição 2021 | [Recortes metropolitanos](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/divisao-regional/18354-recortes-metropolitanos-e-aglomeracoes-urbanas.html) |

A página dos recortes metropolitanos destaca hoje a edição mais recente. A edição 2021 consta na lista de edições da mesma página.

## 2. Arquivos originais (`data/raw/`)

A pasta `data/raw/` não é versionada, exceto `data/raw/recortes/` (planilhas pequenas, guardadas para o pipeline ser reproduzível). Para regenerar os dados, baixe cada arquivo que faltar, coloque-o no caminho abaixo **com o nome exato** (maiúsculas e minúsculas contam) e rode `python -m src.pipeline`. O pipeline confere a presença dos arquivos antes de começar.

| Arquivo | O que é | Tamanho |
|---|---|---|
| `data/raw/malha/BR_Municipios_2021.zip` | Malha municipal 2021 | 194 MB |
| `data/raw/malha/BR_UF_2021.zip` | Malha das unidades da federação 2021 | 13 MB |
| `data/raw/recortes/lista_municipios_Semiarido_2021.xls` | Municípios do Semiárido | 0,15 MB |
| `data/raw/recortes/MATOPIBA_2021.xls` | Municípios do MATOPIBA | 0,08 MB |
| `data/raw/recortes/Composicao_RMs_RIDEs_AglomUrbanas_2021_v2.xls` | Composição de RMs, RIDEs e aglomerações urbanas | 0,44 MB |

Os dados de PIB e população não ficam em arquivo: o pipeline os consulta direto no SIDRA.

## 3. Arquivos processados (`data/processed/`)

Estes arquivos alimentam o painel. Estão no repositório, então o painel roda sem refazer a coleta.

| Arquivo | Conteúdo |
|---|---|
| `pib_municipios_2021.csv` | PIB, valor adicionado por setor e população dos municípios |
| `pib_uf_2021.csv` | Os mesmos indicadores, agregados por estado |
| `pib_regioes_2021.csv` | Os mesmos indicadores, agregados por região |
| `perfis_2021.csv` | Perfil econômico de cada município e indicadores de concentração setorial |
| `recortes_2021.csv` | Marcação dos municípios em MATOPIBA, Semiárido e metrópoles |
| `malha_municipios_2021.geojson` | Limites dos municípios |
| `malha_uf_2021.geojson` | Limites dos estados |
| `malha_regioes_2021.geojson` | Limites das regiões |

## 4. Etapas do pipeline

O comando `python -m src.pipeline` executa as etapas em sequência.

| Etapa | O que faz |
|---|---|
| **Conferência** | Verifica se os arquivos originais estão em `data/raw/` antes de consultar o SIDRA |
| **Dados** | Consulta o SIDRA, trata os valores e valida o resultado: 5.570 municípios e consistência contábil, com tolerância de R$ 50 mil por causa do arredondamento do IBGE. Gera os arquivos de PIB por município, estado e região |
| **Malhas** | Lê os arquivos `.zip` e gera os três arquivos GeoJSON |
| **Recortes** | Lê as planilhas e marca os municípios do Semiárido, do MATOPIBA e das metrópoles. Metrópole é um recorte metropolitano cuja população somada passa de 1 milhão de habitantes |
| **Perfis** | Agrupa os municípios em 4 perfis econômicos (Agropecuário, Dependente do setor público, Industrial diversificado e Urbano de serviços) e classifica cada um em quadrantes de concentração setorial × renda |