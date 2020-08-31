#this file is to cluster people and update their clusters in db

import igraph as ig
import pymongo

#connecting to dB
client=pymongo.MongoClient()
db=client.twitter

#getting users
users=[]
for user in db.users.find({}):
    users.append(user)

#making empty graph
g=ig.Graph(directed=True)

#making vertices
for user in users:
    g.add_vertex(name=user['user']['screen_name'],size=user['activity'],mongo_id=user['_id'])

#making edges
for user in users:
    for edge in user['edges']:
        if edge['bond']!=0:
            g.add_edge(user['user']['screen_name'],edge['screen_name'],weight=edge['bond'])

#clustering people
cluster=g.community_infomap(edge_weights=g.es['weight'],vertex_weights=g.vs['size'],trials=1000)

#dividing them into clusters
cluster_list=[]
for graph in cluster.subgraphs():
    
    members=[]
    for vertex in graph.vs:
        members.append((vertex['name'],vertex['mongo_id']))
    
    cluster_list.append(members)

#now updating in dB
for cluster_number in range(len(cluster_list)):
    for member in cluster_list[cluster_number]:
        db.users.update_one({'_id':member[1]},{'$set':{'cluster_number':cluster_number}})
        
print(cluster.summary())

#printing to a file
cluster_path='E:/twitter_data/discover_weekly_data&report/clusters.txt'
with open(cluster_path,'w') as f:
    #writing summary
    f.write(cluster.summary())
    f.write('\n')
    f.write('\n')
    
    #writing lists
    for cluster_number in range(len(cluster_list)):
        #writing cluster_number
        f.write(f"The Cluster number : {cluster_number} as size is {len(cluster_list[cluster_number])}\n")
        f.write('\n')
        for member in cluster_list[cluster_number]:
            f.write(member[0])
            f.write('\n')
        f.write('\n')