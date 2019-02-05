# You need to learn a function with n inputs.
# For given number of inputs, we will generate random function.
# Your task is to learn it
import time
import random
import torch
import torchvision
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from ..utils import solutionmanager as sm
from ..utils import gridsearch as GridSearch

class SolutionModel(nn.Module):
    def __init__(self, input_size, output_size, solution):
        super(SolutionModel, self).__init__()
        self.input_size = input_size
        sm.SolutionManager.print_hint("Hint[1]: Explore more deep neural networks")
        self.solution = solution
        self.hidden_size = self.solution.hidden_size
        if solution.grid_search.enabled:
            torch.manual_seed(solution.random)
        self.fc1 = nn.Linear(input_size, self.hidden_size)
        self.fc2 = nn.Linear(self.hidden_size, self.hidden_size)
        self.fc3 = nn.Linear(self.hidden_size, output_size)
        self.fcS = nn.Sequential(
                                nn.Linear(input_size, self.hidden_size),
                                nn.ReLU(),
                                nn.Dropout(0.2),
                                nn.Linear(self.hidden_size, output_size)) 
        self.fcR = nn.Hardtanh(-1, 1)
        
    def forward(self, x):

                ###################################################################################x = F.rrelu(self.fc1(x))
        x = x.view(x.size(0), -1)        
                
        x = F.softmax(self.fc1(x), dim = 1)
        
        #x = F.dropout(x, training=self.training)
        #x = F.sigmoid(self.fc2(x))
        
        #x = F.dropout(x, training=self.training)
        
        #x = F.sigmoid(self.fcR(x))

        return F.sigmoid(self.fc3(x))

class Solution():
    def __init__(self):
        self = self
        self.learning_rate = 1.0
        self.lr = 5
        self.lr_grid = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
        self.hidden_size_grid = [3, 5, 7, 11]
        self.hidden_size = 7
        self.grid_search = GridSearch.GridSearch(self).set_enabled(False)

    def create_model(self, input_size, output_size):
        return SolutionModel(input_size, output_size, self)      ######################################### add activation func here

    # Return number of steps used
    def train_model(self, model, train_data, train_target, context):
        step = 0
        # Put model in train mode
        model.train()
        while True:
            time_left = context.get_timer().get_time_left()
            # No more time left, stop training
            if time_left < 0.1:
                break
            optimizer = optim.SGD(model.parameters(), lr=self.learning_rate)
            data = train_data
            target = train_target
            # model.parameters()...gradient set to zero
            optimizer.zero_grad()
            # evaluate model => model.forward(data)
            sm.SolutionManager.print_hint("Hint[2]: Explore other activation functions", step)
            output = model(data)
            # if x < 0.5 predict 0 else predict 1
            predict = output.round()
            # Number of correct predictions
            correct = predict.eq(target.view_as(predict)).long().sum().item()
            # Total number of needed predictions
            total = target.view(-1).size(0)
            if correct == total:
                break
            # calculate loss
            sm.SolutionManager.print_hint("Hint[3]: Explore other loss functions", step)
            loss = ((output-target)**2).sum()
            # calculate deriviative of model.forward() and put it in model.parameters()...gradient
            loss.backward()
            # print progress of the learning
            self.print_stats(step, loss, correct, total)
            # update model: model.parameters() -= lr * gradient
            optimizer.step()
            step += 1
        return step
    
    def print_stats(self, step, loss, correct, total):
        if step % 1000 == 0:
            print("Step = {} Prediction = {}/{} Error = {}".format(step, correct, total, loss.item()))

###
###
### Don't change code after this line
###
###
class Limits:
    def __init__(self):
        self.time_limit = 2.0
        self.size_limit = 10000
        self.test_limit = 1.0

class DataProvider:
    def __init__(self):
        self.number_of_cases = 10

    def create_data(self, input_size, seed):
        random.seed(seed)
        data_size = 1 << input_size
        data = torch.FloatTensor(data_size, input_size)
        target = torch.FloatTensor(data_size)
        for i in range(data_size):
            for j in range(input_size):
                input_bit = (i>>j)&1
                data[i,j] = float(input_bit)
            target[i] = float(random.randint(0, 1))
        return (data, target.view(-1, 1))

    def create_case_data(self, case):
        input_size = min(3+case, 7)
        data, target = self.create_data(input_size, case)
        return sm.CaseData(case, Limits(), (data, target), (data, target)).set_description("{} inputs".format(input_size))


class Config:
    def __init__(self):
        self.max_samples = 1000

    def get_data_provider(self):
        return DataProvider()

    def get_solution(self):
        return Solution()

# If you want to run specific case, put number here
sm.SolutionManager(Config()).run(case_number=-1)
