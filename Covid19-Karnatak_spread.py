#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import urllib.request, json
from bs4 import BeautifulSoup
from anytree import Node, RenderTree, search
from fpdf import FPDF
import matplotlib.pyplot as plt
import re
import matplotlib as mpl
import networkx as nx

def read_from_mirror():
    URL ='https://bangaloremirror.indiatimes.com/bangalore/others/karnataka-covid-19-tracker/articleshow/74892676.cms'
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, "html.parser")
    tags = soup.find_all('div',{'class': 'Normal'})
#    gulf = ['Dubai','Saudi','Mecca']
#    delhi = ['Delhi', 'Jamaat','Manipur','Colombo','Trivandrum']
#    eu = ['Edinburgh','UK',"Switzerland","Greece","Germany","Netherland","London","Spain",'Scotland','France','Paris','Madrid','Amsterdam','Athens']
#    usa = ['USA','Brazil','Guyana', 'New']
    #bengaluru = Node("Bangalore",parent=Local,desc="Resident Of bangalore")
    return tags


# In[ ]:


def get_parent(line):
    val = ''
    patt = re.compile(r'con\w+ of P(( |-)?\d+)')
    mat = patt.search(line)
    if (mat != None):
        val = re.findall('\d+',mat.group(1))[0]
    return val

def get_age_and_place(line):
    resident_of = 'na'
    age = 'na'
    gender = 'na'
    gendp = re.compile(r'male|femal|girl|boy')
    agep = re.compile(r'(\d+)(-| )(year|-year)|month')
    placep = re.compile(r'(from|resident of) (\w+)')
    mat = gendp.search(line)
    if (mat != None):
        gender = mat.group()
    #gender = mat.group()
    mat = agep.search(line)
    if mat != None:
        age = mat.group(1)
    mat = placep.search(line)
    if (mat != None):
        resident_of = mat.group(2)
        
    if (resident_of in ['Bengaluru','Bangalore','Hosakote','Benglauru','Hoskote']):
        resident_of =  'Bangalore'
    if (resident_of in ['Nanjangudu','Mysore','Nanjangud','Nanjungud','Mysuru','Nanjanagudu']):
        resident_of = 'Mysore'
    if (resident_of in ['Kalburgi','Kalaburagi', 'Kalaburgi', 'Kalburagi']):
        resident_of = 'Kalburgi'
    if (resident_of in ['Mandya', 'Malavalli']):
        resident_of = 'Mandya'
    if (resident_of in ['Kasargod','Kochi','Kannur','Kerala']):
        resident_of = 'Kerala'
    if (resident_of in ['Gadag','Mudhol','Hubballi','Dharwad']):
        resident_of = 'Hubballi'
    if (resident_of in ['Batkal','Bhatkal','Bhatkal']):
        resdient_of = 'Bhatkal'
    if (resident_of in ['Bagalkot','Bagalkote']):
        resident_of = 'Bagalkote'
    if (resident_of in ['Ballari', 'Hospet']):
        resident_of = 'Ballari'
    return (age,gender,resident_of)


def get_patient(line):
    patient = ''
    pat = re.compile(r'Pat\w+ number (\d+)' )
    mat = pat.search(line)
    if (mat == None):
        pat =re.compile(r'(\d+) is a')
        mat = pat.search(line)
    if mat != None:
        patient = re.findall('\d+',mat.group(1))[0]
    return patient



def get_travel(line):
    gulf = ['Dubai','Saudi','Mecca']
    delhi = ['Delhi', 'Jamaat','Manipur','Colombo','Trivandrum']
    eu = ['Edinburgh','UK',"Switzerland","Greece","Germany","Netherland","London","Spain",'Scotland','France','Paris','Madrid','Amsterdam','Athens']
    usa = ['USA','Brazil','Guyana', 'New']
    #bengaluru = Node("Bangalore",parent=Local,desc="Resident Of bangalore")


    travel = 'Local'
    pat = re.compile(r'travel history to (the )?(\w+)')
    mat = pat.search(line)
    if (mat == None):
        mat = re.compile(r'returned (to India )?from (\w+)').search(line)
    if (mat == None):
        mat = re.compile(r'(the )?(phar\w+)').search(line)
    if (mat != None):
        travel = mat.group(2)
    
    if (travel in gulf):
        travel = "Gulf"
    elif (travel in eu):
        travel = 'Europe'
    elif (travel in usa):
        travel = "America"
    elif (travel in delhi):
        travel = 'Delhi'
    elif (travel in ['pharma','pharmaceutical']):
        travel = 'Pharma'
    else:
        travel = 'Local'
        
#    print(travel, line)
    return travel


# In[ ]:


def get_count_from_travel(rnode, travel,disp=False):
    (primary_carrier,total_impact,spread_count) = (0,0,0)
    for pre, fill, node in RenderTree(rnode):
        if (node.depth < 4):
            primary_carrier += 1
        if (node.depth >= 4):
            spread_count += 1
        total_impact += 1
        if(disp):
            print("%s%s %s-%s-%s %s" % (pre, node.name,node.age,node.gender,node.loc,node.travel))    
    return (total_impact, primary_carrier, spread_count)


# In[ ]:


def print_node(loc='',travel=''):
    rnode = root
    rdepth = 3
    sdepth = 2
    (uknown_total, uknown_primary, uknown_spread) = (0,0,0)
    (travel_total, travel_primar, travel_spread, primary_carriers, primary_travel) = (0,0,0,0,0)
    total_cases = 0
    total_spread = 0
    
    if loc != '':
        rnode = search.find(root, lambda node: node.name == loc)
    if (rnode != root):
            rdepth = 3
            sdepth = 2
    for pre, fill, node in RenderTree(rnode):
        if (str.isdigit(node.name)):
            total_cases += 1
        
        if (node.depth == rdepth):
            primary_carriers += 1
        
        if (node.name == 'Local'):
                (t, p, s) = get_count_from_travel(node, 'Local')
                uknown_total += t
                uknown_primary += p
                uknown_spread += s
        if( node.name == travel ):
            (t,p,s) = get_count_from_travel(node, travel, True)
            travel_total += t
            travel_primar += p
            travel_spread += s
            if (node.depth == sdepth):
                primary_travel += 1
                    #print("%s%s %s-%s-%s %s" % (pre, node.name,node.age,node.gender,node.loc,node.travel))
        if node.depth > sdepth+1:
            total_spread += 1
        if ( travel == ''):
            print("%s%s %s-%s-%s %s" % (pre, node.name,node.age,node.gender,node.loc,node.travel))
    
    
    print("Total Cases in %s: \t\t\t\t %s" %(loc,total_cases))
    print("Total Primar carriers in %s: \t\t\t %s" %(loc,primary_carriers))
    print("Total Impact due to travel in %s: \t\t %s" %(loc,total_cases - uknown_total))
    print("Total Spread in %s from Primary carriers: \t %s" %(loc,total_spread))
    print("Total Unknown Local cases in %s: \t\t %s" %(loc,uknown_total))
    print("Total Spread from uknown Local cases in %s: \t %s" %(loc,uknown_spread))
    
    print("Impact in %s due to Travel from %s...."%(loc,travel))
    print("\tTotal Impact    : \t %s" %(travel_total))
    print("\tPrimary Carrier : \t %s" % travel_primar)
    print("\tTotal Spread    : \t %s" %(travel_spread))
        
          


# In[ ]:


def add_node(p,cp,age,gender,loc,travel):
    
    #Add localtion if does not exist.
    loc_node = search.find(root, lambda node: node.name == loc)
    if (loc_node == None):
#        print("Adding location %s node to" %loc,root)
        loc_node = Node(loc,parent=root,age='',gender='',loc='',travel='')
    
    #Under loc, add local if no travel, else create under travel.
    if (cp == ''):
        travel_his = search.find(loc_node,lambda node: node.name == travel)
        if (travel_his == None):
            #Adding travel 
#            print("Adding new node with travel ", p,loc_node, travel)
            travel_his = Node(travel,parent=loc_node,age='',gender='',loc='',travel='')
        par = travel_his
    else:
        par = search.find(root, lambda node: node.name == cp)
#    print("Adding patient %s to " % p,par,cp,loc)
    Node(p,parent=par,age=age,gender=gender,loc=loc,travel=travel)


# In[ ]:


def sort_dict(tlist):
    for item in sorted(tlist.keys()):
        add_node(tlist[item]['p'],
                 tlist[item]['par'],
                 tlist[item]['age'],
                 tlist[item]['gender'],
                 tlist[item]['loc'],
                 tlist[item]['travel'])
        
        #print(item)
#        print("Patient no %d contact of %s aged %s from %s has travel to %s" %(item,tlist[item]['par'],
#                                                                               tlist[item]['age'],
#                                                                               tlist[item]['loc'],
#                                                                               tlist[item]['travel']))


# In[ ]:


def add_to_graph(tlist,cont=''):
#    G=nx.DiGraph()
#    G = nx.generators.directed.random_k_out_graph(3, 1, 0.05)
#    G = nx.star_graph(2000)
    
    for item in sorted(tlist.keys()):
        contact = tlist[item]['par']
        patient = tlist[item]['p']
        if (contact == ''):
            print_graph(G,tlist,patient)
#            G.add_node(patient)
#            for item in sorted(tlist.keys()):
#                c = tlist[item]['par']
#                p = tlist[item]['p']
#                if (c == patient):
#                    G.add_edges_from([(p,patient)])
        else:
            continue
#        if (cont != '' and  contact != cont):
#            continue
#        if (contact != ''):
#            G.add_edges_from([(contact,patient)])
#        else:
#            G.add_node(patient)
#    nx.draw(G,with_labels=True)
#    pos = nx.spring_layout(G)
#    colors = range(20)
#    nx.draw(G, pos, with_labels=True)
#    plt.show()
#    nx.draw_graphviz(G)
#    print_graph(G)


# In[ ]:


def populate_data():
    total_count = 1
    local_spread = 1
#    root = Node("Covid-19",desc='Karnataka',age='',gender='',loc='',travel='')
#    Bang = Node('Bangalore', parent=root, desc='Resident of Bangalore',age='',gender='',loc='',travel='')
    i = 0
    p_list = {}
    tags = read_from_mirror()
    for tag in tags:
        
        if "Patient" in tag.text:
            r1 = tag.text.split('\n')
            for line in r1:  
                
                spread = False
                area_root = root
                par = None
                p = get_patient(line)
                if (p != ''):
                    total_count += 1
                    i += 1
                else:
                    continue
                cp = get_parent(line)
                if (cp != ''):
                    local_spread += 1
                    spread = True
                travel = get_travel(line) 
                (age,gender,loc) = get_age_and_place(line)
                p_list.update({int(p):{'p':p,"par":cp,"age":age,"gender":gender,"loc":loc,"travel":travel}})
                #add_node(p,cp,age,gender,loc,travel)
    #            if (i == 10):
    #                break
    sort_dict(p_list)
    return p_list


# In[ ]:


def print_graph(G,tlist,parent):
#    G = nx.DiGraph()
#    G.clear()
#    G.add_node(patient)
    
    for item in sorted(tlist.keys()):
        c = tlist[item]['par']
        p = tlist[item]['p']
        if (c == parent):
            G.add_edges_from([(parent,p)])
            print_graph(G,tlist,p)
    
#    plt.figure(figsize=(18,18))
#    graph_pos = nx.spring_layout(G)
#    nx.draw(G, with_labels=True)
#    plt.show()
#    nx.draw_networkx_nodes(G, graph_pos, node_size=10, node_color='blue', alpha=0.3)
#    nx.draw_networkx_edges(G, graph_pos)
#    nx.draw_networkx_labels(G, graph_pos, font_size=8, font_family='sans-serif')

#    plt.show()
    #plt.savefig("plot.p


# In[109]:


def print_g(G,patient,from_loc,relabel_list):
    if (len(G)<=2):
        return
#    graph_pos = nx.spring_layout(G)
#    nx.draw(G, with_labels=True)
#    plt.show()
    plt.figure(figsize=(18,18))
    plt.axis(False)
#    nx.draw_networkx_nodes(G, graph_pos, node_size=10, node_color='blue', alpha=0.3)
#    nx.draw_networkx_edges(G, graph_pos)
#    nx.draw_networkx_labels(G, graph_pos, font_size=8, font_family='sans-serif')
    nx.relabel_nodes(G, relabel_list, copy=False)
    nx.draw_spring(G,with_labels=True,edge_color="r",width=4,node_color="#A0CBE2",node_size=3000,arrowsize=18,font_size=16)
    name = "imagfiles/"+patient + "_from_" + from_loc + ".pdf" 
    plt.savefig(name,dpi=150)
#    plt.show()


# In[112]:


def display_graph(tlist,cont_filter='',loc_filter=''):
    G=nx.DiGraph()
#    G = nx.generators.directed.random_k_out_graph(3, 1, 0.05)
#    G = nx.star_graph(2000)
#    relabel_list = {}
    for item in sorted(tlist.keys()):
        contact = tlist[item]['par']
        patient = tlist[item]['p']
        loc = tlist[item]['loc']
        travel = tlist[item]['travel']
        if (loc_filter != '' and loc_filter != loc):
            continue
        if (contact == ''):
            G.clear()
            relabel_list = {}
            G.add_node(patient)
            relabel_list.update({patient:"patient no:"+ patient+"-"+loc+"-acquired-from-"+travel})
            print_graph(G,tlist,patient)
            print_g(G,patient,tlist[item]['loc'],relabel_list)

        else:
            continue


# In[ ]:


root = Node("Covid-19",desc='Karnataka',age='',gender='',loc='',travel='')
p_list = populate_data()


# In[ ]:


print_node(loc='Bangalore', travel='')


# In[113]:


display_graph(p_list)


# In[ ]:


import PyPDF2 as pypdf
import os
import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def merge_files():

    

    writer = pypdf.PdfFileWriter()
    files = entries = os.listdir('ImagFiles/')
    
    files.sort(key=natural_keys)
#    print(sfiles)
    for file in files:
        infile = open("ImagFiles/"+file,"rb")
        print("reading from ",file)
        reader = pypdf.PdfFileReader(infile)
        for page in range(reader.getNumPages()):
            writer.addPage(reader.getPage(page))
        # write everything in the writer to a file
    with open("ImagFiles/May3_graph.pdf","wb") as outFile:
        writer.write(outFile)
    outFile.close()


# In[114]:


merge_files()


# In[ ]:





# In[ ]:





# In[ ]:




