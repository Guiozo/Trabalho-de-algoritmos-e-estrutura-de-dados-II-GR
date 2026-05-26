# Trabalho-de-algoritmos-e-estrutura-de-dados-II-GR
Análise comparativa de estruturas de dados auto-balanceáveis (AVL vs. Red-Black Tree) focada em trade-offs de performance, roteamento de dados e eficiência de memória.


RELATÓRIO TÉCNICO: COMPARAÇÃO DE ESTRUTURAS DE DADOS (AVL VS. RED-BLACK)

1. INTRODUÇÃO
Este relatório detalha as características, trade-offs e rotas de dados das árvores binárias auto-balanceáveis AVL e Red-Black (RBT).

2. FILOSOFIA DE BALANCEAMENTO
- Árvore AVL: Balanceamento estrito. A diferença de altura entre subárvores (fator de balanço) é no máximo 1.
- Árvore Red-Black: Balanceamento laxo. Utiliza regras de cores (Vermelho/Preto) para garantir que o caminho mais longo não seja mais do que o dobro do caminho mais curto.

3. ANÁLISE DE TRADE-OFFS
   
-----------------------------------------------------------------------
Característica   | Árvore AVL              | Árvore Red-Black
-----------------------------------------------------------------------
Equilíbrio           | Rígido                  | Flexível

Velocidade de Busca  | Mais Rápida (Otimizada) | Rápida (Sub-otimizada)

Custo de Inserção    | Alto (Mais rotações)    | Baixo (Foco em cores)

Uso de Memória       | Armazena Altura (int)   | Armazena Cor (1 bit)

-----------------------------------------------------------------------

4. ROTA DE DADOS (DATA ROUTE)
Em ambas as estruturas, a rota segue a lógica de busca binária:
- Se valor < nó atual: Direção Esquerda.
- Se valor > nó atual: Direção Direita.

Diferença de Percurso:
- Na AVL, o caminho da raiz até a folha é minimizado ao máximo (H ~ 1.44 log n).
- Na Red-Black, o percurso pode ser mais longo (H <= 2 log n), mas a estrutura é atualizada mais rapidamente.

5. CONCLUSÃO E APLICAÇÕES
- Use AVL para sistemas de leitura intensiva (Dicionários, Lookups estáticos).
- Use Red-Black para sistemas de escrita frequente (Mapas de memória, Schedulers de SO, std::map em C++)
