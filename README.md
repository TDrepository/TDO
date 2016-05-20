# TDO - Truth-Discovery with Ontology

Author:
 - Valentina Beretta
	
Co-authors:
 - Sebastien Harispe
 - Sylvie Ranwez
 - Isabelle Mougenot

TDO library permits to (i) generate sythetic dataset; (ii) test the traditional and adapted Sums approach [....]


For repeat the experiments you have to follow the following steps:

 - make sure that "Pyhton 3.4" is installed on your computer and use it to run the .py files 
 
##INPUTs:
 - download the datasets at https://dx.doi.org/10.6084/m9.figshare.3393706, unzip the archive and put the folder contained the dataset that you want analyze (you can choose one predicate dataset at time) in the empty project folder named "datasets"
 - download the required file wims folder at https://dx.doi.org/10.6084/m9.figshare.3393817, unzip the archive and put it in the folder named "data" of the project

 
##RUN the experiments
 - open the terminal and move in the "source_code" folder contained in the main project folder
 - write the following command line
	> python Main_experiments.py name_predicate
   where name_predicate is the parameter that contains the name of the dataset we entend to examine. So far this parameter can assume
 
##OUTPUTs:
 - all the results file will be stored in "results" located in the "source_code" project folder.
 - a summary of the obtained results can be obtained using the function avaiable using output_analysis.py script. 
   You have to write the following command line
		> python output_results.py results_dir
   where results_dir is the parameter that contains the path where the results you want to summarize are stored.

Dataset generation datails will be added.[**]

##REFERENCES
*“How Can Ontologies Give You Clue for Truth-Discovery? An Exploratory Study”*. Valentina Beretta, Sébastien Harispe, Sylvie Ranwez, Isabelle Mougenot. To be published in the proceedings of WIMS 2016.
