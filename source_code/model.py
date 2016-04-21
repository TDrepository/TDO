import time
from copy import deepcopy

def run_sums_saving_iter(T, F_s, S, initial_confidence, max_iteration_number, output_file, output_file_delta, T_actual):
    #function that implements the sums model
    T_iter = dict()
    T_iter_delta = dict()

    print("START : traditional sums " + " _ Convergence criteria : max iteration number (" + str(max_iteration_number) + ")")
    #traditional sums
    #t_start = time.time()
    convergence = False
    iteration_number = 0

    # confidences for all the facts
    # <key = dataitem + value, value = confidence>
    C = dict()
    for fact_id in S:
        C[fact_id] = initial_confidence

    # iteration for estimating C and T
    while (not convergence):
        #t_start_iter = time.time()
        for source_id in T:
            sum = 0

            facts = F_s.get(source_id) # get facts provided by this source

            for f in facts:
                if not f in C:
                    print ("Error cannot find confidence for ", f)
                    exit()
                sum = sum + (C.get(f))
            T[source_id] = sum

        # normalizing using the maximum value in the list of T
        max_value = max(T.values())
        for source_id in T:
            T[source_id] = T[source_id] / max_value

        C.clear() #in this way - without creating a new obj - is more fast

        for fact_id in S:# S represents all the sources that claim a specific fact <key = dataitem + value, value = set of source ids>
            sum = 0

            for s in S.get(fact_id): #source provining the fact <d+v>
                if not s in T:
                    print ("Error cannot find trustwordiness for ", s)
                    print (S.get(fact_id))
                    exit()
                sum = sum + T[s]
            C[fact_id] = sum

        #normalization
        max_value = max(C.values())
        for fact_id in C:
            C[fact_id] = C.get(fact_id) / max_value

        #save result iteration
        for source_id in T:
            if source_id not in T_iter:
                str_app = str(T[source_id])
                str_app_delta = str(abs(float(T[source_id]) - float(T_actual[source_id])))
            else:
                str_app = str(T_iter[source_id]) + "\t" + str(T[source_id])
                str_app_delta = str(T_iter_delta[source_id]) + "\t" + str(abs(float(T[source_id]) - float(T_actual[source_id])))
            T_iter[source_id] = str_app
            T_iter_delta[source_id] = str_app_delta

        #check conditions ---> 20th iteration has been reached
        if (iteration_number >= max_iteration_number - 1):
            convergence = True

        #t_end_iter = time.time()
        #t_tot_iter = t_end_iter - t_start_iter

        iteration_number = iteration_number + 1
        print(str(iteration_number))
       # print ('Iteration ' + str(iteration_number) + ' ----- Running time : '+ str(t_tot_iter))

    writing_trust_results(output_file, T_iter) #puntual results
    writing_trust_results(output_file_delta, T_iter_delta) #error rate results
    #t_end = time.time()
    #print('run time: ' + str( t_end - t_start))
    return [T, C]
    #END SUMS MODEL

def run_adapted_sums_saving_iter(T, F_s, S_prop, initial_confidence, max_iteration_number, sources_dataItemValues, output_file, output_file_delta, T_actual):
    # function that implements the adapted model
    T_iter = dict()
    T_iter_delta = dict()
    print("START : sums_ADAPTED " + " _ Convergence criteria : max iteration number (" + str(max_iteration_number) + ")")

    #t_start = time.time()
    convergence = False
    iteration_number = 0
    # confidences for all the facts
    # <key = dataitem + value, value = confidence>
    C = dict()
    for fact_id in S_prop:
        C[fact_id] = initial_confidence

    #iteration for estimating C and T
    while (not convergence):
        #t_start_iter = time.time()

        for source_id in T:
            sum = 0
            facts = F_s.get(source_id) # get facts provided by this source
            for f in facts:
                if not f in C:
                    print ("Error cannot find confidence for ", f)
                    exit()
                sum = sum + (C.get(f))
            T[source_id] = sum

        # normalizing using the maximum value in the list of T
        max_value = max(T.values())
        for source_id in T:
            T[source_id] = T[source_id] / max_value

        C = dict()

        for fact_id in S_prop:
            source_plus_set = S_prop.get(fact_id).split(";")
            sum = 0
            for s in source_plus_set:
                try:
                    s = int(s)
                    sum = sum + T[s]
                except ValueError:
                    sum = sum + T[int(s.replace("source", ""))]

            C[fact_id] = sum
        #normalization
        max_value = max(C.values())
        for item in C:
            C[item] = C.get(item) / max_value

        #save result iteration
        for source_id in T:
            if source_id not in T_iter:
                str_app = str(T[source_id])
                str_app_delta = str(abs(float(T[source_id]) - float(T_actual[source_id])))
            else:
                str_app = str(T_iter[source_id]) + "\t" + str(T[source_id])
                str_app_delta = str(T_iter_delta[source_id]) + "\t" + str(abs(float(T[source_id]) - float(T_actual[source_id])))

            T_iter[source_id] = str_app
            T_iter_delta[source_id] = str_app_delta

        #check conditions --> the number of iteration is 20
        if (iteration_number >= max_iteration_number - 1):
            convergence = True

        iteration_number = iteration_number + 1

        #t_end_iter = time.time()
        # t_tot_iter = t_end_iter - t_start_iter
        print(str(iteration_number))
        #print ('Iteration ' + str(iteration_number) + ' ----- Running time : '+ str(t_tot_iter))

    #convergence reached -- end process
    writing_trust_results(output_file, T_iter)
    writing_trust_results(output_file_delta, T_iter_delta)

    #t_end = time.time()
    #print('run time: ' + str( t_end - t_start))

    return [T,C]
    #END FUNCTION ADAPTED MODEL

def writing_trust_results(output_file, T):
    print("flushing the trust result into file.....")
    try:
        file = open(output_file, "w")
        for source_id in T:
            file.write(str(source_id) + "\t" + str(T[source_id]) + "\n")

        file.close()
        return True
    except:
        print("Errors in saving error rate trust estimations")
        return False

def writing_confidence_results(output_file, sources_dataItemValues, dataitem_ids, C):
    '''this saving required a lot of disk space.
    To do only if it is necessary
    '''
    print("flushing the confidence result into file.....")
    try:
        for d in sources_dataItemValues:
            file = open(output_file + "/" + str(dataitem_ids.get(d))+ ".csv", "w")
            app = dict()
            for v in sources_dataItemValues.get(d).keys():
                app[v] = C.get(d + v)
            app_ord = sorted(app, key = app.__getitem__, reverse = True)
            for item in app_ord:
                file.write(str(item) + "\t" + str(C[d + item])+"\n")
            file.close()
        return True
    except:
        print("Errors in saving confidence estimations")
        return False

def writing_comparsion_file(adapted_out_comparison_trust_file, T, T_trad, T_adapt):
    print("flushing the trust result comparison into file.....")
    try:
        file = open(adapted_out_comparison_trust_file, "w")
        average_err_trad = 0
        average_err_adapt = 0
        for source_id in T:
            v_act = T[source_id]
            v_trad = T_trad[source_id]
            v_adapt = T_adapt[source_id]
            trad_vs_act = abs(v_act - v_trad)
            adapt_vs_act = abs(v_act - v_adapt)
            error_advantages = adapt_vs_act - trad_vs_act #if it is negative our model is better, the error is evaluated

            file.write(str(source_id) + "\t" + str(v_trad) + "\t" + str(v_adapt) + "\t" + str(v_act) + "\t" + str(trad_vs_act) + "\t" + str(adapt_vs_act) + "\t" + str(error_advantages)+ "\n")

            average_err_trad =  average_err_trad + trad_vs_act
            average_err_adapt = average_err_adapt + adapt_vs_act

        file.write("\n")
        average_err_trad = average_err_trad/len(T)
        average_err_adapt = average_err_adapt/len(T)
        file.write("AVERAGE" + "\t" + str(average_err_trad) + "\t" + str(average_err_adapt) + "\t" + str(average_err_adapt-average_err_trad) + "\n")

        file.close()
        return True
    except:
        print("Errors in saving trust estimation comparison file")
        return False
