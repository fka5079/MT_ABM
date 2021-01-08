"""

Agent Based Modelling code
Version 2
Assembling Furniture (bookshelf)

"""

import random
from random import randint
import numpy as np
#import pandas as pd
#from matplotlib import pyplot as plt

class Worker:
     
    num_workers = 0
    
    def __init__(self, ID, stature, BMI, experience, riskatt, selfeff,):
        self.ID = ID
        self.stature = stature  # Stature in mm
        self.BMI = BMI
        self.experience = experience  # Amount of relavant experience
        self.riskatt = riskatt  # Risk Attitude
        self.selfeff = selfeff  # Self Efficacy
        
        Worker.num_workers += 1

class Task:
    
    attempt = 0
    #attempts = []
    errorcount = 0
    
    # Status Key
    stat_complete = 4
    stat_error_falsepos = 3
    stat_error_dependent = 2
    stat_error = 1
    stat_default = 0
            
    def __init__(self, DSM, bookshelf, errprob):
        self.DSM = DSM
        self.bookshelf = bookshelf
        self.errprob = errprob
        
        self.steps = len(self.DSM) - 1
        
        error = [0, 1]
        
        for step in range(1, self.steps + 1):
            
            self.part = f'part{step}'
        
            # Error detection
            self.errdetect = randint(0, 1)
        
            # Probability of false positive occuring (should be dependent on self efficacy or risk attitude)
            falsepos = [0, 1]
            falsepos_prob = 0.01
            self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob), falsepos_prob), k=1 )
            
            # Reset counters
            Task.attempt = 0
            Task.errorcount = 0
            
            print(f"Attempting Step{step}.")
            Task.attempt += 1
            # Error in current step based on error probabiliy specified for step
            self.error = random.choices( error, weights = ((1-self.errprob[step - 1]), self.errprob[step - 1]), k=1 )
            
            # If no error occurs -> mark step 2 as complete
            if self.error[0] == 0 and self.falsepositive[0] == 0:
                self.bookshelf[self.part] = Task.stat_complete
                print(f"Step{step} was completed with no errors in " + str(Task.attempt) + " attempt.")

            # If no error occurs and false positive occurs -> increase in number of attempts
            elif self.error[0] == 0 and self.falsepositive[0] > 0:
                while self.falsepositive[0] > 0:
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                    Task.attempt += 1
                self.bookshelf[self.part] = Task.stat_error_falsepos
                print(f"Step{step} was completed in " + str(Task.attempt) + " attempts. Attempt counter increased due to false positive.")
            
            # If error occurs and is not detected -> mark part as incomplete along with all connected parts
            elif self.error[0] > 0 and self.errdetect == 0:
                # List of connected parts:
                depend = []
                for x in range(1, len(self.DSM)):
                    if self.DSM[step, x] == "1":
                        depend.append(self.DSM[0, x])
                # Identify connected parts after current step:
                try: # If there are post-dependent steps
                    depend_post = []
                    for x, part in enumerate(depend):
                        if part == self.part:
                            depend_post.append(depend[x : len(depend)])
                    depend_post = depend_post[0]
                    for x, part in enumerate(depend_post):
                        self.bookshelf[self.part] = Task.stat_error
                        self.bookshelf[part] = Task.stat_error_dependent
                    Task.errorcount += 1
                    print(f"Step{step} completed with un-detected error in " + str(Task.attempt) + " attempt.")
                except:
                    # Last step has no post dependent steps
                    Task.errorcount += 1
                    print(f"Step{step} completed with un-detected error in " + str(Task.attempt) + " attempt.")
                
            # If error occurs and is detected -> try to solve until no error (add to attempt and error count each time)
            # Assuming error in current step can only be solved if error in previous connected steps is solved
            elif self.error[0] > 0 and self.errdetect > 0:
                print(f"Error was detected in Step{step}.")
                
                # Create list of parts connected to current step:
                depend = []
                for y in range(1, len(self.DSM)):
                    if self.DSM[step, y] == "1":
                        depend.append(self.DSM[0, y])
                # Identify connected parts prior to current step:
                depend_pre = []
                for part in depend:
                    if part == self.part:
                        depend_pre.append(depend[0 : step - 1])
                # Identify connected parts after current step:        
                depend_post = []
                for x, part in enumerate(depend):
                    if part == self.part:
                        depend_post.append(depend[x : len(depend)])
                depend_post = depend_post[0]
                        
                try:
                    # For each preceeding step dependent on part:
                    for x, part in enumerate(depend_pre):
                        
                        # If there are no previous errors in connected parts, attempt current step until solved:
                        if self.bookshelf[part[x]] == Task.stat_complete:
                            while self.error[0] > 0:
                                self.error = random.choices( error, weights = (( 1 - self.errprob[step - 1]/2 ), self.errprob[step - 1]/2), k=1 )
                                Task.attempt += 1
                                Task.errorcount += 1
                            self.bookshelf[self.part] = Task.stat_complete
                            print(f"No previous errors. Step{step} completed in " + str(Task.attempt) + " attempts.")
                        
                        # If there is an error in preceding steps:    
                        elif self.bookshelf[part[x]] == Task.stat_error:
                            self.preverrdetect = randint(0, 1)
                            
                            # If error is not detected in preceding step, current step will be attempted but cannot be solved
                            if self.preverrdetect == 0:
                                Task.attempt += 2
                                Task.errorcount += 2
                                try:
                                    for part in depend_post:
                                        self.bookshelf[part] = Task.stat_error_dependent
                                        self.bookshelf[self.part] = Task.stat_error
                                except:
                                    # When on last step, there won't be any post dependent steps
                                    pass
                                print(f"Error in previous steps was not detected. Step{step} was re-attempted " + str(Task.attempt) + " times, but not completed.")
                                    
                            # If error in previous step is detected:
                            elif self.preverrdetect == 1:
                                prev_step = int(part[x][4])
                                print(f"Error detected in {part[x]}. Reattempting step{prev_step}.")
                                part_error = random.choices( error, weights = (( 1 - self.errprob[prev_step - 1]/2), self.errprob[prev_step - 1]/2), k=1 )
                                reattempts[prev_step-1] += 1
                                
                                # If previous step is completed without any errors:
                                if part_error == 0:
                                    self.bookshelf[part[x]] = Task.stat_complete
                                    # Create list of parts connected to previous erraneous part
                                    depend_ = []
                                    for y in range(1, len(self.DSM)):
                                        if self.DSM[prev_step, y] == "1":
                                            depend_.append(self.DSM[0, y])
                                    for item in depend_:
                                        self.bookshelf[item] = Task.stat_default
                                        self.bookshelf[part[x]] = Task.stat_complete
                                    print(f"Step{prev_step} solved with no new errors.")
                                
                                # If previous step is completed with error again:
                                elif part_error == 1:
                                    # Solve until there is no error
                                    while part_error == 1:
                                        part_error = random.choices( error, weights = ((1 - self.errprob[prev_step - 1]/2), self.errprob[prev_step - 1]/2), k=1 )
                                        reattempts[prev_step-1] += 1
                                        # Create list of parts connected to previous erraneous part
                                    depend_ = []
                                    for y in range(len(self.DSM)):
                                        if self.DSM[step, y] == "1":
                                            depend_.append(self.DSM[0, y])
                                    for item in depend_:
                                        self.bookshelf[item] = Task.stat_default
                                    print(f"Step{prev_step} solved. Reattempting step{step}.")
                                
                                # Reattempt current step
                                while self.error == 1:
                                    self.error = random.choices( error, weights = (( 1 - self.errprob[1]/2 ), self.errprob[1]/2), k=1 )
                                    Task.attempt += 1
                                    Task.errorcount += 1
                                self.bookshelf[self.part] = Task.stat_complete
                                print(f"Step{step} was completed in " + str(Task.attempt) + " attempts.")
                        
                except:
                    while self.error == 1:
                        self.error = random.choices( error, weights = (( 1 - self.errprob[1]/2 ), self.errprob[1]/2), k=1 )
                        Task.attempt += 1
                        Task.errorcount += 1
                    self.bookshelf[self.part] = Task.stat_complete
                    print(f"Step{step} was completed in " + str(Task.attempt) + " attempts.")
                    
            print(self.bookshelf)              
            
            attempts.append(int(Task.attempt))
            error_list.append(int(Task.errorcount))
                
# Initiating class

DM_T = ['', 'part1', 'part2', 'part3', 'part4', 'part5', 'part6', 'part7', 'part8', 'part9']
DM_1 = ['part1', 1, 1, 0, 0, 0, 1, 0, 0, 0]
DM_2 = ['part2', 1, 1, 1, 1, 1, 0, 1, 1, 1]
DM_3 = ['part3', 0, 1, 1, 0, 0, 1, 0, 0, 0]
DM_4 = ['part4', 0, 1, 0, 1, 0, 1, 0, 0, 0]
DM_5 = ['part5', 0, 1, 0, 0, 1, 1, 0, 0, 0]
DM_6 = ['part6', 1, 0, 1, 1, 1, 1, 1, 1, 1]
DM_7 = ['part7', 0, 1, 0, 0, 0, 1, 1, 0, 0]
DM_8 = ['part8', 0, 1, 0, 0, 0, 1, 0, 1, 0]
DM_9 = ['part9', 0, 1, 0, 0, 0, 1, 0, 0, 1]
DM_mat = np.matrix([DM_T, DM_1, DM_2, DM_3, DM_4, DM_5, DM_6, DM_7, DM_8, DM_9])

bookshelf = { "part1":0, "part2":0, "part3":0, "part4":0, "part5":0, 
                  "part6":0, "part7":0, "part8":0, "part9":0 }

# Should be dependent on task and worker
errprob = [0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99]

attempts_mat = np.empty((0, len(DM_mat)-1), int)

attempts = []
reattempts = [0,0,0,0,0,0,0,0,0]
error_list = []
Tasks = Task(DM_mat, bookshelf, errprob)

# Run 50x
#k = 0
#while k < 50:
#    attempts = []
#    reattempts = [0,0,0,0,0,0,0,0,0]
#    error_list = []
#    Tasks = Task(DM_mat, bookshelf, errprob)
#    attempts_mat = np.append(attempts_mat, np.array([attempts]), axis=0)
#    reattempts_mat = np.append(reattempts_mat, np.array([reattempts]), axis=0)
#    error_list_mat = np.append(error_list_mat, np.array([error_list]), axis=0)
#    k += 1
    
#attempts_df = pd.DataFrame(attempts_mat)
#reattempts_df = pd.DataFrame(reattempts_mat)
#error_list_df = pd.DataFrame(error_list_mat)
#attempts_df.to_csv('Number_of_Attempts.csv')
#reattempts_df.to_csv('Number_of_ReAttempts.csv')
#error_list_df.to_csv('Number_of_Errors.csv')