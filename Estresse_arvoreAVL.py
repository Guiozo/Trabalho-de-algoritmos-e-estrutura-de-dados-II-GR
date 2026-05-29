import sys
sys.path.insert(0, '/mnt/agents/upload')

from avl import PacketRule, ArvoreAVL
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
    def _contar(node):
        if node is None:
            return 0
        return 1 + _contar(node.esquerda) + _contar(node.direita)
    return _contar(arv.raiz)


def altura_arvore(arv):
    def _altura(node):
        if node is None:
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


def reset_rotacoes(arv):
    if tem_metodo(arv, 'reset_rotacoes'):
        arv.reset_rotacoes()


# ========================================
# GERADOR DE REGRAS OTIMIZADO
# ========================================

def gerar_regras_otimizado(qtd, amostragem=False, amostra_tamanho=None):
    """Gera regras de forma otimizada, com opção de amostragem"""
    if amostragem and amostra_tamanho and amostra_tamanho < qtd:
        # Usar amostra menor para testes rápidos
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
# SIMULACAO DE EXPIRACAO OTIMIZADA
# ========================================

def simular_expiracao_detalhada_otimizada(arv, regras, nome_teste="Expiracao", usar_amostragem=False):
    """Simulação otimizada com coleta de métricas (remove EXATAMENTE 20%)"""
    qtd_atual = get_tamanho(arv)
    qtd_remover = int(qtd_atual * 0.2) # Calcula os 20% reais
    
    if qtd_remover > len(regras):
        qtd_remover = len(regras)
    
    # REMOVIDA a trava artificial de 50.000 nós. 
    # Agora o script vai sortear e remover os 20% completos da árvore.
    expiradas = random.sample(regras, qtd_remover)
    
    # Coletar métricas detalhadas
    metricas = {
        'tempos_individuais': [],
        'alturas_parciais': [],
        'rotacoes_parciais': [],
        'nos_restantes': []
    }
    
    reset_rotacoes(arv)
    
    inicio_total = time.perf_counter_ns()
    rotacoes_inicio = get_rotacoes(arv)
    
    # Coletar métricas a cada N remoções (para não sobrecarregar a memória com o gráfico)
    step = max(1, qtd_remover // 500)  # Coletar ~500 pontos no gráfico
    
    print(f"  Iniciando remocao de {qtd_remover:,} nos (20%)...")
    print(f"  Coletando metricas a cada {step} remocoes para o grafico...")
    
    for i, regra in enumerate(expiradas):
        inicio_remocao = time.perf_counter_ns()
        arv.remover(regra)
        fim_remocao = time.perf_counter_ns()
        
        # Coletar métricas apenas nos intervalos do step
        if i % step == 0 or i == qtd_remover - 1:
            metricas['tempos_individuais'].append(fim_remocao - inicio_remocao)
            metricas['alturas_parciais'].append(get_altura(arv))
            metricas['rotacoes_parciais'].append(get_rotacoes(arv) - rotacoes_inicio)
            metricas['nos_restantes'].append(get_tamanho(arv))
        
        # Mostrar progresso no terminal
        if (i + 1) % max(1, qtd_remover // 10) == 0:
            percentual = ((i + 1) / qtd_remover) * 100
            print(f"  Progresso: {percentual:.0f}% ({i+1:,} removidos de {qtd_remover:,})")
    
    fim_total = time.perf_counter_ns()
    
    tempo_total_ns = fim_total - inicio_total
    rotacoes_totais = get_rotacoes(arv) - rotacoes_inicio
    
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
        'altura_inicial': metricas['alturas_parciais'][0] if metricas['alturas_parciais'] else get_altura(arv),
        'altura_final': get_altura(arv),
        'nos_iniciais': qtd_atual,
        'nos_removidos': qtd_remover,
        'nos_finais': get_tamanho(arv)
    }
    
    # Exibir resultados
    print()
    print("========================================")
    print(f" {nome_teste} - RESULTADOS")
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
    print("--- ROTACOES ---")
    print(f"Rotacoes totais durante remocoes: {rotacoes_totais:,}")
    print(f"Media de rotacoes por remocao: {rotacoes_totais / qtd_remover:.2f}")
    
    return stats, metricas


    """Simulação otimizada com coleta de métricas (pode usar amostragem)"""
    qtd_atual = get_tamanho(arv)
    qtd_remover = int(qtd_atual * 0.2)
    
    if qtd_remover > len(regras):
        qtd_remover = len(regras)
    
    # Para grandes volumes, usar amostragem
    if usar_amostragem and qtd_remover > 50000:
        amostra_tamanho = 50000
        print(f"  Usando amostragem: {amostra_tamanho:,} de {qtd_remover:,} remocoes para analise")
        expiradas = random.sample(regras, amostra_tamanho)
        qtd_remover = amostra_tamanho
    else:
        expiradas = random.sample(regras, qtd_remover)
    
    # Coletar métricas detalhadas (apenas amostra)
    metricas = {
        'tempos_individuais': [],
        'alturas_parciais': [],
        'rotacoes_parciais': [],
        'nos_restantes': []
    }
    
    reset_rotacoes(arv)
    
    inicio_total = time.perf_counter_ns()
    rotacoes_inicio = get_rotacoes(arv)
    
    # Coletar métricas a cada N remoções (para não sobrecarregar)
    step = max(1, qtd_remover // 500)  # Coletar ~500 pontos
    
    print(f"  Coletando metricas a cada {step} remocoes...")
    
    for i, regra in enumerate(expiradas):
        inicio_remocao = time.perf_counter_ns()
        arv.remover(regra)
        fim_remocao = time.perf_counter_ns()
        
        # Coletar métricas apenas em intervalos
        if i % step == 0 or i == qtd_remover - 1:
            metricas['tempos_individuais'].append(fim_remocao - inicio_remocao)
            metricas['alturas_parciais'].append(get_altura(arv))
            metricas['rotacoes_parciais'].append(get_rotacoes(arv) - rotacoes_inicio)
            metricas['nos_restantes'].append(get_tamanho(arv))
        
        # Mostrar progresso
        if (i + 1) % max(1, qtd_remover // 10) == 0:
            percentual = ((i + 1) / qtd_remover) * 100
            print(f"  Progresso: {percentual:.0f}% ({i+1:,} removidos)")
    
    fim_total = time.perf_counter_ns()
    
    tempo_total_ns = fim_total - inicio_total
    rotacoes_totais = get_rotacoes(arv) - rotacoes_inicio
    
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
        'altura_inicial': metricas['alturas_parciais'][0] if metricas['alturas_parciais'] else get_altura(arv),
        'altura_final': get_altura(arv),
        'nos_iniciais': qtd_atual,
        'nos_removidos': qtd_remover,
        'nos_finais': get_tamanho(arv)
    }
    
    # Exibir resultados
    print()
    print("========================================")
    print(f" {nome_teste} - RESULTADOS")
    print("========================================")
    print(f"Nos totais antes: {qtd_atual:,}")
    print(f"Nos removidos (20%): {qtd_remover:,}")
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
    print("--- ROTACOES ---")
    print(f"Rotacoes totais durante remocoes: {rotacoes_totais}")
    print(f"Media de rotacoes por remocao: {rotacoes_totais / qtd_remover:.2f}")
    
    return stats, metricas


def simular_expiracao_multiplos_volumes_otimizado(volumes, usar_amostragem=True):
    """Simula expiração em diferentes volumes de dados (otimizado)"""
    resultados = []
    
    print()
    print("========================================")
    print("  SIMULACAO EM MULTIPLOS VOLUMES")
    print("========================================")
    
    for qtd in volumes:
        print(f"\n--- Testando com {qtd:,} nos ---")
        
        # Estimar tempo
        if qtd >= 500000:
            print(f"  ATENCAO: Este teste pode levar varios minutos...")
        
        arv = ArvoreAVL()
        regras = gerar_regras_otimizado(qtd, amostragem=False)
        
        # Inserção
        print(f"  Inserindo {qtd:,} regras...")
        inicio_ins = time.perf_counter_ns()
        for regra in regras:
            arv.insert(regra)
        fim_ins = time.perf_counter_ns()
        tempo_ins = (fim_ins - inicio_ins) / 1_000_000_000
        print(f"  Insercao concluida em {tempo_ins:.2f} s")
        
        # Simulação de expiração
        qtd_remover = int(qtd * 0.2)
        
        # Para grandes volumes, usar menos remoções na simulação
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
        
        # Estimar tempo total se fosse remover todos
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
        
        # Limpar memória
        del arv
        del regras
        gc.collect()
    
    return resultados


def simular_expiracao_lotes_otimizado(tamanho_inicial=1000000, num_lotes=4, usar_amostragem=True):
    """Simula expiração em lotes de forma otimizada"""
    
    print()
    print("========================================")
    print("  SIMULACAO DE EXPIRACAO POR LOTES")
    print("========================================")
    
    # Ajustar tamanho se for muito grande
    if tamanho_inicial > 500000 and usar_amostragem:
        print(f"\nATENCAO: {tamanho_inicial:,} nos pode levar muito tempo!")
        print("Usando tamanho reduzido para demonstracao: 100.000 nos")
        tamanho_inicial = 100000
    
    print(f"Nos iniciais: {tamanho_inicial:,}")
    print(f"Numero de lotes: {num_lotes}")
    print(f"Percentual por lote: 5%\n")
    
    # Construir árvore
    print(f"Construindo arvore com {tamanho_inicial:,} regras...")
    arv = ArvoreAVL()
    
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
# GRAFICOS OTIMIZADOS E CONSISTENTES
# ========================================

def plotar_tempos_individuais(metricas, nome_teste="Simulacao"):
    """Gráfico de tempos individuais por remoção com Média Móvel e controle de Outliers"""
    if not metricas['tempos_individuais']:
        print("  Sem dados para grafico de tempos individuais")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Converter para microssegundos
    tempos_us = np.array(metricas['tempos_individuais']) / 1000.0
    
    # Plotar os pontos individuais (com mais transparência para não poluir)
    ax.scatter(range(len(tempos_us)), tempos_us, c='blue', s=10, alpha=0.2, label='Tempo Individual')
    
    # 1. Calcular Média Móvel (suaviza o ruído para mostrar a tendência real)
    # A janela se ajusta dinamicamente ao tamanho da amostra (ex: 5% da amostra)
    window_size = max(5, len(tempos_us) // 20) 
    weights = np.ones(window_size) / window_size
    media_movel = np.convolve(tempos_us, weights, mode='valid')
    
    # Ajustar o eixo X da média móvel para alinhar com os dados
    x_media_movel = np.arange(window_size - 1, len(tempos_us))
    ax.plot(x_media_movel, media_movel, color='darkorange', linewidth=2, label=f'Media Movel ({window_size} pts)')
    
    # 2. Média e Mediana globais
    media = np.mean(tempos_us)
    mediana = np.median(tempos_us)
    ax.axhline(y=media, color='red', linestyle='--', alpha=0.8, label=f'Media Global: {media:.2f} µs')
    ax.axhline(y=mediana, color='green', linestyle='-.', alpha=0.8, label=f'Mediana: {mediana:.2f} µs')
    
    # 3. Limitar o Eixo Y para ignorar picos anormais do Garbage Collector (Top 2%)
    if len(tempos_us) > 100:
        limite_superior = np.percentile(tempos_us, 98)
        ax.set_ylim(0, limite_superior * 1.5) # Dá 50% de respiro acima do p98
    
    ax.set_xlabel('Numero da Remocao (amostrado)')
    ax.set_ylabel('Tempo (microssegundos)')
    ax.set_title(f'{nome_teste} - Evolucao do Tempo de Remocao')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plotar_evolucao_altura(metricas, nome_teste="Simulacao"):
    """Gráfico da evolução da altura durante as remoções"""
    if not metricas['alturas_parciais']:
        print("  Sem dados para grafico de altura")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(metricas['alturas_parciais'], 'g-', linewidth=2, marker='o', markersize=3)
    
    ax.set_xlabel('Numero de Remocoes (amostrado)')
    ax.set_ylabel('Altura da Arvore')
    ax.set_title(f'{nome_teste} - Evolucao da Altura Durante Remocoes')
    
    # Forçar o eixo Y a usar números inteiros (altura não tem decimais)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plotar_distribuicao_tempos(metricas, nome_teste="Simulacao"):
    """Histograma da distribuição dos tempos (ignora outliers extremos)"""
    if not metricas['tempos_individuais']:
        print("  Sem dados para histograma")
        return
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    tempos_ns = np.array(metricas['tempos_individuais'])
    media = np.mean(tempos_ns)
    mediana = np.median(tempos_ns)
    
    # Remover o 1% mais alto apenas para a visualização do histograma
    # Isso impede que o histograma vire uma barra única esmagada à esquerda
    limite_superior = np.percentile(tempos_ns, 99)
    tempos_filtrados = tempos_ns[tempos_ns <= limite_superior]
    
    ax.hist(tempos_filtrados, bins=40, edgecolor='black', alpha=0.7, color='skyblue')
    
    ax.axvline(x=media, color='red', linestyle='--', linewidth=2, label=f'Media Real: {media:.0f} ns')
    ax.axvline(x=mediana, color='green', linestyle='-', linewidth=2, label=f'Mediana Real: {mediana:.0f} ns')
    
    ax.set_xlabel('Tempo (nanossegundos)')
    ax.set_ylabel('Frequencia')
    ax.set_title(f'{nome_teste} - Distribuicao dos Tempos (Top 1% outliers omitidos na viz)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plotar_tempos_por_volume(resultados):
    """Gráfico de tempo total vs volume de dados"""
    if not resultados:
        print("  Sem dados para grafico de volumes")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    volumes = [r['volume'] for r in resultados]
    tempos_total = [r['tempo_total_ns'] / 1_000_000_000 for r in resultados]  # segundos
    tempos_medio = [r['tempo_medio_ns'] for r in resultados]
    
    # Gráfico 1: Tempo total
    axes[0].plot(volumes, tempos_total, 'b-o', linewidth=2, markersize=8)
    axes[0].set_xlabel('Numero Total de Nos (Tamanho Inicial)')
    axes[0].set_ylabel('Tempo Total da Bateria (segundos)')
    axes[0].set_title('Escalabilidade: Tempo Total p/ Expirar 20%')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xscale('log')
    
    # Gráfico 2: Tempo médio
    axes[1].plot(volumes, tempos_medio, 'r-o', linewidth=2, markersize=8)
    axes[1].set_xlabel('Numero Total de Nos')
    axes[1].set_ylabel('Tempo Medio por Remocao (ns)')
    axes[1].set_title('Desempenho Medio por Operacao O(log n)')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xscale('log')
    
    plt.tight_layout()
    plt.show()


def plotar_degradacao_lotes(resultados_lotes):
    """Gráfico de degradação de performance por lote"""
    if not resultados_lotes:
        print("  Sem dados para grafico de lotes")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    lotes = [r['lote'] for r in resultados_lotes]
    tempos_medio = [r['tempo_medio_ns'] for r in resultados_lotes]
    alturas = [r['altura_atual'] for r in resultados_lotes]
    nos_restantes = [r['nos_restantes'] for r in resultados_lotes]
    
    # Gráfico 1: Degradação do tempo médio
    axes[0].plot(lotes, tempos_medio, 'darkred', marker='o', linewidth=2, markersize=8)
    axes[0].set_xlabel('Lote de Expiracao')
    axes[0].set_ylabel('Tempo Medio por Remocao (ns)')
    axes[0].set_title('Consistencia de Tempo a Cada Lote (5% removido)')
    axes[0].grid(True, alpha=0.3)
    
    # Forçar os X-ticks a serem inteiros (Lote 1, Lote 2, etc.)
    axes[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    
    # Gráfico 2: Altura e nós restantes
    ax2_twin = axes[1].twinx()
    
    axes[1].plot(lotes, alturas, 'b-o', linewidth=2, markersize=8, label='Altura da Arvore')
    ax2_twin.plot(lotes, nos_restantes, 'g-s', linewidth=2, markersize=8, label='Nos Restantes')
    
    axes[1].set_xlabel('Lote de Expiracao')
    axes[1].set_ylabel('Altura da Arvore', color='b')
    ax2_twin.set_ylabel('Nos Restantes', color='g')
    
    axes[1].tick_params(axis='y', labelcolor='b')
    axes[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2_twin.tick_params(axis='y', labelcolor='g')
    
    axes[1].set_title('Impacto Estrutural: Altura x Capacidade')
    axes[1].grid(True, alpha=0.3)
    
    # Legendas combinadas
    lines1, labels1 = axes[1].get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    axes[1].legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    plt.show()


# ========================================
# TESTE COMPLETO COM GRAFICOS (OTIMIZADO)
# ========================================

def teste_completo_com_graficos_otimizado():
    """Executa simulação completa com todos os gráficos (versão otimizada)"""
    print()
    print("="*60)
    print(" TESTE COMPLETO DE SIMULACAO DE EXPIRACAO")
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
    
    print(f"\n[CENARIO] Arvore com {tamanho:,} regras")
    print("-" * 40)
    
    arv = ArvoreAVL()
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
    
    # Simulação detalhada (com amostragem para grandes volumes)
    stats, metricas = simular_expiracao_detalhada_otimizada(
        arv, regras, f"Teste {tamanho:,}k", 
        usar_amostragem=(tamanho >= 100000)
    )
    
    # Gráficos
    print("\nGerando graficos...")
    
    plotar_tempos_individuais(metricas, f"Expiracao - {tamanho:,} nos")
    plotar_evolucao_altura(metricas, f"Expiracao - {tamanho:,} nos")
    plotar_distribuicao_tempos(metricas, f"Expiracao - {tamanho:,} nos")
    
    # Simulação em múltiplos volumes (apenas para tamanhos menores)
    if tamanho <= 100000:
        print("\n[CENARIO 2] Simulacao em multiplos volumes")
        print("-" * 40)
        volumes = [1000, 5000, 10000, 25000, 50000]
        resultados_volume = simular_expiracao_multiplos_volumes_otimizado(volumes)
        plotar_tempos_por_volume(resultados_volume)
    
    # Simulação por lotes (versão otimizada)
    print("\n[CENARIO 3] Simulacao de expiracao por lotes")
    print("-" * 40)
    resultados_lotes = simular_expiracao_lotes_otimizado(
        tamanho_inicial=min(tamanho, 100000), 
        num_lotes=4,
        usar_amostragem=(tamanho >= 100000)
    )
    plotar_degradacao_lotes(resultados_lotes)
    
    print("\n" + "="*60)
    print(" TESTE CONCLUIDO COM SUCESSO!")
    print("="*60)


def teste_rapido_sem_graficos():
    """Versão rápida sem gráficos"""
    print()
    print("="*60)
    print(" TESTE RAPIDO - SIMULACAO DE EXPIRACAO")
    print("="*60)
    
    arv = ArvoreAVL()
    regras = gerar_regras_otimizado(10000)
    
    print("Inserindo 10.000 regras...")
    for regra in regras:
        arv.insert(regra)
    
    stats, metricas = simular_expiracao_detalhada_otimizada(arv, regras, "Teste Rapido")
    
    print("\nResumo rapido:")
    print(f"  Tempo total: {stats['tempo_total_ns']/1_000_000:.3f} ms")
    print(f"  Tempo medio: {stats['tempo_medio_ns']:.2f} ns/remocao")
    print(f"  Rotacoes totais: {stats['rotacoes_totais']}")


# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    # Para executar a simulação completa com gráficos (otimizada):
    teste_completo_com_graficos_otimizado()
    
    # Para executar a versão rápida sem gráficos:
    # teste_rapido_sem_graficos()