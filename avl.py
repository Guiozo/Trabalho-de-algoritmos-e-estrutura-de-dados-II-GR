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


class AVLNode:
    def __init__(self, valor):
        self.valor = valor
        self.esquerda = None
        self.direita = None
        self.altura = 1


class ArvoreAVL:
    def __init__(self):
        self.raiz = None

    def _altura(self, node):
        if node is None:
            return 0
        return node.altura

    def _fator_balanceamento(self, node):
        if node is None:
            return 0
        return self._altura(node.esquerda) - self._altura(node.direita)

    def _atualizar_altura(self, node):
        if node:
            node.altura = 1 + max(self._altura(node.esquerda), self._altura(node.direita))

    def _rotacao_direita(self, y):
        x = y.esquerda
        T2 = x.direita

        x.direita = y
        y.esquerda = T2

        self._atualizar_altura(y)
        self._atualizar_altura(x)

        return x

    def _rotacao_esquerda(self, x):
        y = x.direita
        T2 = y.esquerda

        y.esquerda = x
        x.direita = T2

        self._atualizar_altura(x)
        self._atualizar_altura(y)

        return y

    def insert(self, valor):
        self.raiz = self._insert_rec(self.raiz, valor)

    def _insert_rec(self, node, valor):
        if node is None:
            return AVLNode(valor)

        if valor < node.valor:
            node.esquerda = self._insert_rec(node.esquerda, valor)
        elif valor > node.valor:
            node.direita = self._insert_rec(node.direita, valor)
        else:
            return node

        self._atualizar_altura(node)

        fb = self._fator_balanceamento(node)

        if fb > 1 and valor < node.esquerda.valor:
            return self._rotacao_direita(node)

        if fb < -1 and valor > node.direita.valor:
            return self._rotacao_esquerda(node)

        if fb > 1 and valor > node.esquerda.valor:
            node.esquerda = self._rotacao_esquerda(node.esquerda)
            return self._rotacao_direita(node)

        if fb < -1 and valor < node.direita.valor:
            node.direita = self._rotacao_direita(node.direita)
            return self._rotacao_esquerda(node)

        return node
