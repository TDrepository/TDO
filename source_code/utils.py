import sys
import csv
''' this functions will permits to load all the file in the "required files" folder'''
def loading_ground_truth(path_ground_file):
    '''read GROUNDTRUTH csv file where all the triple are saved.
    format of GROUNDTRUTH.csv file is "subject, predicate, value"
    example PabloPicasso, bornIn, Malaga
    #        Giovanni, bornIn, Renate
    #        etc
    return an array where in the first position there is a dictionary <key= data item, values = true value>
    and in the second position the set of data items
    '''
    try:
        D = []
        truth = dict()
        with open(path_ground_file, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t', quotechar='|')

            for row in reader:
                dataitem = row['subject'] # for the moment I don't use predicate ---> + ';' + row['predicate']
                value = row['value']
                truth[dataitem] = value
                D.append(dataitem)

        return [truth, D]
    except:
        print("Error in loading ground truth")
        return None

def loading_children(file_path):
    '''given a file where each row contains the URI of a node (e.g. a value) and all its URI's children
    return a dictionary <key= value, values = children of the value>
    '''
    try:
        children = dict()
        with open(file_path, newline='', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                data = line.split('\t')
                key = data[0]
                if len(data) == 1:
                    values = []
                else:
                   child_str = (data[1]).replace(';http', '_____http')
                   values = child_str.split('_____')
                #update dictionary of children of each node
                children[key] = values

        return children
    except:
        print ("No children file")
        print ("Unexpected error:", sys.exc_info()[0])
        return None

def loading_ancestors(path_ancestor_file):
    '''the ancestor file should have the header part
    the ancestor file tr have  not the header part
    return a dictionary <key= value, values = inclusive ancestors of the value>
    '''
    try:
        ancestors = dict()
        tax_domain = set()
        with open(path_ancestor_file, newline='', encoding='utf-8') as file_ancestor:
            if not (path_ancestor_file.endswith("_tr.csv")): file_ancestor.readline()
            for row in file_ancestor:
                row = row.strip()
                data = row.split('\t')
                key = data[0]
                line_anc = (data[1]).replace(';http', '_____http')
                values = line_anc.split('_____')
                ancestors[key] = set(values)
                #put ancestor in taxonomy domain
                tax_domain.update(values)
                tax_domain.add(key)

        return [ancestors, tax_domain]
    except :
        print("No ancestor file")
        return None

def loading_descendents(path_ancestor_file):
    try:
        descendents = dict()

         #with open(path_ancestor_file, newline='') as csvfile_ancestor:
        with open(path_ancestor_file, "r", encoding='utf-8') as file:
            #header
            file.readline()
            for row in file:
                 #no header this file
                 #key = row['value']
                 #line_anc = (row['ancestors']).replace(';http', '_____http')
                row = row.strip()
                data = row.split('\t')
                value = data[0]
                value_desc = (data[1])[2:-2].split("', '")
                descendents[value] = value_desc

        return descendents
    except :
        print("No descendent file")
        return None

def loading_descendants_exclusive_fileformat2(path_file):
    try:
        descendents = dict()

         #with open(path_ancestor_file, newline='') as csvfile_ancestor:
        with open(path_file, newline='', encoding='utf-8') as reader:
             #readerAncestor = csv.DictReader(csvfile_ancestor, delimiter='\t')
            #togli per heuristic tr
             reader.readline()
             for row in reader:

                 row = row.strip()
                 data = row.split('\t')
                 key = data[0]
                 line_desc = (data[1]).replace(';http', '_____http')
                 values = line_desc.split('_____')
                 set_values = set(values)
                 set_values.remove(key)
                 descendents[key] = set_values

        return descendents
    except :
        print("No descendents file")
        return None

def loading_descendants_fileformat2(path_file):
    try:
        descendents = dict()

         #with open(path_ancestor_file, newline='') as csvfile_ancestor:
        with open(path_file, newline='', encoding='utf-8') as reader:
             #readerAncestor = csv.DictReader(csvfile_ancestor, delimiter='\t')
            #togli per heuristic tr
             reader.readline()
             for row in reader:
                row = row.strip()
                data = row.split('\t')
                key = data[0]
                line_desc = (data[1]).replace(';http', '_____http')
                values = line_desc.split('_____')
                descendents[key] = set(values)

        return descendents
    except :
        print("No descendents file")
        return None

def loading_descendents_no_header(path_ancestor_file):
    try:
        descendents = dict()
        with open(path_ancestor_file, "r", encoding='utf-8') as file:

            for row in file:
                row = row.strip()
                data = row.split('\t')
                value = data[0]
                line_anc = (data[1]).replace(';http', '_____http')
                values = line_anc.split('_____')
                descendents[value] = set(values)

        return descendents
    except :
        print("No descendent file")
        return None

def loading_values_sim_ids(path_ids_file):
    try:
        ids = {}
        with open(path_ids_file, encoding='utf-8') as file:
            for row in file.readlines():
                row = row.split('\t')
                ids[row[1][0:-1]] = row[0]#do not consider \n digit
        return ids
    except:
        print("Errors in loading values sim ids")
        return None

def load_values_sim_measure(path_values_sim_file, myzipfile, value_id, sim_dict):

    file = myzipfile.open(path_values_sim_file + value_id)
    #read file of sim measures for this solution
    for row in file.readlines():
        row = (row.decode()).split('\t')
        sim_dict[row[0]] = float(row[1][0:-1])#not consider \n char

    file.close()
    return sim_dict
