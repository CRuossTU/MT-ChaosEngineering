# -*- coding: utf-8 -*-
"""
@author: const

This modul is for conducting the experiments on the Simulation model Konzept_Shopfloor
To use this modul you also need the modul results_calc

Here the simulation time and the number of replications are defined
After that, the experiments are conducted and the results are saved in the Dataframe df_avg_std
To calculate the average and standard deviations for results of several simulation runs the function calc_averages is implemented


"""
import pandas as pd

from Shopfloor import experiment_start
from results_calc import avg_storage_utilization
from results_calc import avg_waittime
from results_calc import avg_durchsatz
from results_calc import avg_capacity_utilization


#determine the simulation time and the replications 
SIM_TIME = 432000
REPLICATIONS = 16


def condcut_experiments(sim_time, replications):
    #conducting the experiments and calculte the average and standard deviation for each metric
    #result is dataframe that includes a row for each simualtion run
    #for each simulation run the seed value is increased by 1 starting form 1
    
    df_avg_std = pd.DataFrame(columns = ["storage_utl_avg", "storage_utl_std", "durchsatz_avg_1", "durchsatz_std_1", "durchsatz_avg_2", "durchsatz_std_2",
                                         "capacity_utl_avg_1", "capacity_utl_std_1", "capacity_utl_avg_2", "capacity_utl_std_2",
                                         "waittime_avg_1", "waittime_std_1", "waittime_avg_2", "waittime_std_2"])
    
    for i in range(1, replications + 1):
        print(i)
        df_waittime, df_prod, df_storage = experiment_start(sim_time, i)
        df_avg_std.loc[i, "storage_utl_avg"], df_avg_std.loc[i, "storage_utl_std"] = avg_storage_utilization(df_storage)
        df_avg_std.loc[i, "waittime_avg_1"], df_avg_std.loc[i, "waittime_std_1"], df_avg_std.loc[i, "waittime_avg_2"], df_avg_std.loc[i, "waittime_std_2"] = avg_waittime(df_waittime)
        df_avg_std.loc[i, "durchsatz_avg_1"], df_avg_std.loc[i, "durchsatz_std_1"], df_avg_std.loc[i, "durchsatz_avg_2"], df_avg_std.loc[i, "durchsatz_std_2"] = avg_durchsatz(df_prod)
        df_avg_std.loc[i, "capacity_utl_avg_1"], df_avg_std.loc[i, "capacity_utl_std_1"], df_avg_std.loc[i, "capacity_utl_avg_2"], df_avg_std.loc[i, "capacity_utl_std_2"] = avg_capacity_utilization(df_prod)
        
    return df_avg_std
   
        
        
def calc_averages():
    #calculte the averages and standard deviations of the averages for each value
    #for example the average of the storage utilization is first calculated for every run over the simulation time seperatly 
    #then the average and standard deviation is calculated of that value for all conducted runs
    
    #contains the average and std for each value for each conducted run
    df_average_std_each_run = condcut_experiments(SIM_TIME, REPLICATIONS) 
    
    #contains the averages and std of the average values over all conducted simulation runs
    df_avg_over_all_runs =  pd.DataFrame(columns = ["storage_utl_avg", "storage_utl_std", "durchsatz_avg_1", "durchsatz_std_1", "durchsatz_avg_2", "durchsatz_std_2",
                                         "capacity_utl_avg_1", "capacity_utl_std_1", "capacity_utl_avg_2", "capacity_utl_std_2",
                                         "waittime_avg_1", "waittime_std_1", "waittime_avg_2", "waittime_std_2"])
    
    df_avg_over_all_runs.loc[1, ["storage_utl_avg"]] = df_average_std_each_run["storage_utl_avg"].mean()
    df_avg_over_all_runs.loc[1, ["storage_utl_std"]] = df_average_std_each_run["storage_utl_avg"].std()
    
    df_avg_over_all_runs.loc[1, ["durchsatz_avg_1"]] = df_average_std_each_run["durchsatz_avg_1"].mean()
    df_avg_over_all_runs.loc[1, ["durchsatz_std_1"]] = df_average_std_each_run["durchsatz_avg_1"].std()
    df_avg_over_all_runs.loc[1, ["durchsatz_avg_2"]] = df_average_std_each_run["durchsatz_avg_2"].mean()
    df_avg_over_all_runs.loc[1, ["durchsatz_std_2"]] = df_average_std_each_run["durchsatz_avg_2"].std()
    
    df_avg_over_all_runs.loc[1, ["capacity_utl_avg_1"]] = df_average_std_each_run["capacity_utl_avg_1"].mean()
    df_avg_over_all_runs.loc[1, ["capacity_utl_std_1"]] = df_average_std_each_run["capacity_utl_avg_1"].std()
    df_avg_over_all_runs.loc[1, ["capacity_utl_avg_2"]] = df_average_std_each_run["capacity_utl_avg_2"].mean()
    df_avg_over_all_runs.loc[1, ["capacity_utl_std_2"]] = df_average_std_each_run["capacity_utl_avg_2"].std()
    
    df_avg_over_all_runs.loc[1, ["waittime_avg_1"]] = df_average_std_each_run["waittime_avg_1"].mean()
    df_avg_over_all_runs.loc[1, ["waittime_std_1"]] = df_average_std_each_run["waittime_avg_1"].std()
    df_avg_over_all_runs.loc[1, ["waittime_avg_2"]] = df_average_std_each_run["waittime_avg_2"].mean()
    df_avg_over_all_runs.loc[1, ["waittime_std_2"]] = df_average_std_each_run["waittime_avg_2"].std()
    
    return df_average_std_each_run, df_avg_over_all_runs
    
    
#df_average_std = condcut_experiments(SIM_TIME, REPLICATIONS)

#df_average_std_each_run contains all averages and standard deviation for each metric for each replication
#df_avg_over_all_runs contains the average of all runs with the same factor setting
df_average_std_each_run, df_avg_over_all_runs = calc_averages()

#save the data
#df_average_std_each_run.to_csv("C:/Users/const/OneDrive/Dokumente/TU Darmstadt/Masterthesis/Experimente/analyse/average_std_each_run_Tabelle_Fertigungsprozess2.csv", sep=',', index=False, encoding='utf-8')
#df_avg_over_all_runs.to_csv("C:/Users/const/OneDrive/Dokumente/TU Darmstadt/Masterthesis/Experimente/analyse/average_over_all_runs_Fertigungsprozess2.csv", sep=',', index=False, encoding='utf-8')
