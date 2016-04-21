'''
script to run experiments - Traditional Sums model and Adapted Sums model -
on different datasets contained in a specific folder
'''

import model
import os
import copy
import taxonomy_manipulation
import dataset_manipulation
import utils
import sys

def get_truth_trad(C_trad, d, ancestors, sources_dataItemValues, truth_trad, max_values_trad):
    '''return the solution given by the traditional SUMS models -
    therefore, for each data item, the value with the highest conficence -
    and the set of values that subsume this solution'''
    max_values_trad.clear()
    max_c = 0
    for v in sources_dataItemValues[d]:
        if C_trad[d+v] == max_c:
            max_values_trad.add(v)
        else:
            if C_trad[d+v] > max_c:
                max_values_trad.clear()
                max_values_trad.add(v)
                max_c = C_trad[d+v]

    truth_trad.clear()

    for element in max_values_trad:
        truth_trad.add(element)
        truth_trad = truth_trad.union(set(ancestors[element]))

    return [max_values_trad, truth_trad]

def get_max_children(max_values, C_adapt, d, children_set):
    #return one or more children that have the highest confidence level among the set of children
    max_c = 0
    max_values.clear()

    for v in children_set:
        if d+v in C_adapt:#somesource provided this value
            if C_adapt[d+v] == max_c:
                max_values.add(v)
            else:
                if C_adapt[d+v] > max_c:
                    max_values.clear()
                    max_values.add(v)
                    max_c = C_adapt[d+v]
        #else: in this case C_adapt = 0 therefore there is no evidence for it [no one stated it]

    return [max_values, max_c]

def get_truth_adapt(C_adapt, d, ancestors, children, truth_adapt, max_values):
    '''greedy algorithm that permits to retrieve the set of values that the adapted model finds as solution
    it has two steps: (i) propagation top-down (ii) propagation bottom-up.
    The parameter threshold_greedy can be change. For
    '''
    threshold_greedy = 0
    element = "http://www.w3.org/2002/07/owl#Thing" #element ROOT
    max_values.clear()
    max_values.add(element)
    most_specific_values = set()
    most_specific_values.add(element)

    etv = set()
    for item in max_values:
        etv = etv.union(set(children[item]))
    # propagatio top down
    while(len(etv) > 0):
        max_values.clear()
        max_children_sol = get_max_children(max_values, C_adapt, d, etv)
        max_values = max_children_sol[0]
        max_conf_value = max_children_sol[1]

        etv.clear()
        if (max_conf_value > threshold_greedy):
            most_specific_values.clear()
            for max_v in max_values:
                etv = etv.union(set(children[max_v]))
                most_specific_values.add(max_v)

    # propagatio bottom up
    for max_v in most_specific_values:
        truth_adapt.add(max_v)
        if max_v in ancestors:
            for a in ancestors[max_v]:
                truth_adapt.add(a)

    return truth_adapt

if __name__ == '__main__':
    predicate = str(sys.argv[1])
    if not ((predicate == 'genre') or (predicate == 'birthPlace')):
        print("errors in the parameters")
        exit()
    print("_______________________________Experiments and evaluation - Script launched_______________________________")
    # input
    #base_dir = "required_files_WIMS_2016_" + str(predicate) + "\\"
    base_dir = "required_files_WIMS_2016\\"
    if predicate == 'genre':
        base_dir = base_dir + "genre\\"
        graph_file = base_dir + 'ancestors_heuristic_genre_base.csv'
        graph_file_reduced = base_dir + 'ancestors_heuristic_genre_base_tr.csv'
        children_file = base_dir + "children_genre_base.csv"
        path_ground_file = base_dir + 'sample_genre_base_3.csv'
    else:#the predicate is 'birthPlace'
        base_dir = base_dir + "birthPlace\\"
        graph_file = base_dir + 'ancestors_heuristic.csv'
        graph_file_reduced = base_dir + 'ancestors_heuristic_tr.csv'
        children_file = base_dir + "children.csv"
        path_ground_file = base_dir + 'sample_ground_grouped.csv'

    path_datasets = "datasets\\"
    '''remerber to change also str_app_path = .....
    Indeed this variable will be interested for each changment in the path_datasets '''

    #output
    model_name = "sums"
    # Constants
    initial_trustworthiness = 0.8
    initial_confidence = 0.5
    max_iteration_number = 20
    #initialization
    D= list()
    T = list()
    S_set = list()
    fact_and_source_info = list()
    dataitem_values_info= list()
    F_s= dict()
    S_prop = dict()
    S=dict()
    sources_dataItemValues = dict()
    dataitem_ids = dict()
    #truth_adapt = set()
    #truth_trad = set()
    #truth_ground_truth = set()

    children = utils.loading_children(children_file)
    print ("number of children " +str(len(children)))
    ancestors = utils.loading_ancestors(graph_file)[0]
    print ("number of ancestors " +str(len(ancestors)))
    truth = utils.loading_ground_truth(path_ground_file)[0]
    print ("number of data item in truth  " +str(len(truth)))

    apply_transitive_reduction = True
    g = taxonomy_manipulation.load_graph(graph_file, graph_file_reduced, apply_transitive_reduction)

    for root, dirs, files in os.walk(path_datasets):

        for file in files:
            if file.startswith("facts_"):
                '''for each file named facts_XXX run the experiments'''
                print(os.path.join(root, file))
                print(root)
                file_name =os.path.basename(file)
                file_name = file_name.replace("facts_", "")
                n_dataset = file_name.replace(".csv", "")

                main_dataset_dir = root + "/"

                #input file paths
                facts_file = main_dataset_dir + "facts_" + str(n_dataset) + ".csv"
                dataitem_index_file = main_dataset_dir + "dataitems_index_" + str(n_dataset) + ".csv"
                source_file = main_dataset_dir + "Output_acc_" + str(n_dataset) + ".txt"

                # output file paths
                if "UNI" in root:
                    #str_app_path extract the number of the dataset
                    str_app_path = root.replace( path_datasets + "\\UNI\\dataset", "")
                    main_results_dir = "results\\results_" + str(model_name) + "/" + "datasetUNI"  + str(str_app_path) + "/"

                if "EXP" in root:
                    str_app_path = root.replace(path_datasets + "EXP\\dataset", "")
                    main_results_dir = "results\\results_" + str(model_name) + "/" + "datasetEXP"  + str(str_app_path) + "/"

                if "LOW_E" in root:
                    str_app_path = root.replace(path_datasets + "LOW_E\\dataset", "")
                    main_results_dir = "results\\results_" + str(model_name) + "/" + "datasetLOW_E" + str(
                        str_app_path) + "/"
                #adapted model results files and dir
                adapted_result_dir = main_results_dir + "adapted/"
                adapted_result_conf_dir = adapted_result_dir + "/data_items/"
                adapted_output_trust_file = adapted_result_dir + "est_trust" + str(n_dataset) + ".csv"
                adapted_output_trust_file_iter = adapted_result_dir + "est_trust_for_iter_" + str(n_dataset) + ".csv"
                adapted_output_trust_file_iter_delta = adapted_result_dir + "est_trust_for_iter_delta" + str(n_dataset) + ".csv"
                # traditional model results files and dir
                trad_result_dir = main_results_dir + "trad/"
                trad_output_trust_file = trad_result_dir + "est_trustworthiness_" + str(n_dataset) + ".csv"
                trad_output_trust_file_iter = trad_result_dir + "est_trust_for_iter_" + str(n_dataset) + ".csv"
                trad_output_trust_file_iter_delta = trad_result_dir + "est_trust_for_iter_delta_" + str(n_dataset) + ".csv"
                confidence_value_computation_info_dir = main_dataset_dir+"/confidence_value_computation_info"
                #comparison file of trust results
                out_comparison_trust_file = main_results_dir + "comparison_trust_" + str(n_dataset) + ".csv"
                #creation of dir
                if not os.path.exists(confidence_value_computation_info_dir): os.makedirs(confidence_value_computation_info_dir)
                if not os.path.exists(main_results_dir): os.makedirs(main_results_dir)
                if not os.path.exists(adapted_result_dir): os.makedirs(adapted_result_dir)
                if not os.path.exists(trad_result_dir): os.makedirs(trad_result_dir)

                print("file names reloaded")

                #clear all the variable to not overload the memory
                dataitem_ids.clear()
                D.clear()
                T.clear()
                S_set.clear()
                S.clear()
                F_s.clear()
                S_prop.clear()
                sources_dataItemValues.clear()
                dataitem_values_info.clear()
                fact_and_source_info.clear()

                #loading source information
                header = False #dictionary with the original trustworthiness
                T_actual = dataset_manipulation.load_sources_info(source_file, header)

                header = False #dictionary with the original trustworthiness, but it will be used by the estimation process
                T = dataset_manipulation.load_sources_info(source_file, header)
                print (str(len(T)) + " sources loaded")

                S_set = list(T.keys()) #source set - all the ids

                #load fact information
                header = True
                sources_dataItemValues = dataset_manipulation.load_facts(facts_file, header)

                #load data item set
                D = list(sources_dataItemValues.keys())

                # compute (1) all the facts that are claimed by a source and (2) all the sources that claim a specific fact
                # (1) set of facts that are claimed by a specific source < key = source id, value = set of facts (dataitem + value) >
                # (2) all the sources that claim a specific fact <key = dataitem + value, value = set of source ids>
                print("Fact loading")
                fact_and_source_info = dataset_manipulation.load_fact_and_source_info(sources_dataItemValues)
                F_s = fact_and_source_info[0]
                S = fact_and_source_info[1]

                print("Computing sources for " + str(len(sources_dataItemValues)) + " data items FOR COMPUTATION PURPOSE")
                if not(len(os.listdir(confidence_value_computation_info_dir)) == len(D)):
                    # compute the files for belief propagation information
                    print("graph nodes " + str(len(g.nodes)))

                    res = taxonomy_manipulation.create_value_info_computation(g, sources_dataItemValues, D, dataitem_index_file, confidence_value_computation_info_dir)
                    sources_dataItemValues.clear()
                    header = True
                    sources_dataItemValues = dataset_manipulation.load_facts(facts_file, header)

                    if res == True:
                       print("Computation DONE")
                # else: the files for contained the info for the belief propagation have been already computed
                #then load the relative dataitem id for using the files
                dataitem_ids = dataset_manipulation.load_dataitem_ids(dataitem_index_file)
                #load the information
                dataitem_values_info = dataset_manipulation.load_all_dataitem_values_confidence_infos_low_memory(dataitem_ids, confidence_value_computation_info_dir, sources_dataItemValues)
                #S_prop is a dictionary contained for each fact all the sources that it has to take into account for leveraging the belief propagation framework
                S_prop = dataitem_values_info[2]

                #######################################################################################################
                ################all the informaiton required are uploaded, NOW the experiments start###################
                #######################################################################################################
                print("Sums Experiments")

                #this function save the error rate at each iteration, this is done for checking the convergence empirically
                res_t = model.run_sums_saving_iter(copy.deepcopy(T), F_s, S, initial_confidence, max_iteration_number, trad_output_trust_file_iter, trad_output_trust_file_iter_delta, T_actual)
                if res_t:
                    T_trad = res_t[0]
                    C_trad = res_t[1]
                    true_facts_trad = dict()
                    for d in sources_dataItemValues:
                        true_facts_trad[d] = get_truth_trad(C_trad, d, ancestors, sources_dataItemValues, set(), set())[0]
                    ''' WRITE OUTPUT RESULTS --> if you want do that de-comment both following lines'''
                    res = model.writing_trust_results(trad_output_trust_file, T_trad)
                    # res = model.writing_confidence_results(trad_output_conf_dir, sources_dataItemValues, dataitem_ids, C_trad)
                else:
                    print("Error in traditional model")

                #######################################################################################################
                print("Adapted Sums Experiments")
                #res_a = model.run_adapted_sums(copy.deepcopy(T), F_s, S_prop, initial_confidence, max_iteration_number)
                res_a = model.run_adapted_sums_saving_iter(copy.deepcopy(T), F_s, S_prop, initial_confidence, max_iteration_number, sources_dataItemValues, adapted_output_trust_file_iter, adapted_output_trust_file_iter_delta, T_actual)
                if res_a:
                    T_adapt = res_a[0]
                    C_adapt= res_a[1]
                    true_facts_adapt = dict()
                    for d in sources_dataItemValues:
                        true_facts_adapt[d] = get_truth_adapt(C_adapt, d, ancestors, children, set(), set())
                    ''' WRITE OUTPUT RESULTS --> if you want do that de-comment both following lines'''
                    res = model.writing_trust_results(adapted_output_trust_file, T_adapt)
                    # res = model.writing_confidence_results(adapted_output_conf_dir, sources_dataItemValues, dataitem_ids, C_adapt)
                else:
                    print("Error in adapted model")

                #######################################################################################################
                ################                        RESULT ANALYSIS                             ###################
                #######################################################################################################
                #(i) analysis of source trustworthiness estimations
                header = False
                T = dataset_manipulation.load_sources_info(source_file, header) #load original trust. values
                if T_adapt != None and T_trad != None and T != None:
                    # write the csv file for the comparison of the error rate in the two cases
                    res = model.writing_comparsion_file(out_comparison_trust_file, T, T_trad, T_adapt)
                    if res == False:
                        print("ERROR in writing the file of comparison")

                #clear results array
                if (res_a!= None): res_a.clear()
                if (res_t!= None): res_t.clear()
                if (T!= None): T.clear()
                if (T_adapt!= None): T_adapt.clear()
                if (T_trad!= None): T_trad.clear()

                print("  The experiments for this dataset have been done  ")
                print("___________________________________________________")
