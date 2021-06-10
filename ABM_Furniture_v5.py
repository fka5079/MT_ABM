"""

Agent Based Modelling code
Version 5
(Add error significance and time)

"""

import random
from random import randint
import numpy as np
import pandas as pd
import math
from scipy import interpolate
#from matplotlib import pyplot as plt

class Worker:
    
    def __init__(self, stature, BMI, gender):
        self.stature = stature  # Stature in mm
        self.BMI = BMI
        self.gender = gender

class Multipliers:
    
    def __init__(self, time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process):
        # Each multiplier will be in the form of a list
        self.time = time
        self.takt_t = takt_t
        self.stress = stress
        self.complexity = complexity
        self.experience = experience
        self.procedures = procedures
        self.ergonomics = ergonomics
        self.FOD = FOD
        self.process = process
        
        self.time_mult = []
        self.hep = []
        
        interp_col1 = np.asarray([self.takt_t, 2*self.takt_t, 5*self.takt_t, 50*self.takt_t])
        interp_col2 = np.asarray([10, 1, 0.1, 0.01])
        for step in range(0, len(DM_mat)-1):
            tck = interpolate.splrep(interp_col1, interp_col2, s=0, k=2)
            self.time_mult.append(interpolate.splev(self.time[step], tck, der=0))
            psf = self.time_mult[step] * self.stress[step] * self.complexity[step] * self.experience[step] * self.procedures[step] * self.ergonomics[step] * self.FOD[step] * self.process[step]
            self.hep.append((0.01 * psf) / (0.01 * (psf - 1) + 1))

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
               
    def __init__(self, DSM, bookshelf, errprob, a, b, c):
        self.DSM = DSM
        self.bookshelf = bookshelf
        self.errprob = errprob
        self.a = a
        self.b = b
        self.c = c
        
        self.steps = len(self.DSM) - 1
        
        error = [0, 1]
        
        deltat_tot = []
        
        for step in range(1, self.steps + 1):
            
            self.part = f'part{step}'
        
            # Likelyhood of detecting error
            self.errdetect = randint(0, 1)
            
            recurrant_errprob = self.errprob[step - 1]/2
        
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
            # # Intensity of error
            # self.errorintensity = randint(1, 100)
            # # Calculate change in time based on error intensity
            # deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
            # deltat_tot.append(deltat)
            
            # If no error occurs -> mark step 2 as complete
            if self.error[0] == 0 and self.falsepositive[0] == 0:
                self.bookshelf[self.part] = Task.stat_complete
                print(f"Step{step} was completed with no errors in " + str(Task.attempt) + " attempt.")

            # If no error occurs and false positive occurs -> increase in number of attempts
            elif self.error[0] == 0 and self.falsepositive[0] > 0:
                while self.falsepositive[0] > 0:
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                    Task.attempt += 1
                    Task.errorcount += 1
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
                            depend_post = depend[x : len(depend)]
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
            # Update time multiplier and hence error probability based on intensity of error
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
                for x, part in enumerate(depend):
                    if part == self.part:
                        depend_post = depend[x : len(depend)]
                        
                try:
                    # For each preceeding step dependent on part:
                    for x, part in enumerate(depend_pre):
                        
                        # If there are no previous errors in connected parts, attempt current step until solved:
                        if self.bookshelf[part[x]] == Task.stat_complete:
                            while self.error[0] > 0:
                                self.error = random.choices( error, weights = (( 1 - recurrant_errprob ),recurrant_errprob), k=1 )
                                # Calculate the intensity of the new error
                                self.errorintensity = randint(1, 100)
                                # Calculate change in time based on error intensity
                                deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                                deltat_tot.append(deltat)
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
                                    self.error = random.choices( error, weights = (( 1 - recurrant_errprob ), recurrant_errprob), k=1 )
                                    # Calculate the intensity of the new error
                                    self.errorintensity = randint(1, 100)
                                    # Calculate change in time based on error intensity
                                    deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                                    deltat_tot.append(deltat)
                                    Task.attempt += 1
                                    Task.errorcount += 1
                                self.bookshelf[self.part] = Task.stat_complete
                                print(f"Step{step} was completed in " + str(Task.attempt) + " attempts.")
                        
                except: # If there are no preceding steps
                    while self.error == 1:
                        self.error = random.choices( error, weights = (( 1 - recurrant_errprob ), recurrant_errprob), k=1 )
                        # Calculate the intensity of the new error
                        self.errorintensity = randint(1, 100)
                        # Calculate change in time based on error intensity
                        deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                        deltat_tot.append(deltat)
                        Task.attempt += 1
                        Task.errorcount += 1
                    self.bookshelf[self.part] = Task.stat_complete
                    print(f"Step{step} was completed in " + str(Task.attempt) + " attempts.")
            
            print(f"Step{step} complete.")
            print(self.bookshelf)              
            
            attempts.append(int(Task.attempt))
            error_list.append(int(Task.errorcount))
            
            # Add all delta_t values saved for this step
            # This constant gives the total change in time that will affect the next step and can be used to calculate new available time
            deltat_sum = sum(deltat_tot)
            # Update the time input for multiplier class; this works for all steps except the last step
            try:
                time[step] -= deltat_sum     # Subtract time lost in error from next step
            except:
                pass
            # Use the new time list and call the multiplier class again to update HEP list
            Multiplier = Multipliers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)
            errprob = Multiplier.hep
            
            

# Initiating class
DSM = pd.read_csv("cotton candy machine_DSM.csv", header = None)
DM_mat = np.matrix(DSM)

bookshelf = { "part1":0, "part2":0, "part3":0, "part4":0, "part5":0, 
                  "part6":0, "part7":0, "part8":0, "part9":0, "part10":0, 
                  "part11":0, "part12":0, "part13":0, "part14":0, "part15":0, 
                  "part16":0, "part17":0, "part18":0, "part19":0, "part20":0 }

# Call Multipliers class and define values for each multiplier for each step within the task
# Input by user/shift supervisor
time = []  # Available time for each task
takt_t = 25
stress = []
complexity = []
experience = []
procedures = []
ergonomics = []
FOD = []
process = []

# Use following for loop to automatically fill a list with identical multiplier values
# This portion can be updated to include a list with different values
for item in range(0, len(DM_mat)-1):
    time.append(30)
    stress.append(1)
    complexity.append(2)
    experience.append(0.5)
    procedures.append(1)
    ergonomics.append(1)
    FOD.append(1)
    process.append(1)
    
Multiplier = Multipliers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)

# Errprob should be dependent on multipliers
#errprob = [0.17, 0.08, 0.42, 0.08, 0.42, 0.17, 0.17, 0.17, 0.08, 0.08, 0.17, 0.42, 0.08, 0.17, 0.08, 0.08, 0.17, 0.08, 0.08, 0.17, 0.17, 0.08, 0.42, 0.08, 0.42, 0.17, 0.17, 0.17, 0.08, 0.08, 0.17, 0.42, 0.08, 0.17, 0.08, 0.08, 0.17]
errprob = Multiplier.hep

#Worker = Worker(1600, 24, 'male', 1.0, 2.0, 0.1, 2.0, 0.5, 1.0, 0.5, 1.0)

# Create empty matrices that can be appended for results
attempts_mat = np.empty((0, len(DM_mat)-1), int)
reattempts_mat = np.empty((0, len(DM_mat)-1), int)
error_list_mat = np.empty((0, len(DM_mat)-1), int)

#attempts = []
#reattempts = [0,0,0,0,0,0,0,0,0]
#error_list = []
#Tasks = Task(DM_mat, bookshelf, errprob)

# Run 100x
k = 0
# Constants for deltat calculation
a = 0.5
b = 10     # scale parameter
c = 3      # shape parameter
while k < 50:
    attempts = []
    reattempts = []
    m = 0
    while m < len(DM_mat) - 1:
        reattempts.append(0)
        m += 1
    error_list = []
    Tasks = Task(DM_mat, bookshelf, errprob, a, b, c)
    
    attempts_mat = np.append(attempts_mat, np.array([attempts]), axis=0)
    reattempts_mat = np.append(reattempts_mat, np.array([reattempts]), axis=0)
    error_list_mat = np.append(error_list_mat, np.array([error_list]), axis=0)
    print(f"Iteration {k+1} completed.")
    k += 1
    
attempts_df = pd.DataFrame(attempts_mat)
reattempts_df = pd.DataFrame(reattempts_mat)
error_list_df = pd.DataFrame(error_list_mat)
attempts_df.to_csv('Number_of_Attempts.csv')
reattempts_df.to_csv('Number_of_ReAttempts.csv')
error_list_df.to_csv('Number_of_Errors.csv')