# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:37:29 2024

@author: const
"""

# -*- coding: utf-8 -*-
"""
@author: const

Simulation with Chaos Engineering of a Shopfloor

The shopfloor consists of 2 process stages with each three machines and one storage between them.
Orders are generated and each part of that order is passed through the production processes and the storage.
To conclude information about the systems resilience the three processes are broken randomly.

"""

import simpy
import numpy as np
import pandas as pd
import random
#import time


def time_to_failure():
    #determine the time between failures for the Chaos Experiments
    print("CE beginnt")
    return random.randint(10000, 180000)

def repair_time():
    #determmine the repair time for process 1 and 2
    return random.normalvariate(21600, 1600) 

def repair_time_storage():
    #determmine the repair time for the storage
    return random.normalvariate(3600, 50) 

class ShopFloor:
    #class shopfloor includes the source, the production processes, the store process
    #and the functions to break part of those processes in the Chaos Experiments
    
    def __init__(self, env, n_machines, machine_times, machine_std,
                 machine_downtime, machine_CO, storage_capacity, storage_init):
        #init methode
        
        self.env = env
        
        #create 2 stages with 3 machines each as Priority Resources
        self.machines = [simpy.PriorityResource(env, n_machines[i]) for i in range(len(n_machines))]
        
        #create one storage as a Container with a max capacity and an inventory
        self.storage = simpy.Container(env, capacity= storage_capacity, init = storage_init)
        
        #create one storage_break resource to determine when the storage is broken
        self.storage_break = simpy.PriorityResource(env, 1)
        
        self.n_machines = n_machines
        self.machine_times = machine_times
        self.machine_std = machine_std
        self.machine_downtime = machine_downtime
        self.machine_CO = machine_CO
        
        #array to determine if production process 1, the storage or production process 2 are broken
        #array to determine if failure is caused by CE, downtime or changeover time
        self.broken = [0,0,0]
        self.broken_typ = [0,0,0]
        
        #create empty dataframes
        self.df_prod = pd.DataFrame(columns = ["ID", "part","order size", "production stage","position", "occupied machines",
                                        "time"])
        self.df_storage = pd.DataFrame(columns = ["inventory", "time"])
        self.df_wait = pd.DataFrame(columns = ["ID", "part", "order size", "production stage", "wait", "time"])
        
        
        
    def source(self, ID, order_size, prio):
       #gets information about the order 
        
        for i in range(order_size):
            #creates parts of the order for the given order size
            #storage break has a capacity of one and is occupied when the storage is broken and therefore no order can be processed but is queued
            #process to occupied the ressource storage_break have a priority of 1 
            
            with self.storage_break.request(priority = prio) as request:
                
                yield request
                if prio == 1:
                    yield self.env.timeout(repair_time_storage())
                    self.broken[1] -= 1
                    return
            
            #check if storage level is higher than the capacity 
            #try to acitivate production process 1, if not possible wait 5s and try again
            shipped1 = True
            while shipped1:
                if self.storage.level < self.storage.capacity:
                    yield self.env.timeout(5) #transport time
                    self.env.process(self.prod_process1(i+1, order_size, ID, prio))
                    shipped1 = False
                else:
                    yield self.env.timeout(5) #waiting time for new while loop
              
   
    def production_control(self, ID, order_size, prio):
        #gets information about the order
        
        for x in range(order_size):   
            #creates parts of the order for the given order size
            
            #storage break has a capacity of one and is occupied when the storage is broken and therefore no order can be processed but is queued
            #process to occupied the ressource storage_break have a priority of 1 
            
            with self.storage_break.request(priority = prio) as request:
                
                yield request
                if prio == 1:
                    yield self.env.timeout(repair_time_storage())
                    self.broken[1] -= 1
                    return
            
            #check if storage level is highern than 0
            #try to acitivate production process 2, if not possible wait 5s and try again
            shipped2 = True
            while shipped2:     
                if self.storage.level > 0:
                    yield self.env.timeout(5) #transport time
                    self.env.process(self.prod_process2(x+1, order_size, ID, prio))
                    shipped2 = False
                else:
                    yield self.env.timeout(5) #waiting time for new while loop
                
                       
    def prod_process1(self, part, order_size, ID, prio):
       
       #request any machine of production stage 1
       #break processes have higher priority than orders
        with self.machines[0].request(priority=prio) as request:
            
            #save data to calculate the waiting time per part
            self.df_wait.loc[len(self.df_wait.index)] = [ID, part, order_size, 1, "begin", self.env.now]
            
            yield request
            
            self.df_wait.loc[len(self.df_wait.index)] = [ID, part, order_size, 1, "end", self.env.now]
            
            #if one machine is broken timeout for the downtime or repairtime
            #after the timeout set the broken variable to False
            if (self.broken[0] > 0) and (prio == 1):
                if self.broken_typ[0] == "downtime":
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"begin", self.machines[0].count, self.env.now]
                    #print(f"Downtime at stage 1 at {self.env.now}")
                    yield self.env.timeout(random.normalvariate(self.machine_downtime[0], 50))
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"leave", self.machines[0].count, self.env.now]
                    self.broken[0] -= 1
                    return
                if self.broken_typ[0] == "changeover":
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"begin", self.machines[0].count, self.env.now]
                    #print(f"Changeovertime at stage 1 at {self.env.now}")
                    yield self.env.timeout(random.normalvariate(self.machine_CO[0], 5))
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"leave", self.machines[0].count, self.env.now]
                    self.broken[0] -= 1
                    return
                if self.broken_typ[0] == "Chaos":
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"begin", self.machines[0].count, self.env.now]
                    yield self.env.timeout(repair_time())
                    self.broken[0] -= 1
                    #print(f"The end of CE on process 1 at {self.env.now}")
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"leave", self.machines[0].count, self.env.now]
                    return
                
            
            #calculate the normal production time and wait it
            self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"begin", self.machines[0].count, self.env.now]
            production_time = random.normalvariate(self.machine_times[0], self.machine_std[0])
            yield self.env.timeout(production_time)
            #print(f"part {part} of {order_size} finished on stage 1 for order {ID} at {env.now}")
            #print(f"{self.machines[0].count} of {self.machines[0].capacity} are used")
            
            #save data in the dataframe
            self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 1,"leave", self.machines[0].count, self.env.now]
            
            #start the store process
            self.env.process(self.store(part, order_size, ID, prio))
            
            
    def store(self, part, order_size, ID, prio):
        #put part into the storage 
        yield self.storage.put(1)
        #print(f"part {part} of {order_size} put in storage for order {ID} at {env.now}")
        #print(f"storage contains {self.storage.level} parts with capacity {self.storage.capacity}")
        self.df_storage.loc[len(self.df_storage.index)] = [self.storage.level, self.env.now] #save data
        
        
       
        
    def prod_process2(self, part, order_size, ID, prio):
        #get the part from the storage
            

        #request any machine of production stage 1
        #break processes have higher priority than orders        
        with self.machines[1].request(priority=prio) as request:
            
            #save data to calculate the waiting time per part
            self.df_wait.loc[len(self.df_wait.index)] = [ID, part, order_size, 2, "begin", self.env.now]
            yield request 
            
            self.df_wait.loc[len(self.df_wait.index)] = [ID, part, order_size, 2, "end", self.env.now]
            
            
            
            
            
            #if one machine is broken timeout for the downtime or repairtime
            #after the timeout set the broken variable to False
            if (self.broken[2] > 0) and (prio == 1):
                if self.broken_typ[2] == "downtime":
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"begin", self.machines[1].count, self.env.now]
                    #print(f"Downtime at stage 2 at {self.env.now}")
                    yield self.env.timeout(random.normalvariate(self.machine_downtime[1],50))
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"leave", self.machines[1].count, self.env.now]
                    self.broken[2] -= 1
                    return
                if self.broken_typ[2] == "changeover":
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"begin", self.machines[1].count, self.env.now]
                    #print(f"Changeovertime at stage 2 at {self.env.now}")
                    yield self.env.timeout(random.normalvariate(self.machine_CO[1],5))
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"leave", self.machines[1].count, self.env.now]
                    self.broken[2] -= 1
                    return
                if self.broken_typ[2] == "Chaos":
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"begin", self.machines[1].count, self.env.now]
                    yield self.env.timeout(repair_time())
                    self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"leave", self.machines[1].count, self.env.now]
                    #print(f"The end of CE on process 2 at {self.env.now}")
                    self.broken[2] -= 1
                    return
                
            
            
            yield self.storage.get(1)
            #print(f"storage contains {self.storage.level} parts with capacity {self.storage.capacity}")
            self.df_storage.loc[len(self.df_storage.index)] = [self.storage.level, self.env.now] #save data
            
            yield self.env.timeout(5) #transport time
            
            
            #calculate the normal production time and wait it
            self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"begin", self.machines[1].count, self.env.now]
            production_time = random.normalvariate(self.machine_times[1], self.machine_std[1])
            yield self.env.timeout(production_time)
            #print(f"part {part} of {order_size} finished on stage 2 for order {ID} at {env.now}")
            #print(f"{self.machines[1].count} of {self.machines[1].capacity} are used")
            self.df_prod.loc[len(self.df_prod.index)] = [ID, part, order_size, 2,"leave", self.machines[1].count, self.env.now]
        
         
    def downtime_stage1(self):
        #function to activate and calculate the downtime
        #print("downtime aktivated")
        while True:
            #downtime repeats in an interval
            timebetween_downtime = random.normalvariate(17000, 500)
            yield self.env.timeout(timebetween_downtime)
            if self.broken[0] < 3:
                self.broken_typ[0] = "downtime"
                self.broken[0] += 1
                #trigger process with higher priority
                self.env.process(self.prod_process1(1, 1, "ID 99999", 1))
               
                                  
    def downtime_stage2(self):
        #function to activate and calculate the downtime
        #print("downtime aktivated")
        while True:
            #downtime repeats in an interval
            timebetween_downtime = random.normalvariate(20000, 500)
            yield self.env.timeout(timebetween_downtime)
            if self.broken[2] < 3:
                self.broken_typ[2] = "downtime"
                self.broken[2] += 1
                #trigger process with higher priority
                self.env.process(self.prod_process2(1, 1, "ID 99999", 1)) 
    
                
    def changeover_stage1(self):
        #function to activate and calculate the changeover
        #print("changeover activated")
        while True:
            timebetween_co = random.normalvariate(6000, 100)
            yield self.env.timeout(timebetween_co)
            #print("changeover process is 1")
            if self.broken[0] < 3:
                self.broken_typ[0] = "changeover"
                self.broken[0] += 1
                #trigger process with higher priority
                self.env.process(self.prod_process1(1,1, "ID 99999", 1))
                   
                                    
    def changeover_stage2(self):
        #function to activate and calculate the changeover
        #print("changeover activated")
        while True:
            timebetween_co = random.normalvariate(8000, 100)
            yield self.env.timeout(timebetween_co)
            #print(f"changeover process is {2}")
            if self.broken[2] < 3:
                self.broken_typ[2] = "changeover"
                self.broken[2] += 1
                #trigger process with higher priority
                self.env.process(self.prod_process2(1,1, "ID 99999", 1))
                   
        
    def break_process(self):
        #function to break the process with failure injection
        #print("machine break activated")
        while True:
            #determine the time to failure
            yield self.env.timeout(time_to_failure())
            
            #determine the process to fail
            #process 0 is the first production process; process 1 is the storage; process 2 is the seccond porduktion process
            process_number = random.randint(0,2)
            #process_number = 2
            #print(f"Start breaking the process {process_number} at {self.env.now}")
            
            match process_number:
                case 0:
                    if self.broken[0] < 3:
                        self.broken_typ[0] = "Chaos"
                        self.broken[0] += 1
                        self.env.process(self.prod_process1(1, 1, "ID 99999", 1))
                case 1:
                    if self.broken[0] < 1:
                        self.broken_typ[1] = "Chaos"
                        self.broken[1] += 1
                        self.env.process(self.source("ID 99999", 1, 1))
                        self.env.process(self.production_control("ID 99999", 1, 1))
                case 2:
                    if self.broken[2] < 3:
                          self.broken_typ[2] = "Chaos"
                          self.broken[2] += 1
                          self.env.process(self.prod_process2(1, 1, "ID 99999", 1))
                case _:
                   return "Something wrong with CE"
            break
                        
                        
            
def order(env, ID, order_size, sf):
    
    #create an order with priority 2
    #print("%s order with order size %d arrives at %.2f." %(ID, order_size, env.now))
    priority = 2
    
    #start the processes that give the information about the order to the production process 1 and 2
    #functions need ID (string), order_size (int) and the priority (always 2)
    yield env.process(sf.source(ID, order_size, priority))
    yield env.process(sf.production_control(ID, order_size, priority))
     
     
                                        
def setup(env, sf):
    
    print("Start der Simulation")
    
    #create the orders with random variables 
    i = 0
    while True:
       
        order_size = 1
        #starts process to create an order with information about the order size 
        env.process(order(env,f'ID {i:05d}', order_size, sf))
        yield env.timeout(20)
        i += 1

#define global Variables to set up the Shopfloor
N_MACHINE = [3, 3] #number of machines per stage
MACHINE_TIME = [35, 40] #mean production time per machine
MACHINE_STD = [5, 2] #std for production time per machine
MACHINE_DOWNTIME = [1500, 1000] #downtime per machine per day for each stage
MACHINE_CO = [120, 100] #changeover time per hour for each stage
STORAGE_CAPACITY = 50 #capacity of the storage
STORAGE_INIT = 25 #amout of parts in the storage at the beginning


def run_simulation(sim_time, seed_value):
    
    #set up the Environment
    env = simpy.Environment()
    
    # create the Shopfloor
    shopfloor = ShopFloor(env, N_MACHINE, MACHINE_TIME, MACHINE_STD,
                 MACHINE_DOWNTIME, MACHINE_CO, STORAGE_CAPACITY, STORAGE_INIT)
    
    env.process(shopfloor.changeover_stage1())
    env.process(shopfloor.changeover_stage2())
    env.process(shopfloor.downtime_stage1())
    env.process(shopfloor.downtime_stage2())
    
    #start the process that initially breaks processes in the Chaos Experiments
    #if the run should occur without CE comment(#) the row below
    env.process(shopfloor.break_process())
    
    env.process(setup(env, shopfloor))
    
    
    #run the simultion until the end of the simulation time is triggered
    #define the simulation time and the seed value
    SIM_TIME = sim_time
    RANDOM_SEED = seed_value
    random.seed(RANDOM_SEED)
    env.run(until= SIM_TIME)
    
    return shopfloor.df_prod, shopfloor.df_wait, shopfloor.df_storage

def experiment_start(sim_time, replication):
    df_production, df_waiting, df_storage = run_simulation(sim_time, replication)
    return  df_waiting, df_production, df_storage
    
