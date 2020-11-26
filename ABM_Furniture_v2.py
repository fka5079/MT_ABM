"""

Agent Based Modelling code
Version 2
Assembling Furniture (bookshelf)

"""

import random
from random import randint
import numpy as np

class Worker:
    
    num_workers = 0
    
    def __init__(self, ID, stature, BMI, selfeff, experience, riskatt):
        self.ID = ID
        self.stature = stature  # Stature in mm
        self.BMI = BMI
        self.selfeff = selfeff  # Self Efficacy
        self.experience = experience  # Amount of relavant experience
        self.riskatt = riskatt  # Risk Attitude
        
        Worker.num_workers += 1

class Task:
    
    DM_T = ['', 'part1', 'part2', 'part3', 'part4', 'part5']
    DM_1 = ['part1', 1, 1, 1, 0, 1]
    DM_2 = ['part2', 1, 1, 0, 1, 0]
    DM_3 = ['part3', 1, 0, 1, 1, 0]
    DM_4 = ['part4', 0, 1, 1, 1, 1]
    DM_5 = ['part5', 1, 0, 0, 1, 1]
    DM_mat = np.matrix([DM_T, DM_1, DM_2, DM_3, DM_4, DM_5])
    
    bookshelf = { "part1":0, "part2":0, "part3":0, "part4":0, "part5":0 }
    attempt = 0
    errorcount = 0
            
    def __init__(self, step, errprob, part):
        self.step = step
        self.errprob = errprob
        self.part = part
        
        error = [0, 1]

        # Error detection
        self.errdetect = randint(0, 1)
        
        # Probability of false positive occuring (should be dependent on self efficacy or risk attitude)
        falsepos = [0, 1]
        falsepos_prob = 0.01
        self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob), falsepos_prob), k=1 )

        # Error handling for Step 1:
        # Select and place part 1 with finished edge faacing forward
        if self.step == 1:
            
            print("Attempting Step 1.")
            Task.attempt += 1
            # Error occurance based on error probability specified for step
            self.error = random.choices( error, weights = ((1 - self.errprob[self.step - 1]), self.errprob[self.step - 1]), k=1 )
            
            # If no error occurs in step1 -> mark task as complete in dict
            if self.error[0] == 0 and self.falsepositive[0] == 0:
                Task.bookshelf[self.part] = 1
                print("Step 1 was completed with no errors in " + str(Task.attempt) + " attempt.")
                    
            # If no error occurs and false positive occurs -> increase in number of attempts
            elif self.error[0] == 0 and self.falsepositive[0] > 0:
                while self.falsepositive[0] > 0:
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                    Task.attempt += 1
                print("Step 1 was completed in " + str(Task.attempt) + " attempts. Attempts increased due to false positive.")
                Task.bookshelf[self.part] = 1
                
            # If error occurs and is not detected -> mark part as incomplete along with all connected parts
            elif self.error[0] > 0 and self.errdetect == 0:
                # Mark dependent parts as incomplete based on DSM values
                depend = []
                for x in range(len(Task.DM_mat)):
                    if Task.DM_mat[self.step, x] == "1":
                        depend.append(Task.DM_mat[0, x])
                for part in depend:
                    Task.bookshelf[part] = 0.5
                Task.errorcount += 1
                print("Step 1 completed with un-detected error in " + str(Task.attempt) + " attempt.")
            
            # If error occurs and is detected -> try to solve until no error (add to attempt count each time)
            elif self.error[0] > 0 and self.errdetect > 0:
                while self.error[0] > 0:
                    self.error = random.choices( error, weights = (( 1 - self.errprob[self.step - 1]/2 ), self.errprob[self.step - 1]/2), k=1 )
                    Task.attempt += 1
                    Task.errorcount += 1
                Task.bookshelf[self.part] = 1
                print("Error was detected, Step 1 completed in a total of " + str(Task.attempt) + " attempts.")
        


        # Error handling for Step 2:
        elif self.step == 2:
            
            # Reset attempt counter
            Task.attempt = 0
            
            print("Attempting Step 2.")
            Task.attempt += 1
            # Error in step2 based on error probabiliy specified for step
            self.error = random.choices( error, weights = ((1-self.errprob[self.step - 1]), self.errprob[self.step - 1]), k=1 )
            
            # If no error occurs -> mark step 2 as complete
            if self.error[0] == 0 and self.falsepositive[0] == 0:
                Task.bookshelf[self.part] = 1
                print("Step 2 was completed with no errors in " + str(Task.attempt) + " attempt.")

            # If no error occurs and false positive occurs -> increase in number of attempts
            elif self.error[0] == 0 and self.falsepositive[0] > 0:
                while self.falsepositive[0] > 0:
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                    Task.attempt += 1
                Task.bookshelf[self.part] = 1
                print("Step 2 was completed in " + str(Task.attempt) + " attempts. Counter increased due to false positive.")
            
            # If error occurs and is not detected -> mark part as incomplete along with all connected parts
            elif self.error[0] > 0 and self.errdetect == 0:
                # List of connected parts:
                depend = []
                for x in range(len(Task.DM_mat)):
                    if Task.DM_mat[self.step, x] == "1":
                        depend.append(Task.DM_mat[0, x])
                # Identify connected parts after current step:
                depend_post = []
                for part in depend:
                    if part == self.part:
                        depend_post.append(depend[self.step-1:len(depend)])
                for x, part in enumerate(depend_post):
                    Task.bookshelf[self.part] = 0.5
                    Task.bookshelf[part[x]] = 0.5
                Task.errorcount += 1
                print(f"Step {self.step} completed with un-detected error in " + str(Task.attempt) + " attempt.")
                
            # If error occurs and is detected -> try to solve until no error (add to attempt and error count each time)
            # Assuming error in current step can only be solved if error in previous connected steps is solved
            elif self.error[0] > 0 and self.errdetect > 0:
                print("Error was detected in Step 2.")
                
                # Create list of parts connected to current step:
                depend = []
                for y in range(len(Task.DM_mat)):
                    if Task.DM_mat[self.step, y] == "1":
                        depend.append(Task.DM_mat[0, y])
                # Identify connected parts prior to current step:
                depend_pre = []
                for part in depend:
                    if part == self.part:
                        depend_pre.append(depend[0:self.step-1])
                # Identify connected parts after current step:
                depend_post = []
                for part in depend:
                    if part == self.part:
                        depend_post.append(depend[self.step-1:len(depend)])
                
                # For each preceeding step dependent on part:
                for x, part in enumerate(depend_pre):
                    # If there are no previous errors in connected parts, attempt step 2 until solved:
                    if Task.bookshelf[part[x]] == 1:
                        while self.error[0] > 0:
                            self.error = random.choices( error, weights = (( 1 - self.errprob[self.step - 1]/2 ), self.errprob[self.step - 1]/2), k=1 )
                            Task.attempt += 1
                            Task.errorcount += 1
                        Task.bookshelf[self.part] = 1
                        print("No previous errors. Step 2 completed in " + str(Task.attempt) + "attempts.")
                    
                    # If there is an error in preceding steps:    
                    elif Task.bookshelf[part[x]] == 0.5:
                        self.preverrdetect = randint(0, 1)
                        
                        # If error in preceding connected part is not detected:
                        if self.preverrdetect == 0:
                            Task.attempt += 2
                            Task.errorcount += 2
                            for part in depend_post:
                                Task.bookshelf[part[x]] = 0.5
                                Task.bookshelf[self.part] = 0.5
                            print("Error in previous steps was not detected. Step 2 was re-attempted " + str(Task.attempt) + " times, but not completed.")
                                
                        # If error in previous step is detected:
                        elif self.preverrdetect == 1:
                            step = int(part[4])
                            print(f"Error detected in {part}. Reattempting step {step}.")
                            part_error = random.choices( error, weights = (( 1 - self.errprob[step - 1]/2), self.errprob[step - 1]/2), k=1 )
                            # If previous step is completed without any errors:
                            if part_error == 0:
                                Task.bookshelf[part[x]] = 1
                                # Create list of parts connected to previous erraneous part
                                depend_ = []
                                for y in range(len(Task.DM_mat)):
                                    if Task.DM_mat[step, y] == "1":
                                        depend_.append(Task.DM_mat[0, y])
                                for item in depend_:
                                    Task.bookshelf[item] = 0
                                    Task.bookshelf[part[x]] = 1
                                print(f"Step {step} solved with no new errors.")
                            
                            # If previous step is completed with error:
                            elif part_error == 1:
                                while part_error == 1:
                                    part_error = random.choices( error, weights = ((1 - self.errprob[step - 1]/2), self.errprob[step - 1]/2), k=1 )
                                    # Create list of parts connected to previous erraneous part
                                depend_ = []
                                for y in range(len(Task.DM_mat)):
                                    if Task.DM_mat[step, y] == "1":
                                        depend_.append(Task.DM_mat[0, y])
                                for item in depend_:
                                    Task.bookshelf[item] = 0
                                    Task.bookshelf[part[x]] = 1
                                print(f"Step {step} solved. Reattempting step {self.step}.")
                            
                            # Reattempt current step
                            while self.error == 1:
                                self.error = random.choices( error, weights = (( 1 - self.errprob[1]/2 ), self.errprob[1]/2), k=1 )
                                Task.attempt += 1
                                Task.errorcount += 1
                            Task.bookshelf[self.part] = 1
                            print(f"Step {self.step} completed in a total of " + str(Task.attempt) + " attempts.")
                                
                            

        # Error handling for Step 3:
        elif self.step == 3:
            
            # Reset attempt counter
            Task.attempt = 0
            
            print(f"Attempting Step {self.step}.")
            Task.attempt += 1
            # Error in current step based on error probabiliy specified for step
            self.error = random.choices( error, weights = ((1-self.errprob[self.step - 1]), self.errprob[self.step - 1]), k=1 )
            
            # If no error occurs -> mark step 2 as complete
            if self.error[0] == 0 and self.falsepositive[0] == 0:
                Task.bookshelf[self.part] = 1
                print(f"Step {self.step} was completed with no errors in " + str(Task.attempt) + " attempt.")

            # If no error occurs and false positive occurs -> increase in number of attempts
            elif self.error[0] == 0 and self.falsepositive[0] > 0:
                while self.falsepositive[0] > 0:
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                    Task.attempt += 1
                Task.bookshelf[self.part] = 1
                print(f"Step {self.step} was completed in " + str(Task.attempt) + " attempts. Counter increased due to false positive.")
            
            # If error occurs and is not detected -> mark part as incomplete along with all connected parts
            elif self.error[0] > 0 and self.errdetect == 0:
                # List of connected parts:
                depend = []
                for x in range(len(Task.DM_mat)):
                    if Task.DM_mat[self.step, x] == "1":
                        depend.append(Task.DM_mat[0, x])
                # Identify connected parts after current step:
                depend_post = []
                for part in depend:
                    if part == self.part:
                        depend_post.append(depend[self.step-1:len(depend)])
                for x, part in enumerate(depend_post):
                    Task.bookshelf[self.part] = 0.5
                    Task.bookshelf[part[x]] = 0.5
                Task.errorcount += 1
                print(f"Step {self.step} completed with un-detected error in " + str(Task.attempt) + " attempt.")
                
            # If error occurs and is detected -> try to solve until no error (add to attempt and error count each time)
            # Assuming error in current step can only be solved if error in previous connected steps is solved
            elif self.error[0] > 0 and self.errdetect > 0:
                print(f"Error was detected in Step {self.part}.")
                
                # Create list of parts connected to current step:
                depend = []
                for y in range(len(Task.DM_mat)):
                    if Task.DM_mat[self.step, y] == "1":
                        depend.append(Task.DM_mat[0, y])
                # Identify connected parts prior to current step:
                depend_pre = []
                for part in depend:
                    if part == self.part:
                        depend_pre.append(depend[0:self.step-1])
                # Identify connected parts after current step:        
                depend_post = []
                for part in depend:
                    if part == self.part:
                        depend_post.append(depend[self.step-1:len(depend)])
                        
                # For each preceeding step dependent on part:
                for x, part in enumerate(depend_pre):
                    # If there are no previous errors in connected parts, attempt step 2 until solved:
                    if Task.bookshelf[part[x]] == 1:
                        while self.error[0] > 0:
                            self.error = random.choices( error, weights = (( 1 - self.errprob[self.step - 1]/2 ), self.errprob[self.step - 1]/2), k=1 )
                            Task.attempt += 1
                            Task.errorcount += 1
                        Task.bookshelf[self.part] = 1
                        print(f"No previous errors. Step {self.step} completed in " + str(Task.attempt) + "attempts.")
                    
                    # If there is an error in preceding steps:    
                    elif Task.bookshelf[part[x]] == 0.5:
                        self.preverrdetect = randint(0, 1)
                        
                        # If error is not detected in preceding step:
                        if self.preverrdetect == 0:
                            Task.attempt += 2
                            Task.errorcount += 2
                            for part in depend_post:
                                Task.bookshelf[part[x]] = 0.5
                                Task.bookshelf[self.part] = 0.5
                            print(f"Error in previous steps was not detected. Step {self.step} was re-attempted " + str(Task.attempt) + " times, but not completed.")
                                
                        # If error in previous step is detected:
                        elif self.preverrdetect == 1:
                            step = int(part[4])
                            print(f"Error detected in {part}. Reattempting step {step}.")
                            part_error = random.choices( error, weights = (( 1 - self.errprob[step - 1]/2), self.errprob[step - 1]/2), k=1 )
                            # If previous step is completed without any errors:
                            if part_error == 0:
                                Task.bookshelf[part[x]] = 1
                                # Create list of parts connected to previous erraneous part
                                depend_ = []
                                for y in range(len(Task.DM_mat)):
                                    if Task.DM_mat[step, y] == "1":
                                        depend_.append(Task.DM_mat[0, y])
                                for item in depend_:
                                    Task.bookshelf[item] = 0
                                    Task.bookshelf[part[x]] = 1
                                print(f"Step {step} solved with no new errors.")
                            
                            # If previous step is completed with error:
                            elif part_error == 1:
                                while part_error == 1:
                                    part_error = random.choices( error, weights = ((1 - self.errprob[step - 1]/2), self.errprob[step - 1]/2), k=1 )
                                    # Create list of parts connected to previous erraneous part
                                depend_ = []
                                for y in range(len(Task.DM_mat)):
                                    if Task.DM_mat[step, y] == "1":
                                        depend_.append(Task.DM_mat[0, y])
                                for item in depend_:
                                    Task.bookshelf[item] = 0
                                print(f"Step {step} solved. Reattempting step{self.step}.")
                            
                            # Reattempt current step
                            while self.error == 1:
                                self.error = random.choices( error, weights = (( 1 - self.errprob[1]/2 ), self.errprob[1]/2), k=1 )
                                Task.attempt += 1
                                Task.errorcount += 1
                            Task.bookshelf[self.part] = 1
                            print(f"Step {self.step} completed in a total of " + str(Task.attempt) + " attempts.")



        # Error handling for Step 4: 
        elif self.step == 4:
            
            # Reset attempt counter
            Task.attempt = 0
            
            print("Attempting Step 4.")
            Task.attempt += 1
            
            # Error in step 4 based on error probabiliy specified for step
            self.error = random.choices( error, weights = ((1-self.errprob[3]), self.errprob[3]), k=1 )
            
            # If no error occurs -> mark step 4 as complete
            if self.error[0] == 0 and self.falsepositive[0] == 0:
                Task.attempt += 1    
                Task.bookshelf[self.part] = 1
                print("Step 4 was completed with no errors in " + str(Task.attempt) + " attempt.")

            # If no error occurs and false positive occurs -> increase in number of attempts
            elif self.error[0] == 0 and self.falsepositive[0] > 0:
                while self.falsepositive[0] > 0:
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                    Task.attempt += 1
                Task.bookshelf[self.part] = 1
                print("Step 4 was completed in " + str(Task.attempt) + " attempts. Counter increased due to false positive.")
            
            # If error occurs and is not detected -> mark part as incomplete along with all connected parts
            elif self.error[0] > 0 and self.errdetect == 0:
                Task.bookshelf[self.part] = 0.5
                Task.bookshelf['part5'] = 0.5
                print("Step 4 completed with un-detected error in " + str(Task.attempt) + " attempt.")
                
            # If error occurs and is detected -> try to solve until no error (add to attempt count each time)
            # Error in step 4 can be solved only if error in part 2 and 3 is solved
            elif self.error[0] > 0 and self.errdetect > 0:
                print("Error was detected in Step 4.")
                
                # No previous error detected
                if Task.bookshelf[self.part] == 0:
                    while self.error[0] > 0:
                        self.error = random.choices( error, weights = (( 1 - self.errprob[3]/2 ), self.errprob[3]/2), k=1 )
                        Task.attempt += 1
                    Task.bookshelf[self.part] = 1
                    print("Re-attempting Step 4, completed in " + str(Task.attempt) + " attempts.")
                    
                elif Task.bookshelf[self.part] == 0.5:
                    # There was an error in either step 2 or step 3
                    
                    self.preverrdetect2 = randint(0, 1)
                    self.preverrdetect3 = randint(0, 1)
                    
                    # Error in step 2 and step 3 is not detected
                    if self.preverrdetect2 == 0 and self.preverrdetect3 == 0:
                        Task.attempt += 5
                        Task.bookshelf[self.part] = 0.5
                        Task.bookshelf['part5'] = 0.5
                        print("Error in previous steps was not detected. Step 4 was re-attempted " + str(Task.attempt) + " times, but not completed.")
                    
                    # If error in step 2 or step 3 is detected
                    # Error in step 2 detected
                    elif self.preverrdetect2 == 1:
                        print("Error detected in Part 2. Re-attempting Step 2.")
                        part2_error = random.choices( error, weights = ((1 - self.errprob[1]/2), self.errprob[1]/2), k=1 )
                        
                        if part2_error == 0:
                            Task.bookshelf['part2'] = 1
                            Task.attempt += 1
                            print("Step 2 solved with no new errors in " + str(Task.attempt) + " attempts.")
                        
                        else:
                            while part2_error[0] > 0:
                                part2_error = random.choices( error, weights = ((1 - self.errprob[1]/2), self.errprob[1]/2), k=1 )
                                Task.attempt += 1
                            Task.bookshelf['part2'] = 1
                            print("Error encountered in Step 2 again, but solved in " + str(Task.attempt) + " attempts.")
                            
                    # Error in step 3 detected
                    elif self.preverrdetect3 == 1:
                        print("Error detected in Part 3. Re-attempting Step 3.")
                        part3_error = random.choices( error, weights = ((1 - self.errprob[2]/2), self.errprob[2]/2), k=1 )
                        
                        if part3_error == 0:
                            Task.bookshelf['part3'] = 1
                            Task.attempt += 1
                            print("Step 3 solved with no new errors in " + str(Task.attempt) + " attempts.")
                        
                        else:
                            while part3_error[0] > 0:
                                part3_error = random.choices( error, weights = ((1 - self.errprob[2]/2), self.errprob[2]/2), k=1 )
                                Task.attempt += 1
                            Task.bookshelf['part3'] = 1
                            print("Error encountered in Step 3 again, but solved in " + str(Task.attempt) + " attempts.")
                            
                        print("Re-attempting Step 4.")                            
                        while self.error[0] > 0:
                            self.error = random.choices( error, weights = (( 1 - self.errprob[3]/2 ), self.errprob[3]/2), k=1 )
                            Task.attempt += 1
                        Task.bookshelf[self.part] = 1
                        print("Step 4 completed in a total of " + str(Task.attempt) + " attempts.")



        # Error handling for Step 5:
        elif self.step == 5:
            
            # Reset attempt counter
            Task.attempt = 0
            
            print("Attempting Step 5.")
            Task.attempt += 1
            
            # Error in step 5 based on error probabiliy specified for step
            self.error = random.choices( error, weights = ((1-self.errprob[4]), self.errprob[4]), k=1 )
            
            # If no error occurs -> mark step 5 as complete
            if self.error[0] == 0 and self.falsepositive[0] == 0:
                Task.attempt += 1    
                Task.bookshelf[self.part] = 1
                print("Step 5 was completed with no errors in " + str(Task.attempt) + " attempt.")

            # If no error occurs and false positive occurs -> increase in number of attempts
            elif self.error[0] == 0 and self.falsepositive[0] > 0:
                while self.falsepositive[0] > 0:
                    self.falsepositive = random.choices( falsepos, weights = ((1-falsepos_prob/2), falsepos_prob/2), k=1 )
                    Task.attempt += 1
                Task.bookshelf[self.part] = 1
                print("Step 5 was completed in " + str(Task.attempt) + " attempts. Counter increased due to false positive.")
            
            # If error occurs and is not detected -> mark part as incomplete along with all connected parts
            elif self.error[0] > 0 and self.errdetect == 0:
                Task.bookshelf[self.part] = 0.5
                print("Step 5 completed with un-detected error in " + str(Task.attempt) + " attempt.")
                
            # If error occurs and is detected -> try to solve until no error (add to attempt count each time)
            # Error in step 5 can be solved only if errors in part 1 and 4 are solved
            elif self.error[0] > 0 and self.errdetect > 0:
                print("Error was detected in Step 5.")
                
                # No error detected in previous parts
                if Task.bookshelf[self.part] == 0:
                    while self.error[0] > 0:
                        self.error = random.choices( error, weights = (( 1 - self.errprob[4]/2 ), self.errprob[4]/2), k=1 )
                        Task.attempt += 1
                    Task.bookshelf[self.part] = 1
                    print("Re-attempting Step 5, completed in " + str(Task.attempt) + " attempts.")
                    
                elif Task.bookshelf[self.part] == 0.5:
                # There was an error in either step 1 or step 4
                    
                    self.preverrdetect1 = randint(0, 1)
                    self.preverrdetect4 = randint(0, 1)
                    
                    # Error in step 1 and step 4 is not detected
                    if self.preverrdetect1 == 0 and self.preverrdetect4 == 0:
                        Task.attempt += 5
                        Task.bookshelf[self.part] = 0.5
                        print("Error in previous steps was not detected. Step 5 was re-attempted " + str(Task.attempt) + " times, but not completed.")
                    
                    # If error in step 1 or step 4 is detected
                    # Error in step 1 detected
                    elif self.preverrdetect1 == 1:
                        print("Error detected in Part 1. Re-attempting Step 1.")
                        part1_error = random.choices( error, weights = ((1 - self.errprob[0]/2), self.errprob[0]/2), k=1 )
                        
                        if part1_error == 0:
                            Task.bookshelf['part1'] = 1
                            Task.attempt += 1
                            print("Step 1 solved with no new errors in " + str(Task.attempt) + " attempts.")
                        
                        else:
                            while part1_error[0] > 0:
                                part1_error = random.choices( error, weights = ((1 - self.errprob[0]/2), self.errprob[0]/2), k=1 )
                                Task.attempt += 1
                            Task.bookshelf['part1'] = 1
                            print("Error encountered in Step 1 again, but solved in " + str(Task.attempt) + " attempts.")
                            
                    # Error in step 4 detected
                    elif self.preverrdetect4 == 1:
                        print("Error detected in Part 4. Re-attempting Step 4.")
                        part4_error = random.choices( error, weights = ((1 - self.errprob[3]/2), self.errprob[3]/2), k=1 )
                        
                        if part4_error == 0:
                            Task.bookshelf['part4'] = 1
                            Task.attempt += 1
                            print("Step 4 solved with no new errors in " + str(Task.attempt) + " attempts.")
                        
                        else:
                            while part4_error[0] > 0:
                                part4_error = random.choices( error, weights = ((1 - self.errprob[3]/2), self.errprob[3]/2), k=1 )
                                Task.attempt += 1
                            Task.bookshelf['part4'] = 1
                            print("Error encountered in Step 4 again, but solved in " + str(Task.attempt) + " attempts.")
                            
                        print("Re-attempting Step 5.")                            
                        while self.error[0] > 0:
                            self.error = random.choices( error, weights = (( 1 - self.errprob[4]/2 ), self.errprob[4]/2), k=1 )
                            Task.attempt += 1
                        Task.bookshelf[self.part] = 1
                        print("Step 5 completed in a total of " + str(Task.attempt) + " attempts.")
            
            
#k = 0
#while k < 100:
#    Task_step1 = Task('Step1', 0.9, 'part1')
    
   # Task_step2= Task('Step2', 0.9, 'part2')
  #  print(Task.bookshelf)
  #   print(Task.attempt)

#    k += 1

errorprob_mat = [0.99, 0.99, 0.99, 0.99, 0.99]

Task_step1= Task(1, errorprob_mat, 'part1')
print(Task.bookshelf)
Task_step2= Task(2, errorprob_mat, 'part2')
print(Task.bookshelf)
Task_step3= Task(3, errorprob_mat, 'part3')
print(Task.bookshelf)
Task_step4= Task(4, errorprob_mat, 'part4')
print(Task.bookshelf)
Task_step5= Task(5, errorprob_mat, 'part5')
print(Task.bookshelf)