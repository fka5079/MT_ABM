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
                        # Update deltat due to error that occured during first attempt
                        self.errorintensity = randint(1, 100)
                        # Calculate change in time based on error intensity
                        deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                        deltat_tot.append(deltat)
                        
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
                        # Update deltat due to error that occured during first attempt
                        self.errorintensity = randint(1, 100)
                        # Calculate change in time based on error intensity
                        deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                        deltat_tot.append(deltat)
                            
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
                    # Calculate the intensity of the error
                    self.errorintensity = randint(1, 100)
                    # Calculate change in time based on error intensity
                    deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                    deltat_tot.append(deltat)
                        
                    # A function that is called when a part has a dependency error.
                    def dependency(or_part, depend_prelist, depend_postlist):
                        or_step = int(re.findall("\d+", str(or_part))[0])
                         
                        stat_track = []
                        for x, part_1r in enumerate(depend_prelist):
                            step_1r = int(re.findall("\d+", str(part_1r))[0])  # Gives the number for current pre-dependent step & pep = prev erraneous part
                    
                            depend_1r = []  # List of parts dependent on part_1r
                            for y in range(1, len(self.DSM)):
                                if self.DSM[step_1r, y] == "1":
                                    depend_1r.append(self.DSM[0, y])
                            for x, dep_part in enumerate(depend_1r):
                                if dep_part == part_1r:
                                    # Identify connected parts prior to current step:
                                    depend_pre_1r = depend_1r[0 : x]
                                    # Identify connected parts after current step:        
                                    depend_post_1r = depend_1r[x+1 : len(depend_1r)]
                            
                            # When part_1r has a dependency error
                            if self.bookshelf[part_1r] == Task.stat_error_dependent:
                                # Attempt Part_1r but it cannot be solved until root error is solved.
                                attempts[step_1r - 1] += 1
                                error_list[step_1r - 1] += 1
                                
                                # Update hep of step_1r based on time available for step and current time elapsed.
                                # time[step_1r - 1] = time[or_step - 1] - sum(deltat_tot)
                                # Worker = Workers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)
                                # self.errprob = Worker.hep
                                
                                # Calculate deltat due to error in part_1r.
                                self.errorintensity = randint(1, 100)
                                # Calculate change in time based on error intensity
                                deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                                deltat_tot.append(deltat)
                                
                                print(f"{part_1r} has a dependency error. Checking previous connected parts.")
                                dependency(part_1r, depend_pre_1r, depend_post_1r)
                                
                            # When part_1r has an error
                            elif self.bookshelf[part_1r] == Task.stat_error:
                                                                
                                # There is a chance for whether the error in part_1r is detected or not.
                                self.errdetect_1r = randint(0, 1)
                                
                                # When the error in part_1r is not detected, the original part is re-attempted but cannot be solved.
                                if self.errdetect_1r == 0:
                                    print(f"{part_1r} has an error that was not detected. Attempting next part.")
                                    
                                elif self.errdetect_1r == 1:
                                    print(f"Error found in {part_1r}. Re-attempting {part_1r}.")
                                    attempts[step_1r - 1] += 1
                                    
                                    # Update hep of step_1r based on time available for step minus current time elapsed.
                                    time[step_1r - 1] = time[or_step - 1] - sum(deltat_tot)
                                    Worker = Workers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)
                                    self.errprob = Worker.hep
                                    
                                    self.error_1r = random.choices( error, weights = ((1-self.errprob[step_1r - 1]), self.errprob[step_1r - 1]), k=1 )
                                    
                                    if self.error_1r == 0:
                                        print(f"Error in {part_1r} was solved.")
                                        self.bookshelf[part_1r] == Task.stat_complete
                                        
                                    elif self.error_1r == 1:
                                        print(f"Error reoccured in {part_1r}. Re-attempting {part_1r}.")
                                        error_list[step_1r - 1] += 1
                                        
                                        # Calculate deltat due to error in part_1r.
                                        self.errorintensity = randint(1, 100)
                                        # Calculate change in time based on error intensity
                                        deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                                        deltat_tot.append(deltat)
                                        
                                        # Update hep of step_1r based on time available for step minus current time elapsed.
                                        time[step_1r - 1] = time[or_step - 1] - sum(deltat_tot)
                                        Worker = Workers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)
                                        self.errprob = Worker.hep
                                    
                                        self.error_1r = random.choices( error, weights = ((1-self.errprob[step_1r - 1]), self.errprob[step_1r - 1]), k=1 )
                                        
                                        while self.error_1r == 1:
                                            error_list[step_1r - 1] += 1
                                            attempts[step_1r - 1] += 1
                                            
                                            # Update hep of step_1r based on time available for step minus current time elapsed.
                                            time[step_1r - 1] = time[or_step - 1] - sum(deltat_tot)
                                            Worker = Workers(time, takt_t, stress, complexity, experience, procedures, ergonomics, FOD, process)
                                            self.errprob = Worker.hep
                                    
                                            self.error_1r = random.choices( error, weights = ((1-self.errprob[step_1r - 1]), self.errprob[step_1r - 1]), k=1 )
                                            
                                            # Calculate deltat due to error in part_1r.
                                            self.errorintensity = randint(1, 100)
                                            # Calculate change in time based on error intensity
                                            deltat = self.a * math.exp((-self.errorintensity/self.b) ** self.c)
                                            deltat_tot.append(deltat)
                                        
                                        self.bookshelf[part_1r] = Task.stat_complete
                                        for dep_part in depend_postlist:
                                            if dep_part == or_step:
                                                break
                                            elif dep_part != step:
                                                Attempt(dep_part)
                                        
                            elif self.bookshelf[part_1r] == Task.stat_complete:
                                pass
                            
                            stat_track.append(int(self.bookshelf[part_1r]))
                        
                        stat = [k for k in stat_track if k == 1]
                        if stat in stat_track == 1:
                            
                            
                            
                                    
                                    
                                    
                                    
                                
                            
                                
                        






                        