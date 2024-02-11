import sys
import time
import numpy as np
from datetime import datetime
from bokeh.io import output_notebook
from bokeh.plotting import figure ,show , curdoc
from bokeh.io import push_notebook
from bokeh.models import ColumnDataSource, Legend, CustomJS, Select
from bokeh.layouts import row, gridplot,layout
from bokeh.server.server import Server 

import dataset_class as dsc
from global_var import control_surfaces, airplane_data, input_commands

#this is a class to create live data plots easily
class Live_plotter:

    #object instantiation
    def __init__(self,points_stored):
        #assign object attributes
        self.points_stored = points_stored
        self.dataset_list = None
        self.server = None
        self.start_time = time.time()

    def create_datasets(self,name0,name1,name2,name3,name4,name5,name6,name7,name8,name9,name10,name11,name12,name13):
        #creation of dataset objects, stored in a list
        self.dataset_list = [] 
        self.dataset_list.append(dsc.Dataset(name0,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name1,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name2,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name3,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name4,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name5,self.points_stored))

        self.dataset_list.append(dsc.Dataset(name6,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name7,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name8,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name9,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name10,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name11,self.points_stored))
        
        self.dataset_list.append(dsc.Dataset(name12,self.points_stored))
        self.dataset_list.append(dsc.Dataset(name13,self.points_stored))

        #build datasources
        for item in self.dataset_list:
            item.build_datasource()
            
    
    def update_data_dictionaries(self):
        time_now = time.time()
        delta_t = time_now - self.start_time
        #this function updates each dataset object with control surface angle data
        self.dataset_list[0].addData(delta_t,control_surfaces["elevator"]["angle"])
        self.dataset_list[1].addData(delta_t,control_surfaces["rudder"]["angle"])
        self.dataset_list[2].addData(delta_t,control_surfaces['port_aileron']['angle'])
        self.dataset_list[3].addData(delta_t,control_surfaces['port_flap']['angle'])
        self.dataset_list[4].addData(delta_t,control_surfaces['starboard_aileron']['angle'])
        self.dataset_list[5].addData(delta_t,control_surfaces['starboard_flap']['angle'])
        self.dataset_list[6].addData(delta_t,control_surfaces["elevator"]["servo_demand"])
        self.dataset_list[7].addData(delta_t,control_surfaces["rudder"]["servo_demand"])
        self.dataset_list[8].addData(delta_t,control_surfaces['port_aileron']['servo_demand'])
        self.dataset_list[9].addData(delta_t,control_surfaces['port_flap']['servo_demand'])
        self.dataset_list[10].addData(delta_t,control_surfaces['starboard_aileron']['servo_demand'])
        self.dataset_list[11].addData(delta_t,control_surfaces['starboard_flap']['servo_demand'])
        self.dataset_list[12].addData(delta_t,airplane_data["pitch"])
        self.dataset_list[13].addData(delta_t,input_commands["pitch_pid"])
        
        #update datasources
        for item in self.dataset_list:
            item.data_source.stream({"x": item.data[0], "y": item.data[1]},self.points_stored)
        

    def bkapp(self,doc):
        doc.theme = "dark_minimal"
        
        #declares figures and provides a source
        fig1 = figure(x_axis_label="Time [s]", y_axis_label="Deflection [Degrees]",title= "Measured Angular Deflection Of Control Surfaces")
        fig2 = figure(x_axis_label="Time [s]", y_axis_label="Demanded Deflection [Degrees]",title= "Demanded Angular Deflection Of Control Surfaces")
        fig3 = figure(x_axis_label="Time [s]", y_axis_label="Pitch [Degrees]",title= "Demanded and Actual Pitch")

        fig1.line(x="x", y="y",legend_label=self.dataset_list[0].name, line_color="tomato", line_width=(2), source=self.dataset_list[0].data_source)
        fig1.line(x="x", y="y",legend_label=self.dataset_list[1].name, line_color="grey", line_width=(2), source=self.dataset_list[1].data_source)
        fig1.line(x="x", y="y",legend_label=self.dataset_list[2].name, line_color="blue", line_width=(2), source=self.dataset_list[2].data_source)
        fig1.line(x="x", y="y",legend_label=self.dataset_list[3].name, line_color="darkgrey", line_width=(2), source=self.dataset_list[3].data_source)
        fig1.line(x="x", y="y",legend_label=self.dataset_list[4].name, line_color="darkblue", line_width=(2), source=self.dataset_list[4].data_source)
        fig1.line(x="x", y="y",legend_label=self.dataset_list[5].name, line_color="green", line_width=(2), source=self.dataset_list[5].data_source)
        
        fig2.line(x="x", y="y",legend_label=self.dataset_list[6].name, line_color="tomato", line_width=(2), source=self.dataset_list[6].data_source)
        fig2.line(x="x", y="y",legend_label=self.dataset_list[7].name, line_color="grey", line_width=(2), source=self.dataset_list[7].data_source)
        fig2.line(x="x", y="y",legend_label=self.dataset_list[8].name, line_color="blue", line_width=(2), source=self.dataset_list[8].data_source)
        fig2.line(x="x", y="y",legend_label=self.dataset_list[9].name, line_color="darkgrey", line_width=(2), source=self.dataset_list[9].data_source)
        fig2.line(x="x", y="y",legend_label=self.dataset_list[10].name, line_color="darkblue", line_width=(2), source=self.dataset_list[10].data_source)
        fig2.line(x="x", y="y",legend_label=self.dataset_list[11].name, line_color="green", line_width=(2), source=self.dataset_list[11].data_source)

        fig3.line(x="x", y="y",legend_label=self.dataset_list[12].name, line_color="darkblue", line_width=(2), source=self.dataset_list[12].data_source)
        fig3.line(x="x", y="y",legend_label=self.dataset_list[13].name, line_color="green", line_width=(2), source=self.dataset_list[13].data_source)

        fig1.legend.location = "top_left"
        fig1.legend.label_text_font_size = "11px"
        fig1.legend.label_text_line_height = 1
        fig1.legend.label_standoff = 2
        fig1.legend.spacing = 1
        fig1.legend.margin = 1
        fig2.legend.location = "top_left"
        fig2.legend.label_text_font_size = "11px"
        fig2.legend.label_text_line_height = 1
        fig2.legend.label_standoff = 2
        fig2.legend.spacing = 1
        fig2.legend.margin = 1
        fig3.legend.location = "top_left"
        fig3.legend.label_text_font_size = "11px"
        fig3.legend.label_text_line_height = 1
        fig3.legend.label_standoff = 2
        fig3.legend.spacing = 1
        fig3.legend.margin = 1

        doc.add_root(layout(children=[[fig1,fig2],fig3],sizing_mode="scale_both"))
        
        doc.add_periodic_callback(self.update_data_dictionaries,50)
        
            
            
        
        
    def ini(self):
        self.server = Server({'/': self.bkapp}, num_procs=1)
        self.server.start()
        self.server.show("/")
        print('Opening Bokeh application on http://localhost:5006/')  
        

    def shutdown(self):
        self.server.stop()
        self.server.io_loop.stop()
