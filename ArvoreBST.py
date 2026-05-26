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

class Node:
    def __init__(self, valor):
        self.valor = valor
        self.esquerda = None
        self.direita = None

class ArvoreBST:
    def __init__(self):
        self.raiz = None

    def insert(self, dado):
        novo = Node(dado)
        if self.raiz is None:
            self.raiz = novo
            return

        atual = self.raiz
        while True:
            if dado < atual.valor:
                if atual.esquerda is None:
                    atual.esquerda = novo
                    return
                else:
                    atual = atual.esquerda
            else:
                if atual.direita is None:
                    atual.direita = novo
                    return
                else:
                    atual = atual.direita

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
        pai = None
        atual = self.raiz

        while atual and atual.valor != valor:
            pai = atual
            if valor < atual.valor:
                atual = atual.esquerda
            else:
                atual = atual.direita

        if not atual:
            print("Elemento não encontrado")
            return False

        if atual.esquerda and atual.direita:
            pai_suc = atual
            suc = atual.direita
            while suc.esquerda:
                pai_suc = suc
                suc = suc.esquerda
            atual.valor = suc.valor
            pai = pai_suc
            atual = suc

        filho = atual.esquerda or atual.direita

        if pai is None:
            self.raiz = filho
        elif pai.esquerda == atual:
            pai.esquerda = filho
        else:
            pai.direita = filho

        return True

    def inorder(self):
        self._inorder_rec(self.raiz)

    def _inorder_rec(self, node):
        if node is not None:
            self._inorder_rec(node.esquerda)
            print(node.valor)
            self._inorder_rec(node.direita)