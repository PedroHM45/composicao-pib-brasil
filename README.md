# Composição do PIB brasileiro - 2021

**Como a riqueza se distribui entre os 5.570 municípios brasileiros, e de que setores ela vem?**

Dashboard interativo em Streamlit, construído com os dados do IBGE sobre o PIB dos municípios em 2021.

## A tese

> O Brasil é um país de economia desigual. A riqueza se concentra em poucos centros urbanos de serviços, enquanto um terço dos municípios depende da administração pública, a indústria está em poucos lugares e o agro ocupa boa parte do interior.

O fio condutor é a diferença entre **valor** e **território**. Pelo valor produzido (o PIB), o Brasil é urbano e de serviços. Pelo território (os municípios), é agrícola e dependente do setor público.

## Em números (2021)

| Achado | Número |
|---|---|
| Concentração | 87 municípios (1,6%) produzem metade do PIB, e 12 produzem um quarto |
| Desigualdade | Gini de 0,838 no PIB, contra 0,735 na população e 0,446 no PIB per capita |
| Serviços | 50,7% da economia do país (66,5% somando a administração pública) |
| Dependência | 34% dos municípios têm a administração pública como maior setor |
| Indústria | 25,8% da economia, mas é o maior setor em só 9,3% dos municípios |
| Agropecuária | 7,7% da economia, mas é o maior setor em 26,7% dos municípios |

*Economia = valor adicionado bruto (VAB) do IBGE, o que cada setor produz, sem os impostos. As definições completas estão na página Metodologia do painel.*

## O que o painel mostra

São cinco páginas, uma para cada passo da história. Todas seguem o mesmo desenho: controles na barra lateral, um painel de leitura à esquerda, o gráfico no centro e um ranking à direita.

| Página | Pergunta | O que mostra |
|---|---|---|
| **Explorar** | Onde está a riqueza e como ela se compõe? | Mapa dos 5.570 municípios, 27 estados ou 5 regiões, colorido pelo setor dominante. Ao clicar ou buscar um território, aparecem a composição do PIB, o PIB total e o PIB per capita |
| **Concentração** | Quão concentrada é a riqueza? | Curva de Lorenz, mapa de bolhas e comparação entre regiões. Ranking dos maiores PIBs, de municípios ou estados |
| **Dependência** | Quem depende da administração pública? | Mapa em faixas, comparação entre regiões e portes de município, e relação entre dependência e renda. Ranking dos territórios mais dependentes |
| **Estrutura produtiva** | Como se distribuem serviços, indústria e agro? | Contraste entre o valor (soma do país) e a mediana dos municípios, mapa do peso de cada setor e especialização dos estados. Ranking por setor |
| **Metodologia** | Como os números foram construídos e quais são os limites? | Fontes, definições, métodos e limites da análise |

## Como rodar

O projeto foi desenvolvido com Python 3.14. Os dados já tratados estão em `data/processed/`, então o painel roda sem refazer a coleta.

**1. Criar o ambiente e instalar as dependências** (PowerShell, na raiz do projeto)

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
~~~

No macOS ou Linux, a ativação é `source .venv/bin/activate`.

**2. Abrir o painel**

~~~powershell
streamlit run app\main.py
~~~

**3. Rodar os testes** (opcional)

~~~powershell
pip install -r requirements-dev.txt
pytest
~~~

**4. Regenerar os dados** (opcional)

~~~powershell
python -m src.pipeline
~~~

O pipeline coleta, trata e valida os dados e gera os arquivos de `data/processed/`. Ele confere antes se os arquivos originais do IBGE (malhas e recortes) estão em `data/raw/`. As planilhas de recortes ficam no repositório (são pequenas). As malhas não, por serem grandes. A lista completa está em `docs/fontes.md`.

## Estrutura do projeto

~~~
radar-pib-br/
├── app/            painel em Streamlit (main.py e as páginas em app/paginas/)
├── src/            coleta, tratamento, indicadores e pipeline
├── data/
│   ├── raw/        arquivos originais do IBGE (só os recortes são versionados)
│   └── processed/  bases prontas para o painel
├── notebooks/      análise exploratória (02_eda.ipynb, sem saídas: execute para gerar os gráficos)
├── tests/          testes automatizados (pytest)
└── docs/           fontes e documentação
~~~

## Fontes e limites

Os dados vêm do IBGE:

- **PIB dos Municípios, 2021:** [SIDRA, tabela 5938](https://sidra.ibge.gov.br/tabela/5938)
- **Estimativas da População, 2021:** [SIDRA, tabela 6579](https://sidra.ibge.gov.br/tabela/6579)
- **Malhas Territoriais, 2021:** limites de municípios, estados e regiões
- Recortes territoriais: ver `docs/fontes.md`

O que a análise **não** diz:

- É um retrato de **um único ano** (2021), sem evolução no tempo.
- O PIB municipal é uma **estimativa** do IBGE, e o PIB per capita não é renda da população.
- "Administração pública" inclui educação e saúde públicas: mede o **peso da atividade pública** na economia local, não a dependência fiscal.
- As relações mostradas são **associações, não causas**.

Os detalhes estão na página **Metodologia** do painel.

## Feito com

Python, pandas, GeoPandas, scikit-learn, Plotly e Streamlit.