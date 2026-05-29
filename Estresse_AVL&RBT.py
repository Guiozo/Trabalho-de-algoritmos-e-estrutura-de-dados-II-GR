import sys
sys.path.insert(0, '/mnt/agents/upload')

import time
import random
import math
from avl import PacketRule, ArvoreAVL
from rb import PacketRule as PacketRuleRB, ArvoreRB, Cor

ArvoreRedBlack = ArvoreRB


def medir_tempo_ns(func, *args, **kwargs):
    inicio = time.perf_counter_ns()
    resultado = func(*args, **kwargs)
    fim = time.perf_counter_ns()
    return resultado, (fim - inicio)


def gerar_regras(n, seed=42):
    rng = random.Random(seed)
    regras = []
    for i in range(n):
        prio = rng.randint(1, n * 10)
        regras.append(PacketRule(i, f"10.0.0.{i}", f"192.168.1.{i}", prio))
    return regras


def gerar_regras_rb(n, seed=42):
    rng = random.Random(seed)
    regras = []
    for i in range(n):
        prio = rng.randint(1, n * 10)
        regras.append(PacketRuleRB(i, f"10.0.0.{i}", f"192.168.1.{i}", prio))
    return regras


def teste_estresse_completo():
    tamanhos = [10_000, 100_000, 1_000_000]
    resultados = []

    print("=" * 80)
    print("  TESTE DE ESTRESSE - AVL vs RED-BLACK TREE")
    print("  SDN-Scale | Estrutura de Dados II")
    print("=" * 80)

    for n in tamanhos:
        print(f"\n{'='*80}")
        print(f"  CENÁRIO: N = {n:,} regras")
        print(f"{'='*80}")

        regras_avl = gerar_regras(n, seed=42)
        regras_rb = gerar_regras_rb(n, seed=42)

        rng_rem = random.Random(123)
        indices_remover = rng_rem.sample(range(n), int(n * 0.20))
        regras_remover_avl = [regras_avl[i] for i in indices_remover]
        regras_remover_rb = [regras_rb[i] for i in indices_remover]

        print("\n  --- ÁRVORE AVL ---")
        avl = ArvoreAVL()

        tempo_insercao_avl = 0
        for r in regras_avl:
            _, t = medir_tempo_ns(avl.insert, r)
            tempo_insercao_avl += t

        altura_avl = avl.get_altura()
        rotacoes_avl = avl.get_rotacoes()
        tamanho_avl = avl.tamanho()

        rng_busca = random.Random(999)
        indices_busca = [rng_busca.randint(0, n-1) for _ in range(1000)]
        tempo_busca_avl = 0
        for i in indices_busca:
            _, t = medir_tempo_ns(avl.buscar, regras_avl[i])
            tempo_busca_avl += t

        tempo_remocao_avl = 0
        for r in regras_remover_avl:
            _, t = medir_tempo_ns(avl.remover, r)
            tempo_remocao_avl += t

        tamanho_final_avl = avl.tamanho()
        altura_final_avl = avl.get_altura()

        print("  --- ÁRVORE RED-BLACK ---")
        rb = ArvoreRedBlack()
        rb.reset_contadores()

        tempo_insercao_rb = 0
        for r in regras_rb:
            _, t = medir_tempo_ns(rb.insert, r)
            tempo_insercao_rb += t

        altura_rb = rb.get_altura()
        rotacoes_rb = rb.get_rotacoes()
        recolorings_rb = rb.get_recolorir()
        tamanho_rb = rb.tamanho()

        tempo_busca_rb = 0
        for i in indices_busca:
            _, t = medir_tempo_ns(rb.buscar, regras_rb[i])
            tempo_busca_rb += t

        rb.reset_contadores()
        tempo_remocao_rb = 0
        for r in regras_remover_rb:
            _, t = medir_tempo_ns(rb.remover, r)
            tempo_remocao_rb += t

        rotacoes_rem_rb = rb.get_rotacoes()
        recolorings_rem_rb = rb.get_recolorir()
        tamanho_final_rb = rb.tamanho()
        altura_final_rb = rb.get_altura()

        res = {
            'n': n,
            'avl': {
                'tempo_insercao_ns': tempo_insercao_avl,
                'tempo_busca_ns': tempo_busca_avl,
                'tempo_remocao_ns': tempo_remocao_avl,
                'altura_inicial': altura_avl,
                'altura_final': altura_final_avl,
                'rotacoes': rotacoes_avl,
                'tamanho_inicial': tamanho_avl,
                'tamanho_final': tamanho_final_avl,
            },
            'rb': {
                'tempo_insercao_ns': tempo_insercao_rb,
                'tempo_busca_ns': tempo_busca_rb,
                'tempo_remocao_ns': tempo_remocao_rb,
                'altura_inicial': altura_rb,
                'altura_final': altura_final_rb,
                'rotacoes': rotacoes_rb,
                'recolorings': recolorings_rb,
                'rotacoes_remocao': rotacoes_rem_rb,
                'recolorings_remocao': recolorings_rem_rb,
                'tamanho_inicial': tamanho_rb,
                'tamanho_final': tamanho_final_rb,
            }
        }
        resultados.append(res)

        print(f"\n  RESULTADOS PARA N = {n:,}:")
        print(f"  {'-'*60}")
        print(f"  {'Métrica':<30} {'AVL':>15} {'Red-Black':>15}")
        print(f"  {'-'*60}")
        print(f"  {'Tempo Inserção (ms)':<30} {tempo_insercao_avl/1e6:>15.2f} {tempo_insercao_rb/1e6:>15.2f}")
        print(f"  {'Tempo Busca 1k ops (ms)':<30} {tempo_busca_avl/1e6:>15.2f} {tempo_busca_rb/1e6:>15.2f}")
        print(f"  {'Tempo Remoção 20% (ms)':<30} {tempo_remocao_avl/1e6:>15.2f} {tempo_remocao_rb/1e6:>15.2f}")
        print(f"  {'Altura Inicial':<30} {altura_avl:>15} {altura_rb:>15}")
        print(f"  {'Altura Final (após remoção)':<30} {altura_final_avl:>15} {altura_final_rb:>15}")
        print(f"  {'Rotações (inserção)':<30} {rotacoes_avl:>15} {rotacoes_rb:>15}")
        print(f"  {'Recolorings (inserção)':<30} {'N/A':>15} {recolorings_rb:>15}")
        print(f"  {'Rotações (remoção)':<30} {'N/A':>15} {rotacoes_rem_rb:>15}")
        print(f"  {'Recolorings (remoção)':<30} {'N/A':>15} {recolorings_rem_rb:>15}")
        print(f"  {'Tamanho Final':<30} {tamanho_final_avl:>15} {tamanho_final_rb:>15}")
        print(f"  {'Limite Teórico Altura':<30} {round(1.44*math.log2(n+2),1):>15} {round(2*math.log2(n+1),1):>15}")
        print(f"  {'-'*60}")

    return resultados


if __name__ == "__main__":
    resultados = teste_estresse_completo()
    print("\n\nTeste concluído!")