"""

Agent Based Modelling code
Version 1
Assembling Furniture (bookshelf)

"""

import random
from random import randint

class Worker:
    
    num_workers = 0
    
    def __init__(self, ID, stature, selfeff):
        self.ID = ID
        self.stature = stature  # Stature in cm
        self.selfeff = selfeff
        
        Worker.num_workers += 1
        
worker_1 = Worker(1, 160, 30)
    
class Task:
    
    # Current state of bookshelf
    bookshelf = { "part1":0, "part2":0, "part3":0, "part4":0, "part5":0 }
    error = [0, 1]
    
    def __init__(self):
        pass
        
    @classmethod    
    # Place part 1 flat on ground
    def step1(self, errprob):
        
        # Probability of error occuring
        self.errprob = errprob
        
        # Weighted generation of error based on error probability
        self.err = random.choices( Task.error, weights = ((1-self.errprob), 
                                                          self.errprob), k=1 )
        
        # Error detection
        self.errdetect = randint(0, 1)
        
        # Updating bookshelf status
        if self.err == 0:
            Task.bookshelf["part1"] = 1
        elif self.errdetect == 0:
                Task.bookshelf["part1"] = 0.5
        else:
            while self.err[0] > 0.0:
                newerrprob = self.errprob/2
                self.err = random.choice( Task.error, weights = 
                                         ((1-newerrprob), newerrprob), k=1 )
            Task.bookshelf["part1"] = 1


    @classmethod
    # Place Part 2 or 3 with finished edge facing the same side as Part 1
    def step2(self, errprob):
        
        # Probability of error occuring
        self.errprob = errprob
        
        # Weighted generation of errorbased on error probability
        self.err = random.choices( Task.error, weights = ((1-self.errprob),
                                                          self.errprob), k=1 )
        
        # Error detection
        self.errdetect = randint(0, 1)
        
        #Updating bookshelf status
        if self.err == 0:
            Task.bookshelf["part2"] = 1
        elif self.errdetect == 0:
            Task.bookshelf["part2"] = 0.5
        else:
            while self.err > 0:
                newerrprob = self.errprob/2
                self.err = random.choice( Task.error, weights =
                                         ((1 - newerrprob), newerrprob), k=1 )
            
            Task.bookshelf["part2"] = 1
            
            
            
            
            
            
            
            
            
            
                
    
    # Select screw
    def step3(self, status):
            self.status = status

    # screw in screw hole a
    def step4(self, status):
            self.status = status
                
    # Screw in screw hole b
    def step5(self, status):
            self.status = status
            
    # Place Part 2 or 3 with finished edge facing same side as Part 1
    def step6(self, status):
            self.status = status
    
    # Use the same screw as Step 3
    def step7(self, status):
            self.status = status
    
    # Screw in screw hole a
    def step8(self, status):
            self.status = status

    # Screw in screw hole b
    def step9(self, status):
            self.status = status
    
    # Place Part 4 in between Parts 2 and 3 with finished edge facing same side as Part 1
    def step10(self, status):
            self.status = status

    # Use the same screw as Step 3
    def step11(self, status):
            self.status = status

    # Screw in screw c on Part 3
    def step12(self, status):
            self.status = status
            
    # Screw in screw d on Part 3
    def step13(self, status):
            self.status = status
            
    # Screw in screw c on Part 4
    def step14(self, status):
            self.status = status

    # Screw in screw d on Part 3
    def step15(self, status):
            self.status = status
