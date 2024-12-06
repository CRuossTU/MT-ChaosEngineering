# -*- coding: utf-8 -*-
"""
@author: const

This modul contains the functions to calculate the metrics relevant for the analysis of the simulation
There is one function for each metric and for each metric the average value and the standard deviation are calculated
Each process receives a dataframe containing the relevant information 

"""

import pandas as pd


def avg_waittime(df_wait):
    #calculate the average and standatd deviation for the waittime for each process and return these values
    
    df_wait_new = df_wait.drop(df_wait[df_wait["ID"] == "ID 99999"].index)
    
    df_wait_stage1 =  df_wait.loc[(df_wait["production stage"] == 1) & (df_wait["wait"] == "begin")]
    df_wait_stage2 =  df_wait.loc[(df_wait["production stage"] == 2) & (df_wait["wait"] == "begin")]
    
    df_results_stage1 = pd.DataFrame(columns = ["waittime", "time"])
    df_results_stage2 = pd.DataFrame(columns = ["waittime", "time"])
    
    for row in df_wait_stage1.index:
        ID = df_wait_stage1.loc[row, "ID"]
        part = df_wait_stage1.loc[row, "part"]
        stage = 1
        
        try:
            endtime = df_wait_new.loc[(df_wait_new["ID"] == ID) & (df_wait_new["part"] == part)
                                  & (df_wait_new["production stage"] == stage) & (df_wait_new["wait"] == "end"),
                                  "time"].iloc[0]
        except:
            continue
        starttime = df_wait_stage1.loc[row, "time"]
        waittime = endtime - starttime
        df_results_stage1.loc[len(df_results_stage1.index)] = [waittime, endtime]
    
    for row in df_wait_stage2.index:
        ID = df_wait_stage2.loc[row, "ID"]
        part = df_wait_stage2.loc[row, "part"]
        stage = 2
        
        try:
            endtime = df_wait_new.loc[(df_wait_new["ID"] == ID) & (df_wait_new["part"] == part)
                                  & (df_wait_new["production stage"] == stage) & (df_wait_new["wait"] == "end"),
                                  "time"].iloc[0]
        except:
            continue
        starttime = df_wait_stage2.loc[row, "time"]
        waittime = endtime - starttime
        df_results_stage2.loc[len(df_results_stage2.index)] = [waittime, endtime]
        
    avg_wait_stage1 = df_results_stage1["waittime"].mean()
    avg_wait_stage2 = df_results_stage2["waittime"].mean()
    std_wait_stage1 = df_results_stage1["waittime"].std()
    std_wait_stage2 = df_results_stage2["waittime"].std()
    
    return  avg_wait_stage1, std_wait_stage1, avg_wait_stage2, std_wait_stage2


def avg_capacity_utilization(df_prod):
    #calculate the average and standatd deviation for the capacity utilization for each process and return these values
    
    df_prod_stage1 = df_prod.loc[df_prod["production stage"] == 1]
    df_prod_stage2 = df_prod.loc[df_prod["production stage"] == 2]
    
    df_results_stage1 = pd.DataFrame(columns = ["utilization", "time"])
    df_results_stage2 = pd.DataFrame(columns = ["utilization", "time"])
    
    for row in df_prod_stage1.index:
        utl = (df_prod_stage1.loc[row, "occupied machines"])/3
            
        df_results_stage1.loc[len(df_results_stage1.index)] = [utl, df_prod_stage1.loc[row, "time"]]
        
    for row in df_prod_stage2.index:
        utl = (df_prod_stage2.loc[row, "occupied machines"])/3
            
        df_results_stage2.loc[len(df_results_stage2.index)] = [utl, df_prod_stage2.loc[row, "time"]]
        
    avg_cap1 = df_results_stage1["utilization"].mean()
    avg_cap2 = df_results_stage2["utilization"].mean()
    std_cap1 = df_results_stage1["utilization"].std()
    std_cap2 = df_results_stage2["utilization"].std()
    
    return avg_cap1, std_cap1, avg_cap2, std_cap2


def avg_durchsatz(df_prod):
    #calculate the average and standatd deviation for the throuput for each process and return these values
    
    df_prod_stage1 = df_prod.loc[(df_prod["production stage"] == 1) & (df_prod["position"] == "leave")]
    df_prod_stage2 = df_prod.loc[(df_prod["production stage"] == 2) & (df_prod["position"] == "leave")]
    df_result_stage1 = pd.DataFrame(columns = ["Durchsatz", "time"])
    df_result_stage2 = pd.DataFrame(columns = ["Durchsatz", "time"])
    
    last_time1 = (df_prod_stage1.tail(1)["time"]).iloc[0]
    number_hours1 = int(last_time1/60) + 1 
    for i in range(1, number_hours1 + 1):
        df_prod1_hour = df_prod_stage1[(df_prod_stage1["time"] <= 60 * i) & (df_prod_stage1["time"] >= 60 * (i - 1))]
        durchsatz = len(df_prod1_hour)
        df_result_stage1.loc[len(df_result_stage1.index)] = [durchsatz, i]
          
    last_time2 = (df_prod_stage2.tail(1)["time"]).iloc[0]
    number_hours2 = int(last_time2/60) + 1 
    for j in range(1, number_hours2 + 1):
        df_prod2_hour = df_prod_stage2[(df_prod_stage2["time"] <= 60 * j) & (df_prod_stage2["time"] >= 60 * (j - 1))]
        durchsatz = len(df_prod2_hour)
        df_result_stage2.loc[len(df_result_stage2.index)] = [durchsatz, j]
        
    avg_durchsatz_stage1 = df_result_stage1["Durchsatz"].mean()
    avg_durchsatz_stage2 = df_result_stage2["Durchsatz"].mean()
    std_durchsatz_stage1 = df_result_stage1["Durchsatz"].std()
    std_durchsatz_stage2 = df_result_stage2["Durchsatz"].std()
    
    return avg_durchsatz_stage1 , std_durchsatz_stage1, avg_durchsatz_stage2, std_durchsatz_stage2
    


def avg_storage_utilization(df_storage):
    #calculate the average and standatd deviation for the storag utilization and return these values
    
    df_store = df_storage
    df_store["inventory"] = df_store["inventory"].div(50)
    
    avg_store = df_store["inventory"].mean()
    std_store = df_store["inventory"].std()
    
    return avg_store, std_store


