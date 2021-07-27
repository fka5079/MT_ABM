# Import necessary libraries
import random
from random import randint
import numpy as np
import pandas as pd
import math
from scipy import interpolate
import re

class Task:
    
    def __init__(self, DSM, bookshelf, errprob, a, b, c):
        self.DSM = DSM
        self.bookshelf = bookshelf
        self.errprob = errprob
        self.a = a  # deltat calculation constants
        self.b = b  # deltat calculation constants
        self.c = c  # deltat calculation constants
        self.steps = len(self.DSM) - 1
        
        attempt = 0
        errorcount = 0
        
        # Status Key
        stat_complete = 4
        # stat_error_falsepos = 3
        stat_error_dependent = 2
        stat_error = 1
        stat_default = 0
        
        # A Function that simulates a worker attempting a step.
        def Attempt(partx):
                
            # Some variables and lists to keep track
            error = [0, 1]
            falsepos = [0, 1]
            falsepos_prob = 0.01  # Probability of a false positive error occuring
            deltat_tot = []  # A list that helps sum deltat at the end of a step
            
            for step in range(1, self.steps + 1):
                
                self.part = partx
                # HEP when a step is being reattempted after an error is detected
                recurrant_errprob = self.errprob[step - 1]/2
                
                # Create a list of pre and post dependent parts
                depend = []  # List of all connected parts
                for y in range(1, len(self.DSM)):
                    if self.DSM[step, y] == "1":
                        depend.append(self.DSM[0, y])
                for x, dep_part in enumerate(depend):
                    if dep_part == self.part:
                        # Identify connected parts prior to current step:
                        depend_pre = depend[0 : x]
                        # Identify connected parts after current step:        
                        depend_post = depend[x+1 : len(depend)]
                        
                # Resetting counters to track attempts and errors
                Task.attempt = 0
                Task.errorcount = 0
                
                if self.bookshelf[self.part] == Task.stat_default:
                    
                    print(f"Attempting Step{step}")
                    Task.attempt += 1
                    
                    # Error status in current step based on HEP for part
                    self.error = random.choices( error, weights = ((1-self.errprob[step - 1]), self.errprob[step - 1]), k=1 )
                    
                    # Probability of detecting error
                    self.errdetect = randint(0, 1)
                    
                    # If no error occurs -> mark part as complete
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
                            print("A falsepositive error occured. Part was reattempted.")
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
           
                elif self.bookshelf[self.part] == Task.stat_error_dependent:
                    # Increase error counter because first attempt at step revealed dependency issue
                    Task.errorcount += 1
                    print(f"Dependency error detcted in Step{step}. Checking previous connected parts.")
                    
                    status_track = []
                    for x, part in enumerate(depend_pre):
                        Task.errorcount += 1
                        
                        # Calculate the intensity of the error
                        self.errorintensity = randint(1, 100)
                        # Calculate change in time based on error intensity
                        deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                        deltat_tot.append(deltat)
                        






                        