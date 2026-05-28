from enum import IntEnum

class Cor(IntEnum):
    PRETO = 0
    VERMELHO = 1

cor = Cor

class PacketRule:
    def __init__(self, rule_id, src_ip, dst_ip, priority):
        self.id = rule_id
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        if other is None:
            return False
        return self.priority == other.priority

    def __repr__(self):
        return f"Rule({self.id}, prio={self.priority})"

    def __gt__(self, other):
        return self.priority > other.priority


class RBNode:
    def __init__(self, valor):
        self.valor = valor
        self.esquerda = None
        self.direita = None
        self.parent = None
        self.cor = Cor.VERMELHO

class TNullSentinel:
    def __init__(self):
        self.cor = Cor.PRETO
    def __eq__(self, other):
        return other is None or isinstance(other, TNullSentinel)
    def __repr__(self):
        return "TNULL"


class ArvoreRB:
    def __init__(self):
        self.raiz = None
        self.TNULL = TNullSentinel()
        self.rotacoes = 0
        self.recolorir = 0

    def tamanho(self):
        def _contar(node):
            if node is None or node == getattr(self, 'TNULL', None):
                return 0
            return 1 + _contar(node.esquerda) + _contar(node.direita)
        return _contar(self.raiz)

    def get_recolorir(self):
        """Retorna o total de recolorings (pode retornar o atributo interno correspondente)"""
        return getattr(self, 'recolorings', 0)
    def get_altura(self):
        def _height(node):
            if node is None:
                return 0
            return 1 + max(_height(node.esquerda), _height(node.direita))
        return _height(self.raiz)

    def get_rotacoes(self):
        return self.rotacoes

    def get_recolorir(self):
        return self.recolorir

    def reset_contadores(self):
        self.rotacoes = 0
        self.recolorir = 0
        
    def reset_contadores_gerais(self): 
        self.reset_contadores()

    def _rotacao_esquerda(self, x):
        self.rotacoes += 1
        y = x.direita
        x.direita = y.esquerda
        if y.esquerda:
            y.esquerda.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.raiz = y
        elif x == x.parent.esquerda:
            x.parent.esquerda = y
        else:
            x.parent.direita = y
        y.esquerda = x
        x.parent = y

    def _rotacao_direita(self, x):
        self.rotacoes += 1
        y = x.esquerda
        x.esquerda = y.direita
        if y.direita:
            y.direita.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.raiz = y
        elif x == x.parent.direita:
            x.parent.direita = y
        else:
            x.parent.esquerda = y
        y.direita = x
        x.parent = y

    def insert(self, valor):
        novo = RBNode(valor)
        self.raiz = self._insert_bst(self.raiz, novo)
        self._consertar_insercao(novo)

    def _insert_bst(self, node, novo):
        if node is None:
            return novo

        if novo.valor < node.valor:
            node.esquerda = self._insert_bst(node.esquerda, novo)
            node.esquerda.parent = node
        elif novo.valor > node.valor:
            node.direita = self._insert_bst(node.direita, novo)
            node.direita.parent = node

        return node

    def _consertar_insercao(self, k):
        while k.parent and k.parent.cor == Cor.VERMELHO:
            if k.parent == k.parent.parent.direita:
                tio = k.parent.parent.esquerda
                if tio and tio.cor == Cor.VERMELHO:
                    tio.cor = Cor.PRETO
                    k.parent.cor = Cor.PRETO
                    k.parent.parent.cor = Cor.VERMELHO
                    self.recolorir += 3
                    k = k.parent.parent
                else:
                    if k == k.parent.esquerda:
                        k = k.parent
                        self._rotacao_direita(k)
                    k.parent.cor = Cor.PRETO
                    k.parent.parent.cor = Cor.VERMELHO
                    self.recolorir += 2
                    self._rotacao_esquerda(k.parent.parent)
            else:
                tio = k.parent.parent.direita
                if tio and tio.cor == Cor.VERMELHO:
                    tio.cor = Cor.PRETO
                    k.parent.cor = Cor.PRETO
                    k.parent.parent.cor = Cor.VERMELHO
                    self.recolorir += 3
                    k = k.parent.parent
                else:
                    if k == k.parent.direita:
                        k = k.parent
                        self._rotacao_esquerda(k)
                    k.parent.cor = Cor.PRETO
                    k.parent.parent.cor = Cor.VERMELHO
                    self.recolorir += 2
                    self._rotacao_direita(k.parent.parent)
            if k == self.raiz:
                break
        if self.raiz.cor != Cor.PRETO:
            self.raiz.cor = Cor.PRETO
            self.recolorir += 1

    def buscar(self, valor):
        atual = self.raiz
        while atual:
            if valor == atual.valor:
                return True
            elif valor < atual.valor:
                atual = atual.esquerda
            else:
                atual = atual.direita
        return False

    def remover(self, valor):
        node = self._buscar_no(self.raiz, valor)
        if node is None:
            return False
        self._remover_no(node)
        return True

    def _buscar_no(self, node, valor):
        while node:
            if valor == node.valor:
                return node
            elif valor < node.valor:
                node = node.esquerda
            else:
                node = node.direita
        return None

    def _remover_no(self, z):
        y = z
        y_cor_original = y.cor
        if z.esquerda is None:
            x = z.direita         
            x_parent = z.parent    
            self._transplantar(z, z.direita)
        elif z.direita is None:
            x = z.esquerda
            x_parent = z.parent
            self._transplantar(z, z.esquerda)
        else:
            y = self._menor_no(z.direita)
            y_cor_original = y.cor
            x = y.direita
            if y.parent == z:
                x_parent = y
                if x:
                    x.parent = y
            else:
                x_parent = y.parent
                self._transplantar(y, y.direita)
                y.direita = z.direita
                y.direita.parent = y
            self._transplantar(z, y)
            y.esquerda = z.esquerda
            y.esquerda.parent = y
            y.cor = z.cor
            self.recolorir += 1

        if y_cor_original == Cor.PRETO:
            self._consertar_remocao(x, x_parent)

    def _transplantar(self, u, v):
        if u.parent is None:
            self.raiz = v
        elif u == u.parent.esquerda:
            u.parent.esquerda = v
        else:
            u.parent.direita = v
        if v:
            v.parent = u.parent

    def _menor_no(self, node):
        while node.esquerda:
            node = node.esquerda
        return node

    def _consertar_remocao(self, x, x_parent):
        while x != self.raiz and (x is None or x.cor == Cor.PRETO):
            parent = x.parent if x is not None else x_parent
            if x == parent.esquerda:
                irmao = parent.direita
                if irmao and irmao.cor == Cor.VERMELHO:
                    irmao.cor = Cor.PRETO
                    parent.cor = Cor.VERMELHO
                    self.recolorir += 2
                    self._rotacao_esquerda(parent)
                    irmao = parent.direita

                if irmao is None:
                    x = parent
                    x_parent = x.parent if x else None
                elif (irmao.esquerda is None or irmao.esquerda.cor == Cor.PRETO) and \
                     (irmao.direita is None or irmao.direita.cor == Cor.PRETO):
                    irmao.cor = Cor.VERMELHO
                    self.recolorir += 1
                    x = parent
                    x_parent = x.parent if x else None
                else:
                    if irmao.direita is None or irmao.direita.cor == Cor.PRETO:
                        if irmao.esquerda:
                            irmao.esquerda.cor = Cor.PRETO
                            self.recolorir += 1
                        irmao.cor = Cor.VERMELHO
                        self.recolorir += 1
                        self._rotacao_direita(irmao)
                        irmao = parent.direita

                    if irmao:
                        irmao.cor = parent.cor
                        self.recolorir += 1
                    parent.cor = Cor.PRETO
                    self.recolorir += 1
                    if irmao and irmao.direita:
                        irmao.direita.cor = Cor.PRETO
                        self.recolorir += 1
                    self._rotacao_esquerda(parent)
                    x = self.raiz
                    x_parent = None
            else:
                irmao = parent.esquerda
                if irmao and irmao.cor == Cor.VERMELHO:
                    irmao.cor = Cor.PRETO
                    parent.cor = Cor.VERMELHO
                    self.recolorir += 2
                    self._rotacao_direita(parent)
                    irmao = parent.esquerda

                if irmao is None:
                    x = parent
                    x_parent = x.parent if x else None
                elif (irmao.direita is None or irmao.direita.cor == Cor.PRETO) and \
                     (irmao.esquerda is None or irmao.esquerda.cor == Cor.PRETO):
                    irmao.cor = Cor.VERMELHO
                    self.recolorir += 1
                    x = parent
                    x_parent = x.parent if x else None
                else:
                    if irmao.esquerda is None or irmao.esquerda.cor == Cor.PRETO:
                        if irmao.direita:
                            irmao.direita.cor = Cor.PRETO
                            self.recolorir += 1
                        irmao.cor = Cor.VERMELHO
                        self.recolorir += 1
                        self._rotacao_esquerda(irmao)
                        irmao = parent.esquerda

                    if irmao:
                        irmao.cor = parent.cor
                        self.recolorir += 1
                    parent.cor = Cor.PRETO
                    self.recolorir += 1
                    if irmao and irmao.esquerda:
                        irmao.esquerda.cor = Cor.PRETO
                        self.recolorir += 1
                    self._rotacao_direita(parent)
                    x = self.raiz
                    x_parent = None
        if x:
            x.cor = Cor.PRETO
            self.recolorir += 1

    def inorder(self):
        self._inorder_rec(self.raiz)

    def _inorder_rec(self, node):
        if node:
            self._inorder_rec(node.esquerda)
            print(node.valor)
            self._inorder_rec(node.direita)

RB = ArvoreRB
