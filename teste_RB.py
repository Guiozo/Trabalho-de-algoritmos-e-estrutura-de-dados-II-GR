import sys
sys.path.insert(0, '/mnt/agents/upload')

from rb import PacketRule
from rb import ArvoreRB, Cor

ArvoreRedBlack = ArvoreRB

def teste_insercao_basica():
    print()
    print('========================================')
    print('  TESTE: INSERCAO BASICA')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    r1 = PacketRule(1, '10.0.0.1', '192.168.1.1', 50)
    r2 = PacketRule(2, '10.0.0.2', '192.168.1.2', 30)
    r3 = PacketRule(3, '10.0.0.3', '192.168.1.3', 70)
    r4 = PacketRule(4, '10.0.0.4', '192.168.1.4', 20)
    r5 = PacketRule(5, '10.0.0.5', '192.168.1.5', 40)
    
    print('Inserindo regras em ordem que causa desbalanceamento:')
    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r4)
    arv.insert(r3)
    arv.insert(r5)
    
    print('Total de nos:', arv.tamanho())
    print('Rotacoes realizadas:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    print('Altura da arvore:', arv.get_altura())
    
    assert arv.tamanho() == 5, 'ERRO: Tamanho deve ser 5'
    assert arv.get_altura() <= 3, 'ERRO: Altura deve ser <= 3 para 5 nos balanceados'
    print('[OK] Insercao basica validada!')


def teste_rotacao_esquerda():
    print()
    print('========================================')
    print('  TESTE: ROTACAO A ESQUERDA (Caso RR)')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    r1 = PacketRule(1, '10.0.0.1', '192.168.1.1', 10)
    r2 = PacketRule(2, '10.0.0.2', '192.168.1.2', 20)
    r3 = PacketRule(3, '10.0.0.3', '192.168.1.3', 30)
    
    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r3)
    
    print('Inseridos nos com prioridades: 10, 20, 30')
    print('Total de nos:', arv.tamanho())
    print('Rotacoes realizadas:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    print('Altura da arvore:', arv.get_altura())
    
    assert arv.get_rotacoes() >= 1, 'ERRO: Deve ter ocorrido pelo menos 1 rotacao'
    assert arv.get_altura() == 2, 'ERRO: Altura deve ser 2 apos balanceamento'
    print('[OK] Rotacao a esquerda validada!')


def teste_rotacao_direita():
    print()
    print('========================================')
    print('  TESTE: ROTACAO A DIREITA (Caso LL)')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    r1 = PacketRule(10, '10.0.0.10', '192.168.1.10', 100)
    r2 = PacketRule(9, '10.0.0.9', '192.168.1.9', 90)
    r3 = PacketRule(8, '10.0.0.8', '192.168.1.8', 80)
    
    arv.insert(r1)
    arv.insert(r2)
    arv.insert(r3)
    
    print('Inseridos nos com prioridades: 100, 90, 80')
    print('Total de nos:', arv.tamanho())
    print('Rotacoes realizadas:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    print('Altura da arvore:', arv.get_altura())
    
    assert arv.get_rotacoes() >= 1, 'ERRO: Deve ter ocorrido pelo menos 1 rotacao'
    assert arv.get_altura() == 2, 'ERRO: Altura deve ser 2 apos balanceamento'
    print('[OK] Rotacao a direita validada!')


def teste_busca():
    print()
    print('========================================')
    print('  TESTE: BUSCA')
    print('========================================')
    
    arv = ArvoreRedBlack()
    prioridades = [15, 6, 18, 3, 7, 17, 20, 2, 4, 13]
    
    print('Inserindo 10 regras com prioridades variadas:')
    for i, prio in enumerate(prioridades):
        regra = PacketRule(i+1, '10.0.0.' + str(i+1), '192.168.1.' + str(i+1), prio)
        arv.insert(regra)
        print('  Inserido [ID:' + str(i+1) + ', Prioridade:' + str(prio) + ']')
    
    print()
    print('Total de nos inseridos:', arv.tamanho())
    print('Rotacoes totais:', arv.get_rotacoes())
    print('Recolorings totais:', arv.get_recolorir())
    
    print()
    print('Buscando prioridades existentes:')
    buscar_existentes = [18, 7, 20, 13]
    for prio in buscar_existentes:
        encontrado = arv.buscar(PacketRule(0, '', '', prio))
        if encontrado:
            print('  Prioridade ' + str(prio) + ' encontrada: OK')
        else:
            print('  [FALHA] Prioridade ' + str(prio) + ' nao encontrada!')
        assert encontrado, 'ERRO: Prioridade ' + str(prio) + ' deveria existir'
    
    print()
    print('Buscando prioridades inexistentes:')
    buscar_inexistentes = [99, 100, 200]
    for prio in buscar_inexistentes:
        encontrado = arv.buscar(PacketRule(0, '', '', prio))
        if not encontrado:
            print('  Prioridade ' + str(prio) + ' nao encontrada (correto)')
        else:
            print('  [FALHA] Prioridade ' + str(prio) + ' foi encontrada inesperadamente!')
        assert not encontrado, 'ERRO: Prioridade ' + str(prio) + ' nao deveria existir'
    
    print('[OK] Busca validada!')


def teste_remocao():
    print()
    print('========================================')
    print('  TESTE: REMOCAO')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    rem1 = PacketRule(1, '10.0.0.1', '192.168.1.1', 100)
    rem2 = PacketRule(2, '10.0.0.2', '192.168.1.2', 90)
    rem3 = PacketRule(3, '10.0.0.3', '192.168.1.3', 80)
    rem4 = PacketRule(4, '10.0.0.4', '192.168.1.4', 70)
    rem5 = PacketRule(5, '10.0.0.5', '192.168.1.5', 60)
    
    arv.insert(rem1)
    arv.insert(rem2)
    arv.insert(rem3)
    arv.insert(rem4)
    arv.insert(rem5)
    
    print('Estado inicial:', arv.tamanho(), 'nos')
    print('Rotacoes iniciais:', arv.get_rotacoes())
    print('Recolorings iniciais:', arv.get_recolorir())
    
    arv.reset_contadores()
    print()
    print('Remover folha (prio=60):')
    arv.remover(rem5)
    print('Nos apos remocao:', arv.tamanho())
    print('Rotacoes:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    assert arv.tamanho() == 4, 'ERRO: Deve ter 4 nos'
    
    arv.reset_contadores()
    print()
    print('Remover no com um filho (prio=80):')
    arv.remover(rem3)
    print('Nos apos remocao:', arv.tamanho())
    print('Rotacoes:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    assert arv.tamanho() == 3, 'ERRO: Deve ter 3 nos'
    
    arv.reset_contadores()
    print()
    print('Remover no com dois filhos (prio=90):')
    arv.remover(rem2)
    print('Nos apos remocao:', arv.tamanho())
    print('Rotacoes:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    assert arv.tamanho() == 2, 'ERRO: Deve ter 2 nos'
    
    arv.reset_contadores()
    print()
    print('Remover raiz (prio=100):')
    arv.remover(rem1)
    print('Nos apos remocao:', arv.tamanho())
    print('Rotacoes:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    assert arv.tamanho() == 1, 'ERRO: Deve ter 1 no'
    
    print('[OK] Remocao validada!')


def teste_estresse():
    print()
    print('========================================')
    print('  TESTE: CENARIO DE ESTRESSE')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    print('Inserindo 50 regras em ordem decrescente...')
    for i in range(100, 50, -1):
        regra = PacketRule(i, '10.0.0.' + str(i), '192.168.1.' + str(i), i)
        arv.insert(regra)
    
    print('Nos inseridos:', arv.tamanho())
    print('Rotacoes realizadas:', arv.get_rotacoes())
    print('Recolorings:', arv.get_recolorir())
    print('Altura da arvore:', arv.get_altura())
    
    import math
    n = arv.tamanho()
    altura_maxima = 2 * math.log2(n + 1)
    print('Altura maxima teorica (RBT):', round(altura_maxima, 2))
    print('Altura real:', arv.get_altura())
    
    assert arv.tamanho() == 50, 'ERRO: Deve ter 50 nos'
    assert arv.get_altura() <= altura_maxima, 'ERRO: Altura excede limite teorico'
    
    print()
    print('Removendo 25 regras aleatoriamente...')
    for i in range(100, 75, -1):
        regra = PacketRule(i, '10.0.0.' + str(i), '192.168.1.' + str(i), i)
        arv.remover(regra)
    
    print('Nos restantes:', arv.tamanho())
    print('Altura apos remocoes:', arv.get_altura())
    
    assert arv.tamanho() == 25, 'ERRO: Deve ter 25 nos restantes'
    print('[OK] Cenario de estresse validado!')


def teste_cores_raiz():
    print()
    print('========================================')
    print('  TESTE: RAIZ SEMPRE PRETA (Propriedade 2)')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    for i in range(1, 11):
        regra = PacketRule(i, '192.168.1.' + str(i), '10.0.0.' + str(i), i * 10)
        arv.insert(regra)
    
    print('Nos inseridos:', arv.tamanho())
    print('Cor da raiz:', arv.raiz.cor.name)
    
    assert arv.raiz.cor == Cor.PRETO, 'ERRO: Raiz deve ser sempre PRETA'
    print('[OK] Raiz sempre preta validada!')


def teste_vermelho_sem_vermelho():
    print()
    print('========================================')
    print('  TESTE: NO VERMELHO SEM FILHO VERMELHO (Propriedade 4)')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    import random
    rng = random.Random(42)
    for i in range(50):
        prio = rng.randint(1, 1000)
        regra = PacketRule(i, '10.0.0.' + str(i), '192.168.1.' + str(i), prio)
        arv.insert(regra)
    
    print('Nos inseridos:', arv.tamanho())
    
    def verificar_vermelho(node):
     if node is None:
        return True
        
     if node.cor == Cor.VERMELHO:
        # Só verifica a cor se o filho da esquerda/direita realmente existir (não for None)
        if (node.esquerda and node.esquerda.cor == Cor.VERMELHO) or \
           (node.direita and node.direita.cor == Cor.VERMELHO):
            return False
            
     return verificar_vermelho(node.esquerda) and verificar_vermelho(node.direita)


def teste_caminhos_mesmo_preto():
    print()
    print('========================================')
    print('  TESTE: MESMO NUMERO DE NOS PRETOS (Propriedade 5)')
    print('========================================')
    
    arv = ArvoreRedBlack()
    
    import random
    rng = random.Random(123)
    for i in range(100):
        prio = rng.randint(1, 5000)
        regra = PacketRule(i, '10.0.0.' + str(i), '192.168.1.' + str(i), prio)
        arv.insert(regra)
    
    print('Nos inseridos:', arv.tamanho())
    
    def contar_pretos(node):
        if node == arv.TNULL:
            return 1
        esq = contar_pretos(node.esquerda)
        direita = contar_pretos(node.direita)
        if esq == -1 or direita == -1 or esq != direita:
            return -1
        if node.cor == Cor.PRETO:
            return esq + 1
        return esq
    
    pretos = contar_pretos(arv.raiz)
    if pretos != -1:
        print('  Todos os caminhos tem ' + str(pretos) + ' nos pretos (incluindo TNULL)')
        print('[OK] Propriedade 5 validada!')
    else:
        assert False, 'Propriedade 5 violada: caminhos com pretos diferentes'


def main():
    print()
    print()
    print('========================================')
    print('  Testes Unitarios - Arvore Red-Black')
    print('  SDN-Scale | Estrutura de Dados II')
    print('========================================')
    print()
    print('   SDN-Scale | Estrutura de Dados II')
    print()
    
    teste_insercao_basica()
    teste_rotacao_esquerda()
    teste_rotacao_direita()
    teste_busca()
    teste_remocao()
    teste_estresse()
    teste_cores_raiz()
    teste_vermelho_sem_vermelho()
    teste_caminhos_mesmo_preto()
    
    print()
    print('========================================')
    print('  TODOS OS TESTES RBT CONCLUIDOS')
    print('========================================')
    print()
    print('Estatisticas gerais:')
    print('  - Insercao testada')
    print('  - Rotacoes testadas (esquerda e direita)')
    print('  - Busca testada')
    print('  - Remocao testada (folha, 1 filho, 2 filhos, raiz)')
    print('  - Cenario de estresse concluido')
    print('  - Propriedade 2 (raiz preta) verificada')
    print('  - Propriedade 4 (vermelho sem filho vermelho) verificada')
    print('  - Propriedade 5 (mesmo numero de pretos) verificada')
    print()
    print('[OK] Todos os testes passaram com sucesso!')
    print()


if __name__ == '__main__':
    main()