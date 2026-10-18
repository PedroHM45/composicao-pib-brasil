"""Página 5: metodologia, definições e limites do painel."""
import streamlit as st

import dados  # noqa: F401  (ajusta o caminho de src)
from componentes import br, cabecalho
from dados import ANO_REF, carregar_base
from src.indicadores import gini

# Exibir o título e a pergunta da página
cabecalho("Metodologia", "Como os números foram construídos e quais são os limites?")

aba_fontes, aba_def, aba_met, aba_lim = st.tabs(
    ["Fontes", "Definições", "Métodos", "Limites"]
)

# Aba 1: listar as fontes
with aba_fontes:
    st.markdown(f"""
| Dado | Fonte | Referência |
|---|---|---|
| PIB e valor adicionado por setor | IBGE, PIB dos Municípios | [SIDRA, tabela 5938](https://sidra.ibge.gov.br/tabela/5938) · {ANO_REF} |
| População | IBGE, Estimativas da População | [SIDRA, tabela 6579](https://sidra.ibge.gov.br/tabela/6579) · {ANO_REF} |
| Mapas (limites territoriais) | IBGE, Malhas Territoriais | {ANO_REF} |

Todos os valores em reais correntes de {ANO_REF}.
""")

# Aba 2: definir os termos
with aba_def:
    st.markdown("""
**Economia.** Neste painel, é o *valor adicionado bruto* (VAB): o que cada setor
produz, sem os impostos. Todas as participações por setor usam o VAB.

**PIB.** É o VAB mais os impostos sobre produtos. O **PIB per capita** é o PIB
dividido pela população estimada.

**Setores (classificação do IBGE)**
- **Agropecuária:** agricultura, pecuária, produção florestal, pesca e aquicultura.
- **Indústria:** extrativa (mineração e petróleo), transformação, construção e
  utilidades (eletricidade, água e esgoto).
- **Serviços:** comércio, transporte, finanças e demais serviços, **sem** a
  administração pública.
- **Administração pública:** administração, defesa, educação e saúde públicas e
  seguridade social.

**Setor dominante.** O setor de maior peso na economia de um município.

**Mediana dos municípios.** Alinhe os municípios em uma fila, do que tem menos
agropecuária ao que tem mais. O município do meio da fila dá a mediana: em metade
dos municípios o setor pesa menos que ela e, na outra metade, pesa mais. A fila é
refeita para cada setor, com municípios diferentes. Por isso a mediana não descreve
uma cidade real, e as medianas dos quatro setores não somam 100%. Diferente da
média, ela não é puxada pelos poucos municípios gigantes.
""")

# Aba 3: explicar os métodos
with aba_met:
    base = carregar_base("Município")

    # Calcular o Gini de PIB, população e PIB per capita
    g_pib = gini(base["pib"].dropna().to_numpy())
    g_pop = gini(base["populacao"].dropna().to_numpy())
    g_pc = gini(base["pib_per_capita"].dropna().to_numpy())

    st.markdown("""
**Curva de Lorenz e índice de Gini.** Ordenamos os municípios do menor ao maior e
medimos quanto da riqueza fica com cada fatia. O Gini vai de 0 (igualdade) a 1
(tudo em um só município).
""")
    c1, c2, c3 = st.columns(3)
    c1.metric("Gini do PIB", br(g_pib, 3))
    c2.metric("Gini da população", br(g_pop, 3))
    c3.metric("Gini do PIB per capita", br(g_pc, 3))

    st.markdown("""
**Quociente locacional (QL).** É o peso do setor no estado dividido pelo peso do
mesmo setor no país. Acima de 1, o estado é mais especializado no setor do que a
média nacional.

**Perfis de municípios.** Agrupamento (K-means, 4 grupos) sobre a composição
setorial, transformada por log-razão centrada (CLR), técnica própria para
proporções que somam 100%.

**Soma × mediana.** O "Brasil" soma todos os municípios, então as grandes cidades
pesam muito: mostra onde está o dinheiro. A mediana dá o mesmo peso a cada
município, grande ou pequeno: mostra onde estão os municípios.

**Correlação de Spearman.** Mede se dois indicadores andam juntos em ordem, sem
ser distorcida por valores extremos. Indica associação, nunca causa.
""")

# Aba 4: listar os limites
with aba_lim:
    st.markdown(f"""
1. **Um único ano.** O painel é um retrato de {ANO_REF}. Não mostra evolução.
2. **Dados ausentes.** Cachoeira Dourada (GO) não tem composição setorial, pelo
   valor adicionado negativo. Boa Esperança do Norte (MT) não tem PIB em {ANO_REF}.
3. **PIB municipal é estimativa.** O IBGE distribui o valor adicionado entre os
   municípios com base em indicadores. A população é estimada, não do Censo. Em municípios pequenos, uma única grande empresa pode concentrar o valor adicionado e gerar números extremos, como PIB per capita muito alto ou um setor acima de 80%. O piso de 10 mil habitantes nos rankings reduz, mas não elimina, esses casos.
4. **Indústria inclui mineração e petróleo.** Municípios com poços, minas ou
   usinas têm PIB per capita alto sem que isso signifique renda da população local.
5. **Administração pública não é dependência fiscal.** A categoria do IBGE inclui
   educação e saúde públicas. O painel mede o peso da atividade pública na economia
   local, não quanto o município recebe de transferências.
6. **Associação não é causa.** Relações como a da dependência com a renda indicam
   que os fenômenos andam juntos, não que um provoque o outro.
7. **Rankings de municípios** consideram apenas os de 10 mil habitantes ou mais,
   para evitar que cidades minúsculas dominem as listas.
""")
