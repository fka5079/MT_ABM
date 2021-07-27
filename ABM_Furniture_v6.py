# -*- coding: utf-8 -*-
"""
Agent Based Modelling code
Version 6
(Fix foundation error)

@author: Fariha

"""

# Import necessary libraries
import random
from random import randint
import numpy as np
import pandas as pd
import math
from scipy import interpolate
import re

class Workers:
    
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
        tck = interpolate.splrep(interp_col1, interp_col2, s=0, k=3)
        for step in range(0, len(DM_mat)-1):
            self.time_mult.append(interpolate.splev(self.time[step], tck, der=0))
            psf = self.time_mult[step] * self.stress[step] * self.complexity[step] * self.experience[step] * self.procedures[step] * self.ergonomics[step] * self.FOD[step] * self.process[step]
            self.hep.append((0.01 * psf) / (0.01 * (psf - 1) + 1))
            
class Task:
    
    attempt = 0
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
        falsepos = [0, 1]
        falsepos_prob = 0.01  # Probability of a false positive error occuring
        
        deltat_tot = []
        
        for step in range(1, self.steps + 1):
            
            self.part = f'part{step}'
            # HEP when a step is being reattempted after an error is detected
            recurrant_errprob = self.errprob[step - 1]/2
            
            # Create a list of parts that are connected to the current step
            depend = []  # List of all connected parts
            for y in range(1, len(self.DSM)):
                if self.DSM[step, y] == "1":
                    depend.append(self.DSM[0, y])
            for x, part in enumerate(depend):
                if part == self.part:
                    # Identify connected parts prior to current step:
                    depend_pre = depend[0 : x]
                    # Identify connected parts after current step:        
                    depend_post = depend[x+1 : len(depend)]
            
            # Reset counters
            ArithmeticError(args)Task.attempt = 0
            Task.errorcount = 0
            
            print(f"Attempting Step{step}.")
            Task.attempt += 1
            
            # If there is no dependency error
            if self.bookshelf[self.part] == Task.stat_default:
                
                # Error status in current step based on HEP for step
                self.error = random.choices( error, weights = ((1-self.errprob[step - 1]), self.errprob[step - 1]), k=1 )
                # Probability of detecting error
                self.errdetect = randint(0, 1)
                
                # If no error occurs -> mark step as complete
                if self.error[0] == 0:
                    self.bookshelf[self.part] = Task.stat_complete
                    print(f"Step{step} was completed with no errors in " + str(Task.attempt) + " attempt(s).")
                
                # If an error occurs but is not detected -> update status of current and all post connected steps
                # Use "try" because the last step in a task will not have any post dependent steps
                elif self.error[0] == 1 and self.errdetect == 0:
                    Task.errorcount += 1
                    try:
                        for x, dep_part in enumerate(depend_post):
                            self.bookshelf[dep_part] = Task.stat_error_dependent  # Update staus of post connected steps
                        print(f"Step{step} completed with un-detected error in " + str(Task.attempt) + " attempt(s).")
                    except:
                        # Last step has no post dependent steps -> add to error count and update current step only
                        print(f"Step{step} completed with un-detected error in " + str(Task.attempt) + " attempt(s).")
                    self.bookshelf[self.part] = Task.stat_error
                    
                # If error occurs and is detected -> try to solve until no error (add to attempt and error count each time)
                # Update time multiplier and error probability based on intensity of error
                elif self.error[0] == 1 and self.errdetect == 1:
                    Task.errorcount += 1
                    
                    # Possibility that the error that occured is a false positive
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob), falsepos_prob), k=1 )
                    
                    if self.falsepositive == 1:
                        print("A falsepositive error occured. Part was reattempted and then solved")
                        Task.attempt += 1
                        
                    elif self.falsepositive == 0:
                        # Calculate the intensity of the error
                        self.errorintensity = randint(1, 100)
                        # Calculate change in time based on error intensity
                        deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                        deltat_tot.append(deltat)
                        print(f"Error was detected in Step{step}.")
                        # Re-attempt task until detected error is solved
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
                    print(f"Step{step} was completed in " + str(Task.attempt) + " attempt(s).")
                    
            # Error in current task cannot be solved if there is an unsolved error in a preceding dependent part
            # This if statement will not be activated if there are no errors in preceding connected parts
            elif self.bookshelf[self.part] == Task.stat_error_dependent:
                # Increase error counter because first attempt at step revealed dependency issue
                Task.errorcount += 1
                print(f"Dependency error detcted in Step{step}. Checking previous connected steps.")
                
                status_track = []
                for x, part in enumerate(depend_pre):
                    # Calculate the intensity of the error
                    self.errorintensity = randint(1, 100)
                    # Calculate change in time based on error intensity
                    deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                    deltat_tot.append(deltat)
                                        
                    def dependency(pep):
                        X = int(re.findall("\d+", str(pep))[0])  # Gives the number for current pre-dependent step & pep = prev erraneous part
                        
                        depend_ = []  # List of all connected parts
                        for y in range(1, len(self.DSM)):
                            if self.DSM[X, y] == "1":
                                depend_.append(self.DSM[0, y])
                        for x, pre_dep_part in enumerate(depend_):
                            if pre_dep_part == pep:
                                # Identify connected parts prior to current step:
                                depend_pre_ = depend_[0 : x]
                                # Identify connected parts after current step:        
                                depend_post_ = depend_[x+1 : len(depend_)]
                        
                        status_track_ = []
                        for part__ in depend_pre_:
                            X_ = int(re.findall("\d+", part__)[0])  # Gives the number for current pre-pre-dependent step
                            
                            if self.bookshelf[part__] == Task.stat_error_dependent:
                                for dep_part in depend_pre_:
                                    dependency(dep_part)
                                
                            elif self.bookshelf[part__] == Task.stat_error:
                                # Randomize error detection in previous step
                                self.errdetect_ = randint(0, 1)
                                if self.errdetect_ == 0:
                                    # Add 2 attempts to original part
                                    # Status of current pre-dependent step will remain = 1 and of current step will remain = 2
                                    print(f"Previous error in {part__} was not detected.")
                                elif self.errdetect_ == 1:
                                    print(f"Error in {part__} was detected.")
                                    # Recalculate errprob based on new deltat
                                    self.error__ = random.choices( error, weights = (( 1 - self.errprob[X_ - 1]/2 ), self.errprob[X_ - 1]/2), k=1 )
                                    # Task.reattempt += 1
                                    # error_list[X_ - 1] += 1
                                    # Calculate the intensity of the error
                                    self.errorintensity = randint(1, 100)
                                    # Calculate change in time based on error intensity
                                    deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                                    deltat_tot.append(deltat)
                                    while self.error__ == 1:
                                        self.error__ = random.choices( error, weights = (( 1 - self.errprob[X_ - 1]/2 ), self.errprob[X_ - 1]/2), k=1 )
                                        # Task.reattempt += 1
                                        # error_list[X_ - 1] += 1
                                        # Calculate the intensity of the error
                                        self.errorintensity = randint(1, 100)
                                        # Calculate change in time based on error intensity
                                        deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                                        deltat_tot.append(deltat)
                                    for dep_part in depend_post_:
                                        self.bookshelf[dep_part] = Task.stat_default
                                    
                            elif self.bookshelf[part__] == Task.stat_complete:
                                pass
                            
                            status_track_.append(self.bookshelf[part__])
                            
                        # Solve pep if all pre dependent steps have been solved
                        stat_counter_ = sum(status_track_) * (len(depend_pre_) + 1)
                        if stat_counter_ == Task.stat_complete * (len(depend_pre_) + 1):
                            # solve pep
                            self.error_ = random.choices( error, weights = (( 1 - self.errprob[X - 1]/2 ), self.errprob[X - 1]/2), k=1 )
                            # Task.reattempt += 1
                            # error_list[X_ - 1] += 1
                            while self.error_ == 1:
                                self.error_ = random.choices( error, weights = (( 1 - self.errprob[X - 1]/2 ), self.errprob[X - 1]/2), k=1 )
                                # Task.reattempt += 1
                                # error_list[X_ - 1] += 1
                            self.bookshelf[pep] = Task.stat_complete                            
                    
                    dependency(part)
                    print(part)
                    print(self.bookshelf[part])
                    status_track.append(self.bookshelf[part])
                
                stat_counter = sum(status_track) * (len(depend_pre) + 1)
                if stat_counter == Task.stat_complete * (len(depend_pre) + 1):
                    # solve part
                    self.error = random.choices( error, weights = (( 1 - recurrant_errprob ), recurrant_errprob), k=1 )
                    Task.attempt += 1
                    Task.errorcount += 1
                    while self.error_ == 1:
                        self.error = random.choices( error, weights = (( 1 - recurrant_errprob ), recurrant_errprob), k=1 )
                        Task.errorcount += 1
                        Task.attempt +=1
                    self.bookshelf[part] = Task.stat_complete
                else:
                    Task.attempt += 2  # There is a dependency error in the current step that cannot be solved
                    print(f"Step{step} cannot be solved due to a previous error that was not detected.")
                        
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
            Worker = Workers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)
            errprob = Worker.hep

# Initiating class
DSM = pd.read_csv("cotton candy machine_DSM.csv", header = None)
DM_mat = np.matrix(DSM)

# Replace header row and column with part numbers
parts = ['']
for part in range(1, len(DM_mat)):
    parts.append(f"part{part}")
DM_mat[0] = parts
DM_mat[:,0] = np.asarray([parts]).T

bookshelf = { "part1":0, "part2":0, "part3":0, "part4":0, "part5":0, 
                  "part6":0, "part7":0, "part8":0, "part9":0, "part10":0, 
                  "part11":0, "part12":0, "part13":0, "part14":0, "part15":0, 
                  "part16":0, "part17":0, "part18":0, "part19":0, "part20":0,
                  "part21":0, "part22":0, "part23":0,  "part24":0, "part25":0, "part26":0,
                  "part27":0, "part28":0, "part29":0, "part30":0, "part31":0,
                  "part32":0, "part33":0, "part34":0, "part35":0, "part36":0}

# Call Multipliers class and define values for each multiplier for each step within the task
# Input by user/shift supervisor
time = []  # Available time for each task
takt_t = 25  # Time needed for each task
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
    time.append(35)
    stress.append(1)
    complexity.append(2)
    experience.append(0.5)
    procedures.append(1)
    ergonomics.append(1)
    FOD.append(1)
    process.append(1)
    
Worker = Workers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)
# Errprob should be dependent on multipliers
errprob = Worker.hep

# Create empty matrices that can be appended for results
attempts_mat = np.empty((0, len(DM_mat)-1), int)
reattempts_mat = np.empty((0, len(DM_mat)-1), int)
error_list_mat = np.empty((0, len(DM_mat)-1), int)

# Run 100x
k = 0
# Constants for deltat calculation
a = 1
b = 50     # scale parameter
c = 1      # shape parameter
while k < 1:
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
    print(bookshelf)
    print(f"Iteration {k+1} completed.")
    k += 1
    
attempts_df = pd.DataFrame(attempts_mat)
reattempts_df = pd.DataFrame(reattempts_mat)
error_list_df = pd.DataFrame(error_list_mat)
attempts_df.to_csv('Number_of_Attempts.csv')
reattempts_df.to_csv('Number_of_ReAttempts.csv')
error_list_df.to_csv('Number_of_Errors.csv')