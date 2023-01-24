import copy
import sys
import json

from sympy import symbols
from sympy.solvers import solve
import numpy as np
import scipy.integrate as spi

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Layout


def plotter(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top",
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#969696",
               "zerolinewidth": 4}
    )
    plot['layout']['yaxis']['autorange'] = "reversed"
    layout = Layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    plot.update_layout(layout)
    plot.show()
    return plot
