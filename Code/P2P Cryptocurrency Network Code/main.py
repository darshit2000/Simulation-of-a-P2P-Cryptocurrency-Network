import random
import numpy
import sys
import genrate_graph
from transaction_object import transaction
import global_data as gd
from Node import node
from event import Event
from Block import block 
import time

import networkx as nx
import matplotlib.pyplot as plt
class GraphVisualization:
   
    def __init__(self):
          
        self.visual = []
          
    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)
          
    def visualize(self,dict,string1):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        nx.draw_networkx(G,with_labels=True,labels=dict)
        plt.savefig(string1)
        plt.show()


n = int(sys.argv[1]) # number of nodes in a network
gd.n=n
ttx = int(sys.argv[2]) # mean time for interarrival between transactions for a node
z = int(sys.argv[3]) # percentage of slow nodes
z=int((n*z)/100)
low_cpu = int(sys.argv[4]) # percentage of low cpu
tk=time.time()+30   # after this much time simulation process will stop
low_cpu=int((n*low_cpu)/100)
li_n=[]
l_cpu=[]
for i in range(n):
    li_n.append(i)
for i in range(n):
    l_cpu.append(i)
gd.slow_node=random.sample(li_n,z)   # randomly selecting z nodes for slow node  gd.slow_node store nodes index which are slow
gd.low_cpu=random.sample(l_cpu,low_cpu) #randomly selecting nodes for slow cpu gd.low_cpu stores nodes which has low cpu
gd.slow_rate=1/(10*n-9*low_cpu)   # gd.slow_rate is fraction hk ie hashing power for low cpu
#print(gd.slow_node)
ttx=ttx
adjacency=[]  # adjacency matrix store  network of nodes graph
adjacency=genrate_graph.generate_graph(n)  # generate graph method creates graph of n nodes which connected and each node has degree between 4 and 8
Node_list=[]  # this list stores the Node objects
init_coins_list=[]  # this is intial coin list where ith entry is the number of conins the node have intailly
for i in range(n):
    init_coins_list.append(random.randint(1,20))
for i in range(n):     # appending empty lists into various lists of node object
    gd.block_id_list.append([])
    gd.block_list.append([])
    gd.transaction_list.append([])
    gd.transaction_id_list.append([])
    temp=[] #temproary list for storeing neighbours of node i
    for j in range(n):
        if adjacency[i][j]==1:
            temp.append(j)
    Node_list.append(node(i,ttx,temp,init_coins_list))  # creating node object and storing in Node_list where i is the node id
print("nodes created")    # ttx is average mean time for transaction generation 
k=1   
txid=1
init_transaction_list=[]  
#creating the intial transaction_list each node is creating or generating  transaction 
for i in range(n):           
    li=[]
    rec=random.randint(0,n-1)
    gd.transaction_id=gd.transaction_id+1

    li=Node_list[i].transaction_generate(gd.time,'intial',10,gd.transaction_id,n)  #calling transaction generate function which will start creating events of generating transaction
    for j in li:
        gd.event_queue_list.append(j)  # gd.vevent_queue is global queue which store all pending events
# code for generating block by each node manually not by making an event of block generating
#print(len(gd.event_queue_list))
for i in range(n):
    li=[]
    gd.blockId=gd.blockId+1  #blockId will be store the last created block id 
    gd.time=gd.time+1
    #print(gd.blockId)
    j=0
    tran_list=[]
    #choosing pending transaction from pending transaction list
    while j<10 and len(Node_list[i].pending_transaction_list)>0:
        tran_list.append(Node_list[i].pending_transaction_list.pop(0))
        j=j+1
       
    bx=block(gd.blockId,i,tran_list,0,init_coins_list,gd.time)  #  block formation meaning forming block object  and this block has parent 0 that is genesis block
    gd.block_id_list[i].append(gd.blockId)  # storing this block into the block_list of node i which store blocks it received or created
    gd.block_list[i].append(bx)
    Node_list[i].created_block_list_id.append(gd.blockId)  #created_block_list_id store the id of block which stores t
    
    lis=[bx,2,Node_list[i].Block_tree_dict[0][2],gd.time]
    Node_list[i].Block_tree_dict.update({gd.blockId:lis}) #updating blockchain tree at node i 
    # broadcasting this block to neighbours of node i
    for j in Node_list[i].adja:
        pij=random.uniform(0.01,0.5)
        Cij=100
        if  i in gd.slow_node or j in gd.slow_node:
            Cij=5
        x=x=numpy.random.exponential(0.096/Cij,1)
        dij=x[0]
        p=sys.getsizeof(bx)/dij
        Lij=pij+p+dij
        ti=gd.time+Lij
        ev=Event(i,j,'BLK_REC',ti,bx,0)  # this event is for reciveing block by node j
        li.append(ev)
    for j in li:
        gd.event_queue_list.append(j)

while(len(gd.event_queue_list)>0):
    gd.event_queue_list=sorted(gd.event_queue_list,key=lambda x: x.time)  # sorting event_queue before poping of event
    if time.time()>tk:
        break 
    ev=gd.event_queue_list.pop(0)
    if ev.type=='TXN_REC':  # this event is for receiving transaction
        #print("i am in TXN_REC")
        ev_list=Node_list[ev.receiver].receive_transaction(ev.receiver,ev.sender,ev.time,n,ev.message)
        for i in ev_list:
            gd.event_queue_list.append(i)
    #print(len(gd.event_queue_list))
    if ev.type=='TXN_GEN':   # this is event is for generating new transaction 
        #print("i am in TXN_GEN")
        coins=random.randint(1,10)
        txid1=txid
        txid=txid+1
        ev_list= Node_list[ev.receiver].transaction_generate(ev.time,ev.type,coins,txid1,n)       
        for i in ev_list:
            gd.event_queue_list.append(i)
    if ev.type=='BLK_REC':  # this event is for receiveing block
        #print("Now i am running event of block recieving the block id ",ev.message.bkid," on the node ", ev.receiver)
        #time.sleep(10)
        if ev.message.bkid not in gd.block_id_list[ev.receiver]:
            ev_list= Node_list[ev.receiver].receive_block(ev.sender,ev.receiver,ev.time,n,ev.message)
            for i in ev_list:
                gd.event_queue_list.append(i)
     
    if ev.type=='BLK_GEN':  # this event is for mining and for generating blocksS
        #print("i am in  blk genration event of node ",ev.receiver," for the block ",ev.message.bkid)

        ev_list=Node_list[ev.receiver].Block_generation(ev.message,ev.parent_id,ev.time)  
        for i in ev_list:
            gd.event_queue_list.append(i)
#code for adding blocks from pending list:
for i in range(n):
    flag=0
    while(1):
        for j in Node_list[i].pending_block_list:
            if j.parent_bkid in Node_list[i].Block_tree_dict.keys():
                flag=1
                temp_li=[]
                temp_li.append(j)
                temp_li.append(1+Node_list[i].Block_tree_dict[j.parent_bkid][1])
                temp_li.append(Node_list[i].Block_tree_dict[j.parent_bkid][2])
                tk=Node_list[i].Block_tree_dict[j.parent_bkid][3]+1
                temp_li.append(tk)
                Node_list[i].Block_tree_dict.update({j:temp_li})
                Node_list[i].pending_block_list.remove(j)
                flag=1
        if flag==0:
            break
        else:
            flag=0
            continue    


print("max height  #blocks_received  #pending_list")
for i in range(n):
    ma=0
    for j in Node_list[i].Block_tree_dict.keys():
        if ma< Node_list[i].Block_tree_dict[j][1]:
            ma=Node_list[i].Block_tree_dict[j][1]
    print(ma,len(gd.block_id_list[i]),len(Node_list[i].pending_block_list))
# 
print("number of block created or generated")
for i in range(n):
    print(len(Node_list[i].created_block_list_id))
print("length of the leafs from root")
for i in range(n):
    temp_list=[]
    for j in Node_list[i].Block_tree_dict.keys():
        flag=0
        for k in Node_list[i].Block_tree_dict.keys():
            if Node_list[i].Block_tree_dict[k][0].parent_bkid==j:
                flag=1
                break
        if flag==0:
            temp_list.append(Node_list[i].Block_tree_dict[j][1])
    print(temp_list)   

print("number of blocks in dictinary in given node")      
for i in range(n):
    print(len(Node_list[i].Block_tree_dict))
print("number of blocks which has zero parent node")
for i in range(n):
    count=0
    for j in Node_list[i].Block_tree_dict.keys():
        if Node_list[i].Block_tree_dict[j][0].parent_bkid==0:
            count=count+1
    print(count)          
print("all finished")
print(gd.blockId)
print("slow nodes list")
print(gd.slow_node)
print("slow cpu nodes list")
print(gd.low_cpu)

# below code is for visiluzation and printing results in files
for i in range(n):
    #dict1={}
    file_name="block_tree_details_file"+str(i)+".txt"  #file name creation
    f = open(file_name, "a") # creating file 
    f.truncate(0)
    for j in  Node_list[i].Block_tree_dict.keys():  # storing all blocks in a file from blockchain of node i
        f.write(f"Node id={ Node_list[i].Block_tree_dict[j][0].bkid} , arrival_time={int(Node_list[i].Block_tree_dict[j][3])}  \n")
    f.close()
    l=len(Node_list[i].Block_tree_dict)
    #below code is visualize for block chain of node i
    labeldict = {}
    for k in Node_list[i].Block_tree_dict.keys():

        if(k==0):
            labeldict[k] = 'G'
        else:
            labeldict[k] = (k,int(Node_list[i].Block_tree_dict[k][3]))

    G = GraphVisualization()
    for j in Node_list[i].Block_tree_dict.keys():
        if j!=0:
            G.addEdge(Node_list[i].Block_tree_dict[j][0].parent_bkid,j)
    string1="Blockchain_node_"+str(i)+".png"
    G.visualize(labeldict,string1)
 
    #below code is for visualize longest chain in blockchain of node i

    ma=0
    node_id=0
    for j in Node_list[i].Block_tree_dict.keys():
        if ma<Node_list[i].Block_tree_dict[j][1]:
            ma=Node_list[i].Block_tree_dict[j][1]
            node_id=j
    max_chain=[]
    max_chain.append(node_id)
    k=node_id
    while(k!=0):
        max_chain.append(Node_list[i].Block_tree_dict[k][0].parent_bkid)
        k=Node_list[i].Block_tree_dict[k][0].parent_bkid

    labeldict1 = {}
    for k in max_chain:

        if(k==0):
            labeldict1[k] = 'G'
        else:
            labeldict1[k] = (k,int(Node_list[i].Block_tree_dict[k][3]))

    G1 = GraphVisualization()
    for j in max_chain:
        if j!=0:
            G1.addEdge(Node_list[i].Block_tree_dict[j][0].parent_bkid,j)
    string1="longest_chain_node_"+str(i)+".png"
    G1.visualize(labeldict1,string1)   
    print("extra info for node ", i) 
    count1=0
    for j in max_chain:
        if j in Node_list[i].created_block_list_id:
            count1=count1+1
    rat=count1/len(Node_list[i].created_block_list_id)    
    print(" number of block of its own in chain= ",count1," number of total created = ",len(Node_list[i].created_block_list_id)," ratio is = ",rat)     





 















