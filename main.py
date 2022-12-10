from graph import Graph
import json

# nama file json konfigurasi game
filename = "./games/9x8/game1.json"

f = open(filename)
data = json.load(f)
f.close()
size = data["size"]
nodes = data["nodes"]
constraints = data["constraints"]
graph = Graph(size[0], size[1])

graph.initialize_empty_nodes(nodes)
graph.initialize_constraints(constraints)
graph.print_board()
graph.solve()
graph.print_board()
