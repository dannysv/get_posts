import json

with open('post_threads_links.json') as f:
    data = json.load(f)

#print(len(data))

btot = []
baixados = []
baixados_set = set()
for i in range(100):
    with open('post_threads_links_pagination'+str(i)+'.json') as fi:
        dat = json.load(fi)
    #baixados=baixados+dat
    #baixados_set = baixados_set.union(set(dat))
    btot+=dat
    for line in dat:
        if('?page=' not in line):
            baixados.append(line)
            baixados_set.add(line)
        else:
            if('?page=0' in line):
                baixados.append(line.split('?page=')[0])
                baixados_set.add(line.split('?page=')[0])

print("lista con paginacion incluida tiene %s itens"%len(btot))
print("lista de baixados tiene %s itens"%len(baixados))
print("set de baixados tiene %s itens"%len(baixados_set))
print("lista de total tiene %s itens"%len(data))
set_data = set(data)
print("set de total tiene %s itens"%len(set_data))
print("set total de la diferencia data-baixados tiene %s itens"%len(set_data.difference(baixados_set)))

#with open('post_threads_links_last.json', 'w') as out:
#    json.dump(list(set_data.difference(baixados_set)),out)


