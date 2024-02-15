from global_var import *
from bokeh.models import ColumnDataSource

#this is a class used to store and manipulate the picos' connection and its status
class Dataset:
    
    

    #object instantiation
    def __init__(self,Name,Num_points):
        #assign object attributes
        self.data = [[0],[0]]
        self.name = Name
        self.num_points = Num_points
        self.data_source = None
        

    def __str__(self): #returns object as a string
        return str(str(self.name) + str(self.num_points))

    #dataset handling
    #add a point to the dataset
    def addData(self,x,y):
        #ensure dataset does not contain more points than allowed
        if self.data[0].__len__() >= self.num_points:
            self.data[0].append(x)
            self.data[1].append(y)

            while self.data[0].__len__() >= self.num_points:
                #remove first point
                self.data[0].pop(0)
                self.data[1].pop(0)

        else:
            #just add the new point
            self.data[0].append(x)
            self.data[1].append(y)
        


    #create datasource
    def build_datasource(self):
        self.data_source = ColumnDataSource(data = {"x": self.data[0], "y": self.data[1]})

    def update_datasource(self):
        self.data_source = ColumnDataSource(data = {"x": self.data[0], "y": self.data[1]})