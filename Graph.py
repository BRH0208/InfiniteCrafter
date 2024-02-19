from sklearn.preprocessing import LabelEncoder
import networkx as nx
import matplotlib.pyplot as plt
import pickle
hell = Exception

recipieDict = dict() # This is bad
#Load recipieDict
with open('recipieDict.pkl', 'rb') as f:
    recipieDict = pickle.load(f) 

#Load wordEncoder
with open('wordEncoder.pkl', 'rb') as f:
    wordEncoder = pickle.load(f) 

#Load wordEncoder
with open('ordertable.pkl', 'rb') as f:
    order = pickle.load(f) 

G = nx.Graph()
count = 0
for element in recipieDict:
    G.add_node(element,subset=order[element])
print("Adding recipies")
for element,recipiesList in recipieDict.items():
    recipies = filter(lambda recipie : not (recipie[0] == element or recipie[1] == element),recipiesList)    
    for recipie in recipies:
        for component in recipie:
            G.add_edge(element, component)
nx.set_node_attributes(G, 0, "subset")
for element in recipieDict:
    G.add_node(element,subset=order[element])
print("Making layout")
pos = nx.multipartite_layout (G)
print("Drawing")
nx.draw_networkx_edges(G, pos=pos, width=0.05)
print("Showing")
plt.show()
