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
            
            # Probability of false positive error occuring
            self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob), falsepos_prob), k=1 )
            
            # Create a list of parts that are connected to the current step
            depend = []  # List of all connected parts
            for y in range(1, len(self.DSM)):
                if self.DSM[step, y] == "1":
                    depend.append(self.DSM[0, y])
            # Identify connected parts prior to current step:
            depend_pre = []  # List of prior connected parts
            for part in depend:
                if part == self.part:
                    depend_pre.append(depend[0 : step - 1])
            # Identify connected parts after current step:        
            for x, part in enumerate(depend):
                if part == self.part:
                    depend_post = depend[x : len(depend)]  # List of connected parts after current step
            
            # Reset counters
            Task.attempt = 0
            Task.errorcount = 0
            
            print(f"Attempting Step{step}.")
            Task.attempt += 1
            
            # If there is no dependency error
            if self.bookshelf[self.part] == Task.stat_default:
                
                # Error status in current step based on HEP for step
                self.error = random.choices( error, weights = ((1-self.errprob[step - 1]), self.errprob[step - 1]), k=1 )
                # Probability of detecting error
                self.errdetect = randint(0, 1)
                
                # False positive error status in current step
                self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob), falsepos_prob), k=1 )
                
                # If no error occurs -> mark step as complete
                if self.error[0] == 0 and self.falsepositive[0] == 0:
                    self.bookshelf[self.part] = Task.stat_complete
                    print(f"Step{step} was completed with no errors in " + str(Task.attempt) + " attempt(s).")
                    
                # If no error occurs but a false positive error occurs -> Add to attempt counter
                elif self.error[0] == 0 and self.falsepositive[0] == 1:
                    while self.falsepositive[0] > 0:
                        self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                        Task.attempt += 1
                        Task.errorcount += 1
                    self.bookshelf[self.part] = Task.stat_error_falsepos
                    print(f"Step{step} was completed in " + str(Task.attempt) + " attempt(s). Attempt counter increased due to false positive.")
                
                # If an error occurs but is not detected -> update status of current and all post connected steps
                # Use "try" because the last step in a task will not have any post dependent steps
                elif self.error[0] == 1 and self.errdetect == 0:
                    try:
                        for x, part in enumerate(depend_post):
                            self.bookshelf[self.part] = Task.stat_error
                            self.bookshelf[part] = Task.stat_error_dependent  # Update staus of post connected steps
                        Task.errorcount += 1
                        print(f"Step{step} completed with un-detected error in " + str(Task.attempt) + " attempt(s).")
                    except:
                        # Last step has no post dependent steps -> add to error count and update current step only
                        Task.errorcount += 1
                        self.bookshelf[self.part] = Task.stat_error
                        print(f"Step{step} completed with un-detected error in " + str(Task.attempt) + " attempt(s).")
                
                # If error occurs and is detected -> try to solve until no error (add to attempt and error count each time)
                # Update time multiplier and error probability based on intensity of error
                elif self.error[0] == 1 and self.errdetect == 1:
                    print(f"Error was detected in Step{step}.")
                    # Attempt task until detected error is solved
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
                Task.error += 1
                print(f"Dependency error detcted in Step{self.step}. Checking previous connected steps.")
                
                for x, part in enumerate(depend_pre):
                    X = int(re.findall("\d+", part)[0])  # Gives the number for preceding dependent step
                    
                    # Create list of parts connected to previous erraneous part
                    depend_ = []
                    for y in range(1, len(self.DSM)):
                        if self.DSM[X, y] == "1":
                            depend_.append(self.DSM[0, y])
                    
                    # If error is not detected in preceding part, current step will be attempted but cannot be solved
                    # The current step should also maintain its dependent error status
                    if Task.bookshelf[part] == Task.stat_error:
                        # Probability for whether the preceding error is detected or not
                        self.preverrdetect = randint(0, 1)  # This value can be altered depending on the Worker
                        
                        if self.preverrdetect == 0:
                            Task.attempt += 2
                            Task.errorcount += 2
                            # Mark all dependent parts after current step to have a dependency error
                            # Current step will continue to have a dependency error
                            try:
                                for part in depend_post:
                                    self.bookshelf[part] = Task.stat_error_dependent
                            # When on last step, there won't be any post dependent parts
                            except:
                                pass
                            print(f"Error in previous connected steps was not detected. Step{step} was re-attempted " + str(Task.attempt) + " time(s), but not completed.")
                        
                        # If error in previous part is detected -> Solve previous error then solve current step
                        elif self.preverrdetect == 1:
                            print(f"Error detected in {part[X]}. Reattempting step{X}.")
                            
                            # Reattempt previous connected part until solved
                            reattempts[X-1] += 1
                            part_error = random.choices( error, weights = (( 1 - self.errprob[X - 1]/2), self.errprob[X - 1]/2), k=1 )
                            
                            # If an error occurs in the previous connected part again -> continue to attempt until solved
                            if part_error == 1:
                                Task.errorcount += 1
                                while part_error == 1:
                                    part_error = random.choices( error, weights = (( 1 - self.errprob[X - 1]/2), self.errprob[X - 1]/2), k=1 )
                                    Task.errorcount += 1
                                    reattempts[X-1] += 1
                                    
                            # If an error did not occur in the previous connected part or if error was solved -> Solve current step'
                            
                            # Update status of previous connected part, its post dependent parts, and current step
                                    
                    elif Task.bookshelf[part] == Task.stat_error_dependent:
                        
                        
                
                
                
                
                

