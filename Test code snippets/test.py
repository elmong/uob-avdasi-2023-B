from bokeh.models import  ColumnDataSource, Legend, CustomJS, Select
from bokeh.plotting import figure
from bokeh.palettes import Category10
from bokeh.layouts import row
import pandas as pd
from bokeh.server.server import Server


def server_params(doc):
    #function that allows for server to open?
    select = Select(title="Option:", value="foo", options=["foo", "bar", "baz", "quux"])
    select.js_on_change("value", CustomJS(code="""console.log('select: value=' + this.value, this.toString())"""))
    
def open_server():
    #actually opens server
    server = Server({'/': server_params}, num_procs=1)
    server.start()
    
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()




