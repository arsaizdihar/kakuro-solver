import copy
import networkx as nx


class Graph(nx.Graph):
    possible_values: dict[tuple[int, int], tuple[int, list[list[int]]]] = {}
    iter_count = 0

    def __init__(self, height, width) -> None:
        super().__init__()
        self.width = width
        self.height = height

    def initialize_empty_nodes(self, positions: list[tuple[int, int]]):
        # Menambahkan kotak putih ke dalam graf, diinisiasi dengan value = 0
        for pos in positions:
            self.add_node(tuple(pos), value=0)

    def initialize_constraints(self, contraints):
        # Menambahkan batasan tiap entri ke dalam graf, yaitu berupa sisi yang menghubungkan antar kotak pada suatu entri
        for constraint in contraints:
            len_nodes = len(constraint[0])
            sum_val = constraint[1]
            possible_values = Graph.get_possible_values(len_nodes, sum_val)
            _row, _col = constraint[0][0]
            for i, (row, col) in enumerate(constraint[0]):
                if row != _row and col != _col:
                    raise Exception(
                        f"Invalid constraint {constraint}, must be in same row or col")
                node = self.nodes.get((row, col))
                if node is None:
                    raise Exception("Node is not empty")

                for j in range(i + 1, len(constraint[0])):
                    row2, col2 = constraint[0][j]
                    self.add_edge((row, col), (row2, col2),
                                  weight=copy.deepcopy(possible_values))

    def copy(self):
        return copy.deepcopy(self)

    @staticmethod
    def get_possible_values(length: int, sum_val: int, start=1):
        # Mengembalikan semua kemungkinan nilai yang dapat diisi pada entri dengan panjang length dan jumlah sum_val
        if start > 9:
            return []

        if length == 1:
            if sum_val < 1 or sum_val > 9 or sum_val < start:
                return []
            return [[sum_val]]

        # Menggunakan hasil kombinasi yang telah disimpan sebelumnya
        if (length, sum_val) in Graph.possible_values:
            pos_start, possible_values = Graph.possible_values[(
                length, sum_val)]
            if pos_start == start:
                return possible_values
            elif pos_start < start:
                filtered = filter(lambda x: min(x) >= start, possible_values)
                return list(filtered)

        possible_values = []
        rest_possible = Graph.get_possible_values(
            length - 1, sum_val - start, start + 1)
        for rest in rest_possible:
            possible_values.append([start] + rest)
        possible_values.extend(
            Graph.get_possible_values(length, sum_val, start + 1))

        # Menyimpan hasil kombinasi yang telah dihitung agar tidak perlu menghitung ulang kombinasi yang sama
        Graph.possible_values[(length, sum_val)] = (start, possible_values)
        return possible_values

    def get_node_possible_values(self, pos: tuple[int, int]):
        node = self.nodes.get(pos)
        if node is None:
            raise Exception("Node not found")
        res: set[int] = set()
        first = True
        rowDone = False
        colDone = False
        for _, neighbor, data in self.edges(pos, True):
            if neighbor[0] == pos[0]:
                if rowDone:
                    continue
                rowDone = True
            else:
                if colDone:
                    continue
                colDone = True
            weight = data.get("weight", [])
            values = set()
            for v in weight:
                values = values.union(v)
            res = res.intersection(values) if not first else values
            first = False
        return list(res)

    def print_board(self):
        print()
        for row in range(self.height):
            for col in range(self.width):
                node = self.nodes.get((row, col))
                if node is None:
                    print(" ", end="")
                else:
                    print(node["value"], end="")
                print(end=" ")
            print()
        print()

    def set_value(self, pos, value):
        # Mengisi nilai pada simpul tertentu dengan angka tertentu dan memperbarui sisi-sisi yang terdampak
        self.nodes[pos]["value"] = value
        to_remove = []
        processed = set()
        for _, neighbor, _ in self.edges(pos, True):
            if neighbor[0] == pos[0]:
                isSameRow = True
            else:
                isSameRow = False
            for _, neighbor2, data in self.edges(neighbor, True):
                # hanya memproses simpul yang berada pada entri yang sama dengan simpul A dan simpul B
                if (isSameRow and neighbor2[0] != pos[0]) or (not isSameRow and neighbor2[1] != pos[1]):
                    continue
                # hanya memproses sekali
                if (neighbor2, neighbor) in processed:
                    continue
                processed.add((neighbor, neighbor2))
                weight = data.get("weight", [])
                pos_to_remove = []
                for possible in weight:
                    # jika nilai yang dimasukkan terdapat pada kemungkinan, maka hapus nilai tersebut pada kemungkinan, sebaliknya hapus kemungkinan tersebut
                    if value in possible:
                        possible.remove(value)
                    else:
                        pos_to_remove.append(possible)
                for p in pos_to_remove:
                    weight.remove(p)

            to_remove.append(neighbor)
        for r in to_remove:
            edge = self.edges.get((r, pos))
            if edge is not None:
                weight = edge.get("weight", [])
                if len(weight) != 1 or len(weight[0]) != 1:
                    self.remove_edge(r, pos)

    def solve(self):
        return self.__solve_rec(list(self.nodes(True)))

    def __solve_rec(self, rest):
        if len(rest) == 0:
            return True

        first = rest[0]
        pos = first[0]
        possible_values = self.get_node_possible_values(pos)
        if len(possible_values) == 0:
            return False

        for value in possible_values:
            copy = self.copy()
            copy.set_value(pos, value)
            if copy.__solve_rec(rest[1:]):
                self.nodes = copy.nodes
                self.edges = copy.edges
                return True
        return False
