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
        self.cor = 1


class ArvoreRB:
    def __init__(self):
        self.raiz = None

    def _rotacao_esquerda(self, x):
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
        while k.parent and k.parent.cor == 1:
            if k.parent == k.parent.parent.direita:
                tio = k.parent.parent.esquerda
                if tio and tio.cor == 1:
                    tio.cor = 0
                    k.parent.cor = 0
                    k.parent.parent.cor = 1
                    k = k.parent.parent
                else:
                    if k == k.parent.esquerda:
                        k = k.parent
                        self._rotacao_direita(k)
                    k.parent.cor = 0
                    k.parent.parent.cor = 1
                    self._rotacao_esquerda(k.parent.parent)
            else:
                tio = k.parent.parent.direita
                if tio and tio.cor == 1:
                    tio.cor = 0
                    k.parent.cor = 0
                    k.parent.parent.cor = 1
                    k = k.parent.parent
                else:
                    if k == k.parent.direita:
                        k = k.parent
                        self._rotacao_esquerda(k)
                    k.parent.cor = 0
                    k.parent.parent.cor = 1
                    self._rotacao_direita(k.parent.parent)
            if k == self.raiz:
                break
        self.raiz.cor = 0

    def buscar(self, valor):
        atual = self.raiz
        while atual:
            if valor == atual.valor:
                print("Valor encontrado", valor)
                return True
            elif valor < atual.valor:
                atual = atual.esquerda
            else:
                atual = atual.direita
        print("Valor não encontrado", valor)
        return False

    def remover(self, valor):
        node = self._buscar_no(self.raiz, valor)
        if node is None:
            print("Elemento não encontrado")
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
            self._transplantar(z, z.direita)
        elif z.direita is None:
            x = z.esquerda
            self._transplantar(z, z.esquerda)
        else:
            y = self._menor_no(z.direita)
            y_cor_original = y.cor
            x = y.direita
            if y.parent == z:
                if x:
                    x.parent = y
            else:
                self._transplantar(y, y.direita)
                y.direita = z.direita
                y.direita.parent = y
            self._transplantar(z, y)
            y.esquerda = z.esquerda
            y.esquerda.parent = y
            y.cor = z.cor

        if y_cor_original == 0:
            self._consertar_remocao(x)

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

    def _consertar_remocao(self, x):
        while x != self.raiz and (x is None or x.cor == 0):
            if x == x.parent.esquerda:
                irmao = x.parent.direita
                if irmao and irmao.cor == 1:
                    irmao.cor = 0
                    x.parent.cor = 1
                    self._rotacao_esquerda(x.parent)
                    irmao = x.parent.direita

                if irmao is None:
                    x = x.parent
                elif (irmao.esquerda is None or irmao.esquerda.cor == 0) and \
                     (irmao.direita is None or irmao.direita.cor == 0):
                    irmao.cor = 1
                    x = x.parent
                else:
                    if irmao.direita is None or irmao.direita.cor == 0:
                        if irmao.esquerda:
                            irmao.esquerda.cor = 0
                        irmao.cor = 1
                        self._rotacao_direita(irmao)
                        irmao = x.parent.direita

                    if irmao:
                        irmao.cor = x.parent.cor
                    x.parent.cor = 0
                    if irmao and irmao.direita:
                        irmao.direita.cor = 0
                    self._rotacao_esquerda(x.parent)
                    x = self.raiz
            else:
                irmao = x.parent.esquerda
                if irmao and irmao.cor == 1:
                    irmao.cor = 0
                    x.parent.cor = 1
                    self._rotacao_direita(x.parent)
                    irmao = x.parent.esquerda

                if irmao is None:
                    x = x.parent
                elif (irmao.direita is None or irmao.direita.cor == 0) and \
                     (irmao.esquerda is None or irmao.esquerda.cor == 0):
                    irmao.cor = 1
                    x = x.parent
                else:
                    if irmao.esquerda is None or irmao.esquerda.cor == 0:
                        if irmao.direita:
                            irmao.direita.cor = 0
                        irmao.cor = 1
                        self._rotacao_esquerda(irmao)
                        irmao = x.parent.esquerda

                    if irmao:
                        irmao.cor = x.parent.cor
                    x.parent.cor = 0
                    if irmao and irmao.esquerda:
                        irmao.esquerda.cor = 0
                    self._rotacao_direita(x.parent)
                    x = self.raiz
        if x:
            x.cor = 0

    def inorder(self):
        self._inorder_rec(self.raiz)

    def _inorder_rec(self, node):
        if node:
            self._inorder_rec(node.esquerda)
            print(node.valor)
            self._inorder_rec(node.direita)
