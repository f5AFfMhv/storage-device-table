#!/usr/bin/env python3

# Tutorials: 
# Plotly: https://plotly.com/python/
# Command line arguments: https://www.tutorialspoint.com/python/python_command_line_arguments.htm

# pip install:
#   pandas
#   plotly
#   requests

import plotly.graph_objects as go
import requests
import sys

# Chart data
device = []
used = []
free = []

# Create empty graph object
fig = go.Figure()

def create_graph(BASE_URL, NAME):
    # Get data from API
    r = requests.get(BASE_URL + '?name=' + NAME)
    server = r.json()
    # Parse data to list for ploting
    for dev in server:
        device.append(dev.get('device'))
        free.append(dev.get('free_gb'))
        used.append(dev.get('size_gb') - dev.get('free_gb'))

    # Add data to graph. First used disk space stacked by free disk space
    fig.add_trace(go.Bar(x=device, y=used, name='Used space, GB'))
    fig.add_trace(go.Bar(x=device, y=free, name='Free space, GB'))

    # Format chart representation
    fig.update_layout(title=NAME + " storage devices usage", title_font_color="red", title_font_size=30)
    fig.update_layout(hovermode="x")
    fig.update_layout(legend_title_text = "Storage devices:")
    fig.update_layout(barmode='stack')
    fig.update_xaxes(categoryorder='total ascending')
    fig.update_yaxes(title_text='GB')

    return fig
