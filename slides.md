---
title: "Implementação de um SAT Solver"
author: "Lucas Bazante, José Eduardo"
date: "9 de Dezembro, 2025"
output: 
  beamer_presentation:
    latex_engine: xelatex
header-includes: |
  \usepackage{amsmath}
  \usepackage{graphicx}
  \usepackage{booktabs}
bibliography: refs.bib
---

# Slide 1: Introdução
## Boolean Satisfiability Problem (SAT)
- O problema da satisfiabilidade Booliana refere-se a possibilidade de encontrar atribuições de valores para variáveis de forma que a fórmula Booliana a que elas pertencem tornem-se verdadeiras.

- SAT foi o primeiro problema a ser mostrado NP-Completo [@cook] , e possui ampla relevância acadêmica e industrial, com SAT solvers sendo utilizados em diversas áreas tais quais: Inteligência Artificial, Bioinformática, Verificação de Software e etc.

- Neste trabalho focamos na implementação de um Max-SAT solver e a comparação de seus resultados com outras duas implementações (DPLL e WalkSAT).


# Slide 2: Max-SAT
## Maximum Satisfiability (Max-SAT)
- Enquanto o SAT é um problema de decisão, o Max-SAT é um problema de combinatória.

- O Max-SAT consiste em encontrar uma atribuição que satisfaça o maior número possível de cláusulas.


# Slide 3: Iterated Local Search (ILS)
- A Iterated Local Search [@lourenco2001iteratedlocalsearch] é uma metaheurística de busca local.
- A busca local tradicional pode chegar a um máximo local e não progredir mais.
- ILS utiliza-se de dois passos para resolver isso: um para encontrar ótimos locais de forma eficiente (**Intensificação**) e outro para escapar de estados locais (**Perturbação**).


# Slide 3.1: Iterated Local Search (ILS)
## Pseudocódigo
```
function ILS()
  s0 = GerarSolucaoInicial()
  s = BuscaLocal(s0)
  while(!condicao_de_parada) do
    s' = pertubacao(s)
    s'' = BuscaLocal(s')

    s = criterio_de_aceitacao(s, s'')
  end

  retorne s
end
```

# Slide 4: Estado da Arte
## Solvers Incompletos (Busca Local)
- **NuWLS-c** [@chu2024nuwls]: Baseado em **Busca Local Estocástica (SLS)**, combina a heurística de **Configuration Checking (CC)** com esquemas de **Dynamic Clause Weighting** para alternar entre intensificação e diversificação.

## Solvers Completos (Exatos)
- **RC2** [@ignatiev2019rc2]: Implementa uma abordagem **Core-Guided** que utiliza *Soft Cardinality Constraints* e **Estratificação de Pesos** para o relaxamento iterativo.
- **CASHWMaxSAT** [@li2025cashw]: Integra técnicas de **Component Caching** com heurísticas de poda via **Branch-and-Bound**, otimizando a gestão de memória e a redução do espaço de busca.

# Slide 5: Implementações
- DPLL + VSIDLS (Algoritmo Exato)
- WalkSAT (Algoritmo Aproximativo)
- ILS (Metaheurística)


# Slide 6: Metodologia
Para testar a eficácia e corretude dos algoritmos, foram utilizados conjuntos de testes disponibilizados pela biblioteca **SATLIB** [@hoos2000satlib].

\begin{columns}
  \begin{column}{0.5\textwidth}
    \begin{itemize}
      \item uuf50-218
      \item uuf75-325
      \item uuf200-860
    \end{itemize}
  \end{column}
  
  \begin{column}{0.5\textwidth}
    \begin{itemize}
      \item uf50-218
      \item flat30-60
    \end{itemize}
  \end{column}
\end{columns}

# Slide 6 : ILS em problemas UNSOLVABLE
\begin{table}
\centering
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccccc}
\toprule
Test Suite & Num. Instancias & Tempo Total (m) & Tempo Médio (s) & Mediana do Tempo (s) & Média de clausulas satisfeitas \\
\midrule
uuf50-218 & 1000 & 162.46 & 9.74 & 9.72 & 216.9 \\
uuf75-325 & 100 & 22.31 & 13.74 & 13.78 & 310.4 \\
uuf200-860 & 99 & 55.18 & 33.44 & 33.49 & 858.4 \\
\bottomrule
\end{tabular}
}
\caption{Resultados do ILS}
\end{table}

# Slide 7 : DPLL vs WalkSAT vs ILS
\begin{table}
\centering
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccccc}
\toprule
Algoritmo & Tempo Total (m) & Tempo Médio (s) & Mediana do Tempo (s) & Média de clausulas satisfeitas \\
\midrule
ILS & 162.46 &  9.74  & 9.72 & 216.92 \\
WalkSAT & 224.48 & 13.46 & 13.43 & 211.73 \\
DPLL & 7.6 & 0.46 & 0.43 & 0 \\
\bottomrule
\end{tabular}
}
\caption{Resultados de cada algoritmo no conjunto de testes uuf50-218}
\end{table}

# Slide 8: Conclusão

- Limitação de Métodos Exatos: O DPLL confirma rapidamente a insatisfatibilidade, mas não otimiza a solução parcial, tornando-o inviável para Max-SAT puro.

- Eficácia do ILS: O mecanismo de *perturbação* permitiu escapar de ótimos locais onde o WalkSAT estagnou, resultando em mais cláusulas satisfeitas em menos tempo.

# Referências

::: {#refs}
:::
