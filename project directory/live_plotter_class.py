import sys
import time
import numpy as np
from datetime import datetime
from bokeh.io import output_notebook
from bokeh.plotting import figure
from bokeh.io import show , curdoc
from bokeh.io import push_notebook
from bokeh.models import ColumnDataSource, Legend, CustomJS, Select
from bokeh.server.server import Server 

import dataset_class as dsc
from global_var import control_surfaces

#this is a class to create live data plots easily
class Live_plotter:

    #object instantiation
    def __init__(self,points_stored):
        #assign object attributes
        self.points_stored = points_stored
        self.dataset_list = None
        self.server = None

    def create_datasets(self,name0,name1,name2,name3,name4,name5):
        #creation of dataset objects, stored in a list
        self.dataset_list = [dsc.Dataset(name0,self.points_stored),dsc.Dataset(name1,self.points_stored),dsc.Dataset(name2,self.points_stored),dsc.Dataset(name3,self.points_stored),dsc.Dataset(name4,self.points_stored),dsc.Dataset(name5,self.points_stored)]

        #build datasources
        for item in self.dataset_list:
            item.build_datasource()
    
    def update_data_dictionaries_control_surfaces(self):
        #this function updates each dataset object with control surface angle data
        self.dataset_list[0].addData(np.random.random(),control_surfaces["elevator"]["angle"])
        self.dataset_list[1].addData(np.random.random(),control_surfaces["rudder"]["angle"])
        self.dataset_list[2].addData(np.random.random(),control_surfaces['port_aileron']['angle'])
        self.dataset_list[3].addData(np.random.random(),control_surfaces['port_flap']['angle'])
        self.dataset_list[4].addData(np.random.random(),control_surfaces['starboard_aileron']['angle'])
        self.dataset_list[5].addData(np.random.random(),control_surfaces['starboard_flap']['angle'])

        #update datasources
        for item in self.dataset_list:
            item.update_datasource()

    def declare_figures(self):
        #declares figures and provides a source
        self.figure_list = [figure(),figure(),figure(),figure(),figure(),figure()]

        index = 0
        for fig in self.figure_list:
            fig.line(x="x", y="y", line_color="tomato", line_width=2, source=self.dataset_list[index].data_source)
            index += 1


    def bkapp(self,doc):
        self.declare_figures()

        for fig in self.figure_list:
            show(fig)
        
        
    def ini(self):
        self.server = Server({'/': self.bkapp}, num_procs=1)
        self.server.start()
        print('Opening Bokeh application on http://localhost:5006/')  
        self.server.show("/")
        

    def shutdown(self):
        self.server.stop()
        self.server.io_loop.stop()
