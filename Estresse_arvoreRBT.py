import sys
sys.path.insert(0, '/mnt/agents/upload')

from rb import ArvoreRB, PacketRule, Cor
import time
import random
import math
import matplotlib.pyplot as plt
import numpy as np
import gc
from datetime import datetime
from matplotlib.ticker import MaxNLocator

# Configurar para mostrar gráficos com acentos
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12

def contar_nos(arv):
    """Conta o número de nós na árvore RB"""
    def _contar(node):
        if node is None or node == getattr(arv, 'TNULL', None):
            return 0
        return 1 + _contar(node.esquerda) + _contar(node.direita)
    return _contar(arv.raiz)

def altura_arvore(arv):
    """Calcula a altura da árvore RB"""
    def _altura(node):
        if node is None or node == getattr(arv, 'TNULL', None):
            return 0
        return 1 + max(_altura(node.esquerda), _altura(node.direita))
    return _altura(arv.raiz)

def tem_metodo(obj, nome):
    return hasattr(obj, nome) and callable(getattr(obj, nome))

def get_tamanho(arv):
    if tem_metodo(arv, 'tamanho'):
        return arv.tamanho()
    return contar_nos(arv)

def get_altura(arv):
    if tem_metodo(arv, 'get_altura'):
        return arv.get_altura()
    return altura_arvore(arv)

def get_rotacoes(arv):
    if tem_metodo(arv, 'get_rotacoes'):
        return arv.get_rotacoes()
    return 0

def get_recolorir(arv):
    if tem_metodo(arv, 'get_recolorir'):
        return arv.get_recolorir()
    return 0

def reset_contadores(arv):
    if tem_metodo(arv, 'reset_contadores'):
        arv.reset_contadores()


# ========================================
# GERADOR DE REGRAS OTIMIZADO
# ========================================

def gerar_regras_otimizado(qtd, amostragem=False, amostra_tamanho=None):
    """Gera regras de forma otimizada, com opção de amostragem"""
    if amostragem and amostra_tamanho and amostra_tamanho < qtd:
        qtd = amostra_tamanho
        print(f"  (Usando amostra de {qtd:,} regras para acelerar)")
    
    regras = []
    prioridades = list(range(1, qtd + 1))
    random.shuffle(prioridades)

    for i, prio in enumerate(prioridades):
        regra = PacketRule(
            i,
            f"10.0.0.{i}",
            f"192.168.1.{i}",
            prio
        )
        regras.append(regra)

    return regras

def gerar_regras_insercao_direta(qtd):
    """Gera regras e insere diretamente (economiza memória)"""
    prioridades = list(range(1, qtd + 1))
    for i in range(qtd - 1, 0, -1):
        j = random.randint(0, i)
        prioridades[i], prioridades[j] = prioridades[j], prioridades[i]
    
    for i, prio in enumerate(prioridades):
        yield PacketRule(i, f"10.0.0.{i}", f"192.168.1.{i}", prio)


# ========================================
# SIMULACAO DE EXPIRACAO OTIMIZADA PARA RB
# ========================================

def simular_expiracao_detalhada_otimizada_rb(arv, regras, nome_teste="Expiracao", usar_amostragem=False):
    """Simulação otimizada para árvore RB com coleta de métricas (remove EXATAMENTE 20%)"""
    qtd_atual = get_tamanho(arv)
    qtd_remover = int(qtd_atual * 0.2)
    
    if qtd_remover > len(regras):
        qtd_remover = len(regras)
    
    expiradas = random.sample(regras, qtd_remover)
    
    # Coletar métricas detalhadas
    metricas = {
        'tempos_individuais': [],
        'alturas_parciais': [],
        'rotacoes_parciais': [],
        'recolorings_parciais': [],
        'nos_restantes': []
    }
    
    reset_contadores(arv)
    
    inicio_total = time.perf_counter_ns()
    rotacoes_inicio = get_rotacoes(arv)
    recolorir_inicio = get_recolorir(arv)
    
    # Coletar métricas a cada N remoções
    step = max(1, qtd_remover // 500)
    
    print(f"  Iniciando remocao de {qtd_remover:,} nos (20%)...")
    print(f"  Coletando metricas a cada {step} remocoes para o grafico...")
    
    for i, regra in enumerate(expiradas):
        inicio_remocao = time.perf_counter_ns()
        arv.remover(regra)
        fim_remocao = time.perf_counter_ns()
        
        if i % step == 0 or i == qtd_remover - 1:
            metricas['tempos_individuais'].append(fim_remocao - inicio_remocao)
            metricas['alturas_parciais'].append(get_altura(arv))
            metricas['rotacoes_parciais'].append(get_rotacoes(arv) - rotacoes_inicio)
            metricas['recolorings_parciais'].append(get_recolorir(arv) - recolorir_inicio)
            metricas['nos_restantes'].append(get_tamanho(arv))
        
        if (i + 1) % max(1, qtd_remover // 10) == 0:
            percentual = ((i + 1) / qtd_remover) * 100
            print(f"  Progresso: {percentual:.0f}% ({i+1:,} removidos de {qtd_remover:,})")
    
    fim_total = time.perf_counter_ns()
    
    tempo_total_ns = fim_total - inicio_total
    rotacoes_totais = get_rotacoes(arv) - rotacoes_inicio
    recolorings_totais = get_recolorir(arv) - recolorir_inicio
    
    # Estatísticas
    stats = {
        'tempo_total_ns': tempo_total_ns,
        'tempo_medio_ns': tempo_total_ns / qtd_remover,
        'tempo_mediana_ns': np.median(metricas['tempos_individuais']),
        'tempo_std_ns': np.std(metricas['tempos_individuais']),
        'tempo_min_ns': min(metricas['tempos_individuais']),
        'tempo_max_ns': max(metricas['tempos_individuais']),
        'rotacoes_totais': rotacoes_totais,
        'rotacoes_por_remocao': rotacoes_totais / qtd_remover,
        'recolorings_totais': recolorings_totais,
        'recolorings_por_remocao': recolorings_totais / qtd_remover,
        'altura_inicial': metricas['alturas_parciais'][0] if metricas['alturas_parciais'] else get_altura(arv),
        'altura_final': get_altura(arv),
        'nos_iniciais': qtd_atual,
        'nos_removidos': qtd_remover,
        'nos_finais': get_tamanho(arv)
    }
    
    # Exibir resultados
    print()
    print("========================================")
    print(f" {nome_teste} - RESULTADOS (RB Tree)")
    print("========================================")
    print(f"Nos totais antes: {qtd_atual:,}")
    print(f"Nos removidos (20% reais): {qtd_remover:,}")
    print(f"Nos restantes: {get_tamanho(arv):,}")
    print()
    print("--- TEMPOS ---")
    print(f"Tempo total: {tempo_total_ns:,} ns = {tempo_total_ns / 1_000_000:.3f} ms = {tempo_total_ns / 1_000_000_000:.3f} s")
    print(f"Tempo medio por remocao: {tempo_total_ns / qtd_remover:,.2f} ns")
    print(f"Mediana dos tempos: {stats['tempo_mediana_ns']:,.2f} ns")
    print(f"Desvio padrao: {stats['tempo_std_ns']:,.2f} ns")
    print(f"Tempo minimo: {stats['tempo_min_ns']:,} ns")
    print(f"Tempo maximo: {stats['tempo_max_ns']:,} ns")
    print()
    print("--- ROTACOES E RECOLORINGS ---")
    print(f"Rotacoes totais durante remocoes: {rotacoes_totais:,}")
    print(f"Media de rotacoes por remocao: {rotacoes_totais / qtd_remover:.2f}")
    print(f"Recolorings totais: {recolorings_totais:,}")
    print(f"Media de recolorings por remocao: {recolorings_totais / qtd_remover:.2f}")
    
    return stats, metricas


def simular_expiracao_multiplos_volumes_otimizado_rb(volumes, usar_amostragem=True):
    """Simula expiração em diferentes volumes de dados para RB Tree"""
    resultados = []
    
    print()
    print("========================================")
    print("  SIMULACAO EM MULTIPLOS VOLUMES (RB)")
    print("========================================")
    
    for qtd in volumes:
        print(f"\n--- Testando com {qtd:,} nos ---")
        
        if qtd >= 500000:
            print(f"  ATENCAO: Este teste pode levar varios minutos...")
        
        arv = ArvoreRB()
        regras = gerar_regras_otimizado(qtd, amostragem=False)
        
        print(f"  Inserindo {qtd:,} regras...")
        inicio_ins = time.perf_counter_ns()
        for regra in regras:
            arv.insert(regra)
        fim_ins = time.perf_counter_ns()
        tempo_ins = (fim_ins - inicio_ins) / 1_000_000_000
        print(f"  Insercao concluida em {tempo_ins:.2f} s")
        
        qtd_remover = int(qtd * 0.2)
        
        if usar_amostragem and qtd_remover > 100000:
            remover_efetivo = 100000
            expiradas = random.sample(regras, remover_efetivo)
            print(f"  Usando amostra de {remover_efetivo:,} remocoes (de {qtd_remover:,})")
        else:
            remover_efetivo = qtd_remover
            expiradas = random.sample(regras, remover_efetivo)
        
        inicio = time.perf_counter_ns()
        for regra in expiradas:
            arv.remover(regra)
        fim = time.perf_counter_ns()
        
        tempo_total = (fim - inicio) / 1_000_000_000
        
        if remover_efetivo < qtd_remover:
            tempo_estimado_total = tempo_total * (qtd_remover / remover_efetivo)
            print(f"  Tempo amostra: {tempo_total:.3f} s")
            print(f"  Tempo total estimado: {tempo_estimado_total:.3f} s")
        else:
            tempo_estimado_total = tempo_total
        
        resultados.append({
            'volume': qtd,
            'nos_removidos': qtd_remover,
            'tempo_total_ns': int(tempo_estimado_total * 1_000_000_000),
            'tempo_medio_ns': (tempo_estimado_total / qtd_remover) * 1_000_000_000,
            'altura_final': get_altura(arv),
            'nos_finais': get_tamanho(arv)
        })
        
        print(f"  Tempo total: {tempo_estimado_total:.3f} s")
        print(f"  Tempo medio: {resultados[-1]['tempo_medio_ns']:.2f} ns/remocao")
        print(f"  Altura final: {get_altura(arv)}")
        
        del arv
        del regras
        gc.collect()
    
    return resultados


def simular_expiracao_lotes_otimizado_rb(tamanho_inicial=1000000, num_lotes=4, usar_amostragem=True):
    """Simula expiração em lotes para árvore RB"""
    
    print()
    print("========================================")
    print("  SIMULACAO DE EXPIRACAO POR LOTES (RB)")
    print("========================================")
    
    if tamanho_inicial > 500000 and usar_amostragem:
        print(f"\nATENCAO: {tamanho_inicial:,} nos pode levar muito tempo!")
        print("Usando tamanho reduzido para demonstracao: 100.000 nos")
        tamanho_inicial = 100000
    
    print(f"Nos iniciais: {tamanho_inicial:,}")
    print(f"Numero de lotes: {num_lotes}")
    print(f"Percentual por lote: 5%\n")
    
    print(f"Construindo arvore RB com {tamanho_inicial:,} regras...")
    arv = ArvoreRB()
    
    inicio_const = time.perf_counter_ns()
    for i, regra in enumerate(gerar_regras_insercao_direta(tamanho_inicial)):
        arv.insert(regra)
        if (i + 1) % max(1, tamanho_inicial // 10) == 0:
            percentual = ((i + 1) / tamanho_inicial) * 100
            print(f"  Insercao: {percentual:.0f}% ({i+1:,} nos)")
    
    fim_const = time.perf_counter_ns()
    tempo_const = (fim_const - inicio_const) / 1_000_000_000
    print(f"Arvore construida em {tempo_const:.2f} s")
    print(f"Altura inicial: {get_altura(arv)}")
    
    qtd_por_lote = int(tamanho_inicial * 0.05)
    regras_restantes = list(range(1, tamanho_inicial + 1))
    random.shuffle(regras_restantes)
    
    resultados_lotes = []
    
    for lote in range(1, num_lotes + 1):
        qtd_remover = min(qtd_por_lote, len(regras_restantes))
        if qtd_remover <= 0:
            break
        
        prioridades_lote = regras_restantes[:qtd_remover]
        regras_restantes = regras_restantes[qtd_remover:]
        
        print(f"\nLote {lote}: removendo {qtd_remover:,} regras...")
        
        inicio = time.perf_counter_ns()
        for prio in prioridades_lote:
            arv.remover(PacketRule(0, "", "", prio))
        fim = time.perf_counter_ns()
        
        tempo_lote = (fim - inicio) / 1_000_000_000
        resultados_lotes.append({
            'lote': lote,
            'nos_removidos': qtd_remover,
            'tempo_lote_s': tempo_lote,
            'tempo_medio_ns': (tempo_lote / qtd_remover) * 1_000_000_000,
            'nos_restantes': get_tamanho(arv),
            'altura_atual': get_altura(arv)
        })
        
        print(f"  Tempo: {tempo_lote:.3f} s")
        print(f"  Media: {resultados_lotes[-1]['tempo_medio_ns']:.2f} ns/remocao")
        print(f"  Nos restantes: {get_tamanho(arv):,} | Altura: {get_altura(arv)}")
    
    return resultados_lotes


# ========================================
# GRAFICOS OTIMIZADOS PARA RB
# ========================================

def plotar_tempos_individuais_rb(metricas, nome_teste="Simulacao"):
    """Gráfico de tempos individuais por remoção para RB"""
    if not metricas['tempos_individuais']:
        print("  Sem dados para grafico de tempos individuais")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    tempos_us = np.array(metricas['tempos_individuais']) / 1000.0
    
    ax.scatter(range(len(tempos_us)), tempos_us, c='blue', s=10, alpha=0.2, label='Tempo Individual')
    
    window_size = max(5, len(tempos_us) // 20)
    weights = np.ones(window_size) / window_size
    media_movel = np.convolve(tempos_us, weights, mode='valid')
    
    x_media_movel = np.arange(window_size - 1, len(tempos_us))
    ax.plot(x_media_movel, media_movel, color='darkorange', linewidth=2, label=f'Media Movel ({window_size} pts)')
    
    media = np.mean(tempos_us)
    mediana = np.median(tempos_us)
    ax.axhline(y=media, color='red', linestyle='--', alpha=0.8, label=f'Media Global: {media:.2f} µs')
    ax.axhline(y=mediana, color='green', linestyle='-.', alpha=0.8, label=f'Mediana: {mediana:.2f} µs')
    
    if len(tempos_us) > 100:
        limite_superior = np.percentile(tempos_us, 98)
        ax.set_ylim(0, limite_superior * 1.5)
    
    ax.set_xlabel('Numero da Remocao (amostrado)')
    ax.set_ylabel('Tempo (microssegundos)')
    ax.set_title(f'{nome_teste} (RB Tree) - Evolucao do Tempo de Remocao')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plotar_evolucao_altura_rb(metricas, nome_teste="Simulacao"):
    """Gráfico da evolução da altura durante as remoções para RB"""
    if not metricas['alturas_parciais']:
        print("  Sem dados para grafico de altura")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(metricas['alturas_parciais'], 'g-', linewidth=2, marker='o', markersize=3)
    
    ax.set_xlabel('Numero de Remocoes (amostrado)')
    ax.set_ylabel('Altura da Arvore RB')
    ax.set_title(f'{nome_teste} (RB Tree) - Evolucao da Altura Durante Remocoes')
    
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plotar_distribuicao_tempos_rb(metricas, nome_teste="Simulacao"):
    """Histograma da distribuição dos tempos para RB"""
    if not metricas['tempos_individuais']:
        print("  Sem dados para histograma")
        return
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    tempos_ns = np.array(metricas['tempos_individuais'])
    media = np.mean(tempos_ns)
    mediana = np.median(tempos_ns)
    
    limite_superior = np.percentile(tempos_ns, 99)
    tempos_filtrados = tempos_ns[tempos_ns <= limite_superior]
    
    ax.hist(tempos_filtrados, bins=40, edgecolor='black', alpha=0.7, color='skyblue')
    
    ax.axvline(x=media, color='red', linestyle='--', linewidth=2, label=f'Media Real: {media:.0f} ns')
    ax.axvline(x=mediana, color='green', linestyle='-', linewidth=2, label=f'Mediana Real: {mediana:.0f} ns')
    
    ax.set_xlabel('Tempo (nanossegundos)')
    ax.set_ylabel('Frequencia')
    ax.set_title(f'{nome_teste} (RB Tree) - Distribuicao dos Tempos')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plotar_rotacoes_recolorings(metricas, nome_teste="Simulacao"):
    """Gráfico da evolução de rotações e recolorings durante remoções"""
    if not metricas['rotacoes_parciais']:
        print("  Sem dados para grafico de rotacoes")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(metricas['rotacoes_parciais'], 'r-', linewidth=2, marker='s', markersize=3, label='Rotações')
    ax.plot(metricas['recolorings_parciais'], 'b-', linewidth=2, marker='o', markersize=3, label='Recolorings')
    
    ax.set_xlabel('Numero de Remocoes (amostrado)')
    ax.set_ylabel('Quantidade Acumulada')
    ax.set_title(f'{nome_teste} (RB Tree) - Evolucao de Rotacoes e Recolorings')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plotar_tempos_por_volume_rb(resultados):
    """Gráfico de tempo total vs volume de dados para RB"""
    if not resultados:
        print("  Sem dados para grafico de volumes")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    volumes = [r['volume'] for r in resultados]
    tempos_total = [r['tempo_total_ns'] / 1_000_000_000 for r in resultados]
    tempos_medio = [r['tempo_medio_ns'] for r in resultados]
    
    axes[0].plot(volumes, tempos_total, 'b-o', linewidth=2, markersize=8)
    axes[0].set_xlabel('Numero Total de Nos (Tamanho Inicial)')
    axes[0].set_ylabel('Tempo Total da Bateria (segundos)')
    axes[0].set_title('RB Tree - Escalabilidade: Tempo Total p/ Expirar 20%')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xscale('log')
    
    axes[1].plot(volumes, tempos_medio, 'r-o', linewidth=2, markersize=8)
    axes[1].set_xlabel('Numero Total de Nos')
    axes[1].set_ylabel('Tempo Medio por Remocao (ns)')
    axes[1].set_title('RB Tree - Desempenho Medio por Operacao O(log n)')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xscale('log')
    
    plt.tight_layout()
    plt.show()


def plotar_degradacao_lotes_rb(resultados_lotes):
    """Gráfico de degradação de performance por lote para RB"""
    if not resultados_lotes:
        print("  Sem dados para grafico de lotes")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    lotes = [r['lote'] for r in resultados_lotes]
    tempos_medio = [r['tempo_medio_ns'] for r in resultados_lotes]
    alturas = [r['altura_atual'] for r in resultados_lotes]
    nos_restantes = [r['nos_restantes'] for r in resultados_lotes]
    
    axes[0].plot(lotes, tempos_medio, 'darkred', marker='o', linewidth=2, markersize=8)
    axes[0].set_xlabel('Lote de Expiracao')
    axes[0].set_ylabel('Tempo Medio por Remocao (ns)')
    axes[0].set_title('RB Tree - Consistencia de Tempo a Cada Lote (5% removido)')
    axes[0].grid(True, alpha=0.3)
    axes[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    
    ax2_twin = axes[1].twinx()
    
    axes[1].plot(lotes, alturas, 'b-o', linewidth=2, markersize=8, label='Altura da Arvore RB')
    ax2_twin.plot(lotes, nos_restantes, 'g-s', linewidth=2, markersize=8, label='Nos Restantes')
    
    axes[1].set_xlabel('Lote de Expiracao')
    axes[1].set_ylabel('Altura da Arvore RB', color='b')
    ax2_twin.set_ylabel('Nos Restantes', color='g')
    
    axes[1].tick_params(axis='y', labelcolor='b')
    axes[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2_twin.tick_params(axis='y', labelcolor='g')
    
    axes[1].set_title('RB Tree - Impacto Estrutural: Altura x Capacidade')
    axes[1].grid(True, alpha=0.3)
    
    lines1, labels1 = axes[1].get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    axes[1].legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    plt.show()


def plotar_comparacao_avl_rb(resultados_avl, resultados_rb, nome_teste="Comparacao"):
    """Gráfico comparativo entre AVL e RB Tree"""
    if not resultados_avl or not resultados_rb:
        print("  Sem dados para comparacao")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    volumes = [r['volume'] for r in resultados_avl]
    
    # Tempo total
    tempos_total_avl = [r['tempo_total_ns'] / 1_000_000_000 for r in resultados_avl]
    tempos_total_rb = [r['tempo_total_ns'] / 1_000_000_000 for r in resultados_rb]
    
    axes[0, 0].plot(volumes, tempos_total_avl, 'b-o', linewidth=2, markersize=8, label='AVL')
    axes[0, 0].plot(volumes, tempos_total_rb, 'r-s', linewidth=2, markersize=8, label='RB Tree')
    axes[0, 0].set_xlabel('Numero Total de Nos')
    axes[0, 0].set_ylabel('Tempo Total (segundos)')
    axes[0, 0].set_title('Comparacao: Tempo Total de Remocao (20%)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_xscale('log')
    
    # Tempo médio
    tempo_medio_avl = [r['tempo_medio_ns'] for r in resultados_avl]
    tempo_medio_rb = [r['tempo_medio_ns'] for r in resultados_rb]
    
    axes[0, 1].plot(volumes, tempo_medio_avl, 'b-o', linewidth=2, markersize=8, label='AVL')
    axes[0, 1].plot(volumes, tempo_medio_rb, 'r-s', linewidth=2, markersize=8, label='RB Tree')
    axes[0, 1].set_xlabel('Numero Total de Nos')
    axes[0, 1].set_ylabel('Tempo Medio por Remocao (ns)')
    axes[0, 1].set_title('Comparacao: Tempo Medio por Remocao')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_xscale('log')
    
    # Altura final
    altura_avl = [r.get('altura_final', 0) for r in resultados_avl]
    altura_rb = [r.get('altura_final', 0) for r in resultados_rb]
    
    axes[1, 0].plot(volumes, altura_avl, 'b-o', linewidth=2, markersize=8, label='AVL')
    axes[1, 0].plot(volumes, altura_rb, 'r-s', linewidth=2, markersize=8, label='RB Tree')
    axes[1, 0].set_xlabel('Numero Total de Nos')
    axes[1, 0].set_ylabel('Altura Final da Arvore')
    axes[1, 0].set_title('Comparacao: Altura Final apos Remocoes')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_xscale('log')
    axes[1, 0].yaxis.set_major_locator(MaxNLocator(integer=True))
    
    # Ganho percentual RB vs AVL
    ganho = [(avl - rb) / avl * 100 if avl > 0 else 0 for avl, rb in zip(tempo_medio_avl, tempo_medio_rb)]
    
    cores = ['green' if g > 0 else 'red' for g in ganho]
    axes[1, 1].bar(range(len(volumes)), ganho, color=cores, alpha=0.7)
    axes[1, 1].set_xticks(range(len(volumes)))
    axes[1, 1].set_xticklabels([f'{v:,}' for v in volumes], rotation=45)
    axes[1, 1].set_xlabel('Numero Total de Nos')
    axes[1, 1].set_ylabel('Ganho RB sobre AVL (%)')
    axes[1, 1].set_title('Comparacao: Ganho de Performance (RB vs AVL)')
    axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=1)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


# ========================================
# TESTE COMPLETO PARA RB TREE
# ========================================

def teste_completo_com_graficos_otimizado_rb():
    """Executa simulação completa para RB Tree com todos os gráficos"""
    print()
    print("="*60)
    print(" TESTE COMPLETO - ARVORE RUBRO-NEGRA (RB Tree)")
    print(" SDN-Scale | Estrutura de Dados II")
    print("="*60)
    
    print("\nEscolha o tamanho do teste:")
    print("1. Teste rapido (10.000 nos) - ~5 segundos")
    print("2. Teste medio (50.000 nos) - ~30 segundos")
    print("3. Teste grande (100.000 nos) - ~2 minutos")
    print("4. Teste muito grande (250.000 nos) - ~10 minutos")
    print("5. Teste extremo (1.000.000 nos) - ~1 hora (use com cautela)")
    
    try:
        opcao = input("\nEscolha uma opcao (1-5): ").strip()
    except:
        opcao = "2"
    
    tamanhos = {
        "1": 10000,
        "2": 50000,
        "3": 100000,
        "4": 250000,
        "5": 1000000
    }
    
    tamanho = tamanhos.get(opcao, 50000)
    
    if tamanho >= 250000:
        print(f"\nATENCAO: Teste com {tamanho:,} nos pode levar varios minutos!")
        confirmar = input("Deseja continuar? (s/n): ").strip().lower()
        if confirmar != 's':
            print("Teste cancelado.")
            return
    
    print(f"\n[CENARIO] Arvore RB com {tamanho:,} regras")
    print("-" * 40)
    
    arv = ArvoreRB()
    regras = gerar_regras_otimizado(tamanho, amostragem=(tamanho >= 250000))
    
    print("Inserindo regras...")
    inicio_ins = time.perf_counter_ns()
    for i, regra in enumerate(regras):
        arv.insert(regra)
        if (i + 1) % max(1, tamanho // 10) == 0:
            percentual = ((i + 1) / tamanho) * 100
            print(f"  Insercao: {percentual:.0f}% ({i+1:,} nos)")
    
    fim_ins = time.perf_counter_ns()
    tempo_ins = (fim_ins - inicio_ins) / 1_000_000_000
    print(f"\nInsercao concluida em {tempo_ins:.2f} s")
    print(f"Total inserido: {get_tamanho(arv):,} nos")
    print(f"Altura inicial: {get_altura(arv)}")
    print(f"Rotacoes na insercao: {get_rotacoes(arv):,}")
    print(f"Recolorings na insercao: {get_recolorir(arv):,}")
    
    stats, metricas = simular_expiracao_detalhada_otimizada_rb(
        arv, regras, f"Teste RB {tamanho:,} nos", 
        usar_amostragem=(tamanho >= 100000)
    )
    
    print("\nGerando graficos...")
    
    plotar_tempos_individuais_rb(metricas, f"Expiracao RB - {tamanho:,} nos")
    plotar_evolucao_altura_rb(metricas, f"Expiracao RB - {tamanho:,} nos")
    plotar_distribuicao_tempos_rb(metricas, f"Expiracao RB - {tamanho:,} nos")
    plotar_rotacoes_recolorings(metricas, f"Expiracao RB - {tamanho:,} nos")
    
    if tamanho <= 100000:
        print("\n[CENARIO 2] Simulacao em multiplos volumes (RB)")
        print("-" * 40)
        volumes = [1000, 5000, 10000, 25000, 50000]
        resultados_volume = simular_expiracao_multiplos_volumes_otimizado_rb(volumes)
        plotar_tempos_por_volume_rb(resultados_volume)
    
    print("\n[CENARIO 3] Simulacao de expiracao por lotes (RB)")
    print("-" * 40)
    resultados_lotes = simular_expiracao_lotes_otimizado_rb(
        tamanho_inicial=min(tamanho, 100000), 
        num_lotes=4,
        usar_amostragem=(tamanho >= 100000)
    )
    plotar_degradacao_lotes_rb(resultados_lotes)
    
    print("\n" + "="*60)
    print(" TESTE RB CONCLUIDO COM SUCESSO!")
    print("="*60)


def teste_rapido_sem_graficos_rb():
    """Versão rápida sem gráficos para RB"""
    print()
    print("="*60)
    print(" TESTE RAPIDO RB - SIMULACAO DE EXPIRACAO")
    print("="*60)
    
    arv = ArvoreRB()
    regras = gerar_regras_otimizado(10000)
    
    print("Inserindo 10.000 regras na RB Tree...")
    for regra in regras:
        arv.insert(regra)
    
    stats, metricas = simular_expiracao_detalhada_otimizada_rb(arv, regras, "Teste Rapido RB")
    
    print("\nResumo rapido (RB Tree):")
    print(f"  Tempo total: {stats['tempo_total_ns']/1_000_000:.3f} ms")
    print(f"  Tempo medio: {stats['tempo_medio_ns']:.2f} ns/remocao")
    print(f"  Rotacoes totais: {stats['rotacoes_totais']}")
    print(f"  Recolorings totais: {stats['recolorings_totais']}")


# ========================================
# COMPARACAO ENTRE AVL E RB TREE
# ========================================

def comparar_avl_rb():
    """Executa comparação completa entre AVL e RB Tree"""
    print()
    print("="*60)
    print(" COMPARACAO: AVL x RB TREE")
    print("="*60)
    
    volumes = [1000, 5000, 10000, 25000, 50000]
    
    print("\nExecutando testes para AVL...")
    from avl import ArvoreAVL
    
    resultados_avl = []
    for qtd in volumes:
        print(f"\n--- AVL: Testando com {qtd:,} nos ---")
        arv = ArvoreAVL()
        regras = gerar_regras_otimizado(qtd, amostragem=False)
        
        for regra in regras:
            arv.insert(regra)
        
        qtd_remover = int(qtd * 0.2)
        expiradas = random.sample(regras, qtd_remover)
        
        inicio = time.perf_counter_ns()
        for regra in expiradas:
            arv.remover(regra)
        fim = time.perf_counter_ns()
        
        tempo_total = (fim - inicio) / 1_000_000_000
        
        resultados_avl.append({
            'volume': qtd,
            'tempo_total_ns': int(tempo_total * 1_000_000_000),
            'tempo_medio_ns': (tempo_total / qtd_remover) * 1_000_000_000,
            'altura_final': get_altura(arv)
        })
        
        print(f"  Tempo total: {tempo_total:.3f} s")
        print(f"  Tempo medio: {resultados_avl[-1]['tempo_medio_ns']:.2f} ns/remocao")
    
    print("\nExecutando testes para RB Tree...")
    resultados_rb = []
    for qtd in volumes:
        print(f"\n--- RB: Testando com {qtd:,} nos ---")
        arv = ArvoreRB()
        regras = gerar_regras_otimizado(qtd, amostragem=False)
        
        for regra in regras:
            arv.insert(regra)
        
        qtd_remover = int(qtd * 0.2)
        expiradas = random.sample(regras, qtd_remover)
        
        inicio = time.perf_counter_ns()
        for regra in expiradas:
            arv.remover(regra)
        fim = time.perf_counter_ns()
        
        tempo_total = (fim - inicio) / 1_000_000_000
        
        resultados_rb.append({
            'volume': qtd,
            'tempo_total_ns': int(tempo_total * 1_000_000_000),
            'tempo_medio_ns': (tempo_total / qtd_remover) * 1_000_000_000,
            'altura_final': get_altura(arv)
        })
        
        print(f"  Tempo total: {tempo_total:.3f} s")
        print(f"  Tempo medio: {resultados_rb[-1]['tempo_medio_ns']:.2f} ns/remocao")
    
    print("\nGerando graficos comparativos...")
    plotar_comparacao_avl_rb(resultados_avl, resultados_rb)
    
    # Tabela resumo
    print("\n" + "="*80)
    print(" TABELA COMPARATIVA RESUMO")
    print("="*80)
    print(f"{'Volume':<12} {'AVL (ns/rem)':<20} {'RB (ns/rem)':<20} {'Ganho RB':<15}")
    print("-"*80)
    for avl, rb in zip(resultados_avl, resultados_rb):
        ganho = ((avl['tempo_medio_ns'] - rb['tempo_medio_ns']) / avl['tempo_medio_ns']) * 100
        print(f"{avl['volume']:<12,} {avl['tempo_medio_ns']:<20,.2f} {rb['tempo_medio_ns']:<20,.2f} {ganho:>+.2f}%")
    print("="*80)


# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    print("\nEscolha o teste para Arvore Rubro-Negra (RB):")
    print("1. Teste completo RB com graficos")
    print("2. Teste rapido RB sem graficos")
    print("3. Comparacao AVL x RB Tree")
    print("4. Sair")
    
    try:
        opcao = input("\nEscolha uma opcao (1-4): ").strip()
    except:
        opcao = "1"
    
    if opcao == "1":
        teste_completo_com_graficos_otimizado_rb()
    elif opcao == "2":
        teste_rapido_sem_graficos_rb()
    elif opcao == "3":
        comparar_avl_rb()
    else:
        print("Saindo...")