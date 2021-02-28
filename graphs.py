#!/usr/bin/env python3

"""
This application generates plotly graph object containing host storage bargraph.
Data for bargraph aquired by API call.
For more information how to use API check this project Github page.

Copyright (C) 2021 Martynas J. 
f5AFfMhv@protonmail.com  
https://github.com/f5AFfMhv

Tutorials: 
    Plotly: https://plotly.com/python/
"""

import plotly.graph_objects as go
import requests

class figure:
    def __init__(self, BASE_URL, DEVICE):
        self.url = BASE_URL
        self.dev = DEVICE

        # Graph data
        self.devices = []
        self.used = []
        self.free = []

        # Create empty graph object
        self.fig = go.Figure()

    def create_graph(self):
        # Get data from API
        self.r = requests.get(self.url + '?host=' + self.dev)
        self.server = self.r.json()
        # Parse data to list for ploting
        for self.d in self.server:
            self.devices.append(self.d.get('device'))
            self.free.append(self.d.get('free_mb'))
            self.used.append(self.d.get('size_mb') - self.d.get('free_mb'))

        # Add data to graph.
        self.fig.add_trace(go.Bar(x=self.devices, y=self.used, name='Used space, MB'))
        self.fig.add_trace(go.Bar(x=self.devices, y=self.free, name='Free space, MB'))

        # Format chart representation
        self.fig.update_layout(overwrite=True, title=self.dev + " storage devices usage", title_font_color="red", title_font_size=30)
        self.fig.update_layout(hovermode="x")
        self.fig.update_layout(barmode='stack')
        self.fig.update_xaxes(categoryorder='total ascending')
        self.fig.update_yaxes(title_text='MB')

        return self.fig