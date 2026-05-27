import sys
sys.path.insert(0, '/mnt/agents/upload')

from avl import PacketRule
from avl import ArvoreAVL


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


def teste_insercao_basica():
    print()
    print("========================================")
    print("  TESTE: INSERCAO BASICA")
    print("========================================")

    arv = ArvoreAVL()

    r1 = PacketRule(1, "10.0.0.1", "192.168.1.1", 50)
    r2 = PacketRule(2, "10.0.0.2", "192.168.1.2", 30)
    r3 = PacketRule(3, "10.0.0.3", "192.168.1.3", 70)
    r4 = PacketRule(4, "10.0.0.4", "192.168.1.4", 20)
    r5 = PacketRule(5, "10.0.0.5", "192.168.1.5", 40)

    print("Inserindo regras em ordem que causa desbalanceamento:")
    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r4)
    arv.insert(r3)
    arv.insert(r5)

    print("Total de nos:", get_tamanho(arv))
    print("Rotacoes realizadas:", get_rotacoes(arv))
    print("Altura da arvore:", get_altura(arv))

    assert get_tamanho(arv) == 5, "ERRO: Tamanho deve ser 5"
    assert get_altura(arv) <= 3, "ERRO: Altura deve ser <= 3 para 5 nos balanceados"
    print("[OK] Insercao basica validada!")


def teste_rotacao_simples_direita():
    print()
    print("========================================")
    print("  TESTE: ROTACAO SIMPLES A DIREITA (Caso LL)")
    print("========================================")

    arv = ArvoreAVL()

    r1 = PacketRule(10, "10.0.0.10", "192.168.1.10", 100)
    r2 = PacketRule(9, "10.0.0.9", "192.168.1.9", 90)
    r3 = PacketRule(8, "10.0.0.8", "192.168.1.8", 80)

    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r3)

    print("Inseridos nos com prioridades: 100, 90, 80")
    print("Total de nos:", get_tamanho(arv))
    print("Rotacoes realizadas:", get_rotacoes(arv))
    print("Altura da arvore:", get_altura(arv))

    assert get_rotacoes(arv) >= 1, "ERRO: Deve ter ocorrido pelo menos 1 rotacao"
    assert get_altura(arv) == 2, "ERRO: Altura deve ser 2 apos balanceamento"
    print("[OK] Rotacao simples a direita validada!")


def teste_rotacao_simples_esquerda():
    print()
    print("========================================")
    print("  TESTE: ROTACAO SIMPLES A ESQUERDA (Caso RR)")
    print("========================================")

    arv = ArvoreAVL()

    r1 = PacketRule(1, "10.0.0.1", "192.168.1.1", 10)
    r2 = PacketRule(2, "10.0.0.2", "192.168.1.2", 20)
    r3 = PacketRule(3, "10.0.0.3", "192.168.1.3", 30)

    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r3)

    print("Inseridos nos com prioridades: 10, 20, 30")
    print("Total de nos:", get_tamanho(arv))
    print("Rotacoes realizadas:", get_rotacoes(arv))
    print("Altura da arvore:", get_altura(arv))

    assert get_rotacoes(arv) >= 1, "ERRO: Deve ter ocorrido pelo menos 1 rotacao"
    assert get_altura(arv) == 2, "ERRO: Altura deve ser 2 apos balanceamento"
    print("[OK] Rotacao simples a esquerda validada!")


def teste_rotacao_dupla_lr():
    print()
    print("========================================")
    print("  TESTE: ROTACAO DUPLA ESQUERDA-DIREITA (Caso LR)")
    print("========================================")

    arv = ArvoreAVL()

    r1 = PacketRule(5, "10.0.0.5", "192.168.1.5", 50)
    r2 = PacketRule(3, "10.0.0.3", "192.168.1.3", 30)
    r3 = PacketRule(4, "10.0.0.4", "192.168.1.4", 40)

    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r3)

    print("Inseridos nos com prioridades: 50, 30, 40")
    print("Total de nos:", get_tamanho(arv))
    print("Rotacoes realizadas:", get_rotacoes(arv))
    print("Altura da arvore:", get_altura(arv))

    assert get_rotacoes(arv) >= 2, "ERRO: Deve ter ocorrido pelo menos 2 rotacoes (dupla)"
    assert get_altura(arv) == 2, "ERRO: Altura deve ser 2 apos balanceamento"
    print("[OK] Rotacao dupla LR validada!")


def teste_rotacao_dupla_rl():
    print()
    print("========================================")
    print("  TESTE: ROTACAO DUPLA DIREITA-ESQUERDA (Caso RL)")
    print("========================================")

    arv = ArvoreAVL()

    r1 = PacketRule(1, "10.0.0.1", "192.168.1.1", 10)
    r2 = PacketRule(3, "10.0.0.3", "192.168.1.3", 30)
    r3 = PacketRule(2, "10.0.0.2", "192.168.1.2", 20)

    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r3)

    print("Inseridos nos com prioridades: 10, 30, 20")
    print("Total de nos:", get_tamanho(arv))
    print("Rotacoes realizadas:", get_rotacoes(arv))
    print("Altura da arvore:", get_altura(arv))

    assert get_rotacoes(arv) >= 2, "ERRO: Deve ter ocorrido pelo menos 2 rotacoes (dupla)"
    assert get_altura(arv) == 2, "ERRO: Altura deve ser 2 apos balanceamento"
    print("[OK] Rotacao dupla RL validada!")


def teste_busca():
    print()
    print("========================================")
    print("  TESTE: BUSCA")
    print("========================================")

    arv = ArvoreAVL()
    prioridades = [15, 6, 18, 3, 7, 17, 20, 2, 4, 13]

    print("Inserindo 10 regras com prioridades variadas:")
    for i, prio in enumerate(prioridades):
        regra = PacketRule(i+1, "10.0.0." + str(i+1), "192.168.1." + str(i+1), prio)
        arv.insert(regra)
        print("  Inserido [ID:" + str(i+1) + ", Prioridade:" + str(prio) + "]")

    print()
    print("Total de nos inseridos:", get_tamanho(arv))
    print("Rotacoes totais:", get_rotacoes(arv))

    print()
    print("Buscando prioridades existentes:")
    buscar_existentes = [18, 7, 20, 13]
    for prio in buscar_existentes:
        encontrado = arv.buscar(PacketRule(0, "", "", prio))
        if encontrado:
            print("  Prioridade " + str(prio) + " encontrada: " + str(encontrado))
        else:
            print("  [FALHA] Prioridade " + str(prio) + " nao encontrada!")
        assert encontrado, "ERRO: Prioridade " + str(prio) + " deveria existir"

    print()
    print("Buscando prioridades inexistentes:")
    buscar_inexistentes = [99, 100, 200]
    for prio in buscar_inexistentes:
        encontrado = arv.buscar(PacketRule(0, "", "", prio))
        if not encontrado:
            print("  Prioridade " + str(prio) + " nao encontrada (correto)")
        else:
            print("  [FALHA] Prioridade " + str(prio) + " foi encontrada inesperadamente!")
        assert not encontrado, "ERRO: Prioridade " + str(prio) + " nao deveria existir"

    print("[OK] Busca validada!")


def teste_remocao():
    print()
    print("========================================")
    print("  TESTE: REMOCAO")
    print("========================================")

    arv = ArvoreAVL()

    rem1 = PacketRule(1, "10.0.0.1", "192.168.1.1", 100)
    rem2 = PacketRule(2, "10.0.0.2", "192.168.1.2", 90)
    rem3 = PacketRule(3, "10.0.0.3", "192.168.1.3", 80)
    rem4 = PacketRule(4, "10.0.0.4", "192.168.1.4", 70)
    rem5 = PacketRule(5, "10.0.0.5", "192.168.1.5", 60)

    arv.insert(rem1)
    arv.insert(rem2)
    arv.insert(rem3)
    arv.insert(rem4)
    arv.insert(rem5)

    print("Estado inicial:", get_tamanho(arv), "nos")
    print("Rotacoes iniciais:", get_rotacoes(arv))

    print()
    print("Remover folha (prio=60):")
    arv.remover(rem5)
    print("Nos apos remocao:", get_tamanho(arv))
    print("Rotacoes:", get_rotacoes(arv))
    assert get_tamanho(arv) == 4, "ERRO: Deve ter 4 nos"

    print()
    print("Remover no com um filho (prio=80):")
    arv.remover(rem3)
    print("Nos apos remocao:", get_tamanho(arv))
    print("Rotacoes:", get_rotacoes(arv))
    assert get_tamanho(arv) == 3, "ERRO: Deve ter 3 nos"

    print()
    print("Remover no com dois filhos (prio=90):")
    arv.remover(rem2)
    print("Nos apos remocao:", get_tamanho(arv))
    print("Rotacoes:", get_rotacoes(arv))
    assert get_tamanho(arv) == 2, "ERRO: Deve ter 2 nos"

    print()
    print("Remover raiz (prio=100):")
    arv.remover(rem1)
    print("Nos apos remocao:", get_tamanho(arv))
    print("Rotacoes:", get_rotacoes(arv))
    assert get_tamanho(arv) == 1, "ERRO: Deve ter 1 no"

    print("[OK] Remocao validada!")


def teste_prioridades_iguais():
    print()
    print("========================================")
    print("  TESTE: PRIORIDADES IGUAIS")
    print("========================================")

    arv = ArvoreAVL()

    igual1 = PacketRule(10, "10.0.0.10", "192.168.1.10", 50)
    igual2 = PacketRule(5, "10.0.0.5", "192.168.1.5", 50)
    igual3 = PacketRule(1, "10.0.0.1", "192.168.1.1", 50)

    arv.insert(igual1)
    arv.insert(igual2)
    arv.insert(igual3)

    print("Inseridas 3 regras com prioridade 50 (IDs: 10, 5, 1)")
    print("Total de nos:", get_tamanho(arv))
    print("Rotacoes:", get_rotacoes(arv))
    print("Nota: A AVL pode descartar duplicatas de prioridade (mantem apenas a primeira)")

    buscado = arv.buscar(PacketRule(0, "", "", 50))
    if buscado:
        print("Busca por prioridade 50 retornou:", buscado)
    else:
        print("[FALHA] Busca por prioridade 50 falhou!")

    assert buscado is not None, "ERRO: Deve encontrar a regra com prio 50"
    print("[OK] Prioridades iguais validadas!")


def teste_estresse():
    print()
    print("========================================")
    print("  TESTE: CENARIO DE ESTRESSE")
    print("========================================")

    arv = ArvoreAVL()

    print("Inserindo 50 regras em ordem decrescente...")
    for i in range(100, 50, -1):
        regra = PacketRule(i, "10.0.0." + str(i), "192.168.1." + str(i), i)
        arv.insert(regra)

    print("Nos inseridos:", get_tamanho(arv))
    print("Rotacoes realizadas:", get_rotacoes(arv))
    print("Altura da arvore:", get_altura(arv))

    import math
    n = get_tamanho(arv)
    altura_maxima = 1.44 * math.log2(n + 2)
    print("Altura maxima teorica (AVL):", round(altura_maxima, 2))
    print("Altura real:", get_altura(arv))

    assert get_tamanho(arv) == 50, "ERRO: Deve ter 50 nos"
    assert get_altura(arv) < altura_maxima, "ERRO: Altura " + str(get_altura(arv)) + " excede limite teorico " + str(round(altura_maxima, 2))

    print()
    print("Removendo 25 regras aleatoriamente...")
    for i in range(100, 75, -1):
        regra = PacketRule(i, "10.0.0." + str(i), "192.168.1." + str(i), i)
        arv.remover(regra)

    print("Nos restantes:", get_tamanho(arv))
    print("Altura apos remocoes:", get_altura(arv))

    assert get_tamanho(arv) == 25, "ERRO: Deve ter 25 nos restantes"
    print("[OK] Cenario de estresse validado!")


def teste_invariante_fb():
    print()
    print("========================================")
    print("  TESTE: INVARIANTE DO FATOR DE BALANCEAMENTO")
    print("========================================")

    arv = ArvoreAVL()

    print("Inserindo 20 regras aleatorias...")
    import random
    rng = random.Random(42)
    for i in range(20):
        prio = rng.randint(1, 1000)
        regra = PacketRule(i, "10.0.0." + str(i), "192.168.1." + str(i), prio)
        arv.insert(regra)

    print("Nos inseridos:", get_tamanho(arv))
    print("Altura:", get_altura(arv))

    def verificar_fb(node):
        if node is None:
            return True
        # Calcula FB manualmente se o metodo nao existir
        if tem_metodo(arv, '_fator_balanceamento'):
            fb = arv._fator_balanceamento(node)
        else:
            def alt(node):
                if node is None:
                    return 0
                return 1 + max(alt(node.esquerda), alt(node.direita))
            fb = alt(node.esquerda) - alt(node.direita)
        if abs(fb) > 1:
            print("  [FALHA] No com prio=" + str(node.valor.priority) + " tem FB=" + str(fb))
            return False
        return verificar_fb(node.esquerda) and verificar_fb(node.direita)

    valido = verificar_fb(arv.raiz)
    if valido:
        print("  Todos os nos respeitam |FB| <= 1")
        print("[OK] Invariante de balanceamento validada!")
    else:
        print("[FALHA] Invariante de balanceamento violada!")
        assert False, "Invariante |FB| <= 1 violada"


def main():
    print()
    print("========================================")
    print("  Testes Unitarios - Arvore AVL")
    print("  SDN-Scale | Estrutura de Dados II")
    print("========================================")
    print()

    teste_insercao_basica()
    teste_rotacao_simples_direita()
    teste_rotacao_simples_esquerda()
    teste_rotacao_dupla_lr()
    teste_rotacao_dupla_rl()
    teste_busca()
    teste_remocao()
    teste_prioridades_iguais()
    teste_estresse()
    teste_invariante_fb()

    print()
    print("========================================")
    print("  TODOS OS TESTES AVL CONCLUIDOS")
    print("========================================")
    print()
    print("Estatisticas gerais:")
    print("  - Insercao testada")
    print("  - Rotacoes simples testadas (LL e RR)")
    print("  - Rotacoes duplas testadas (LR e RL)")
    print("  - Busca testada")
    print("  - Remocao testada (folha, 1 filho, 2 filhos, raiz)")
    print("  - Prioridades iguais testadas")
    print("  - Cenario de estresse concluido")
    print("  - Invariante |FB| <= 1 verificada")
    print()
    print("[OK] Todos os testes passaram com sucesso!")
    print()


if __name__ == "__main__":
    main()
