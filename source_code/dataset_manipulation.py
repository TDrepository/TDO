
class ValueConfidenceInfo:

    'Information required for computing the confidence of a specific value'
    value = None # value associated to the object
    confidence = None # current confidence of the value
    valueDependencies = None # the dependencies among value confidences -  confidence of this values have to be sum
    sourceTrustwordinessToAdd = None # set of the source trustwordiness to add - trustwordiness of these sources have to be added
    sourceTrustwordinessToRemove = None # dictionary of the source trustwordiness to remove (potentially several times for a same source)  - trustwordiness of these sources have to be added

    def __init__(self, value, confidence):
        self.value = value
        self.confidence = confidence

    def setValueDependencies(self, vd):
        self.valueDependencies = vd

    def setSourceTrustwordinessToAdd(self, d):
        self.sourceTrustwordinessToAdd = d

    def setSourceTrustwordinessToRemove(self, d):
        self.sourceTrustwordinessToRemove = d

    def __str__(self):

        value_dependencies_string = "None"
        source_trustwordiness_to_add_string = "None"
        source_trustwordiness_to_remove_string = "None"
        if not self.valueDependencies == None: value_dependencies_string = self.valueDependencies
        if not self.sourceTrustwordinessToAdd == None: source_trustwordiness_to_add_string = self.sourceTrustwordinessToAdd
        if not self.sourceTrustwordinessToRemove == None: source_trustwordiness_to_remove_string = self.sourceTrustwordinessToRemove
        out = "-----------------------------------------------------------------\n"
        out += "value: "+self.value+"\n"
        out += "-----------------------------------------------------------------\n"
        out += "confidence: "+str(self.confidence)+"\n"
        out += "-----------------------------------------------------------------\n"
        out += "value conf to sum "+value_dependencies_string+"\n"
        out += "-----------------------------------------------------------------\n"
        out += "source to add "+source_trustwordiness_to_add_string+"\n"
        out += "-----------------------------------------------------------------\n"
        out += "source to remove "+source_trustwordiness_to_remove_string+"\n"
        out += "-----------------------------------------------------------------"
        return out

def __init__(self):
    self.D = list()
    self.F_d = dict()

def load_sources_info(sources_file, header):
    ''' return a dictionary contained for each source its trustworthiness level
    <key = source_id, value = source_trustworthiness level>'''
    accuracies_source = {}

    with open(sources_file, "r", encoding="utf-8") as reader:
        for line in reader:
            if header:
                header = False
                continue

            line = line.strip()
            data = line.split("\t")

            if(len(data) != 2):
                print ("[Warning] skipping " + str(line))
                continue

            s = int(data[0].replace("source", ""))
            acc = float(data[1])

            if not(s in accuracies_source):
                accuracies_source[s]  = acc
            else:
                "WARNING DUPLICATE SOURCES"

    return accuracies_source

def load_facts(facts_file, header):
    '''upload a dictionary of this form
    <key = dataitem , value = <key = value_for_d, value = sources> >
    using the fact_XXX file - our dataset
    '''
    sources_dataItemValues = {}
    fact_cont = 0
    with open(facts_file, "r", encoding="utf-8") as reader:

        for line in reader:
            fact_cont = fact_cont + 1

            if header:
                header = False
                continue

            line = line.strip()
            data = line.split("\t")

            if(len(data) != 4):
                print(fact_cont)
                print ("[Warning] skipping " + str(line))
                continue

            d = data[1]
            v = data[2]

            s = int(data[3].replace("source", ""))
            if not( d in sources_dataItemValues): sources_dataItemValues[d]  = {}
            if not( v in sources_dataItemValues[d]): sources_dataItemValues[d][v]  = set()
            sources_dataItemValues[d][v].add(s)

    log_file.log("Load " + str(fact_cont) + " facts")
    return sources_dataItemValues

def load_facts_with_ids(facts_file, header, dataitem_ids):
    '''required if there are problems with memory space
    It does the same function of load_facts, but it load the ids not the string of data items'''
    sources_dataItemValues = {}
    with open(facts_file, "r", encoding="utf-8") as reader:
        for line in reader:
            if header:
                header = False
                continue

            line = line.strip()
            data = line.split("\t")

            if(len(data) != 4):
                print ("[Warning] skipping " + str(line))
                continue

            d = data[1]
            d = int(dataitem_ids[d])
            v = data[2]
            s = int(data[3].replace("source", ""))

            if not( d in sources_dataItemValues): sources_dataItemValues[d]  = {}
            if not( v in sources_dataItemValues[d]): sources_dataItemValues[d][v]  = set()
            sources_dataItemValues[d][v].add(s)

    return sources_dataItemValues

def load_fact_and_source_info(sources_dataItemValues):
    '''this function retrieves two dictionary
    - F_s represents the set of facts claimed by a source (<key = source, value = facts claimed by the source>)
    - S represents the set of sources that claim a fact (<key = fact, value = sources claimed the fact>)'''
    print ("Loading facts and source info")
    F_s = {}
    S = {}

    for d in sources_dataItemValues:
        for v in sources_dataItemValues.get(d):
            fact_id = d + v
            for s in sources_dataItemValues.get(d).get(v):

                if not s in F_s: F_s[s] = set()
                F_s.get(s).add(fact_id)

                if not fact_id in S: S[fact_id] = set()
                S.get(fact_id).add(s)

    return [F_s,S]

def load_dataitem_ids(file_path):
    #dataitem ids for storing informaiton for the propagation of belief phase
    dataitem_ids = {}
    print ("Loading dataitem ids from: ",file_path)

    file = open(file_path, 'r', encoding="utf-8")
    for row in file.readlines():
        row = (row[0:-1]).split('\t') #not consider \n char
        dataitem_ids[row[0]] = row[1]
    file.close()
    print ("dataitems loaded: ", len(dataitem_ids))

    return dataitem_ids

def load_all_dataitem_values_confidence_infos_low_memory(dataitem_ids, dir_path, sources_dataItemValues):
    '''read the file where the information required for computing the effects of belief propagation'''
    print ("Loading information to compute confidence of facts (dataitem + values) ")
    print ("processing ", len(dataitem_ids), " dataitems")
    print ("source directory: ", dir_path)

    S_prop = {}

    cont = 0
    cont_no_facts = 0
    for data_item in dataitem_ids:
        cont = cont + 1
        if (cont %1000 == 0):
            print ("Processed " + str(cont) +"/" +str(len(dataitem_ids)))
        fpath = dir_path + "/" + str(dataitem_ids.get(data_item))+".csv"

        f = open(fpath,'r', encoding="utf-8")

        for row in f.readlines():

            row = row.strip()
            data = 	row.split("\t")
            if(len(data) != 5):
                print ("[2_Warning] Excluding: "+row)
            else:
                if data[0] in sources_dataItemValues[data_item]:
                    S_prop[data_item+data[0]] = data[4]
                else:
                    cont_no_facts = cont_no_facts +1
        f.close()

    print ("number of values confidence infos loaded: "+str(len(S_prop)))
    print ("number of values confidence infos for which no source provided this facts: " + str(cont_no_facts))
    return [None, None, S_prop]
