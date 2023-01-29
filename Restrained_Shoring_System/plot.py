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


def plotter_load(depth_final, sigma_final, embedment_depht, active_pressure, passive_pressure, x_title, y_title, x_unit,
                 y_unit):
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

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(242, 87, 87, 0.7)"
                               ))

    j = int(len(depth_final) / 5)
    arrow0 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[0],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[0],
        ay=depth_final[0],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )

    arrow1 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[j],
        ay=depth_final[j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow2 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[2 * j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[2 * j],
        ay=depth_final[2 * j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow3 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[3 * j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[3 * j],
        ay=depth_final[3 * j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow4 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[4 * j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[4 * j],
        ay=depth_final[4 * j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow5 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[5 * j - 1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[5 * j - 1],
        ay=depth_final[5 * j - 1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    # list_of_all_arrows = [arrow0, arrow1, arrow2, arrow3, arrow4, arrow5]
    # plot.update_layout(annotations=list_of_all_arrows)

    plot.update_layout(title_text='Load Diagram', title_y=0.96)

    plot.add_scatter(x=active_pressure, y=embedment_depht + depth_final[-1], showlegend=False)
    plot.add_scatter(x=-passive_pressure, y=embedment_depht + depth_final[-1], showlegend=False)
    plot.update_traces(hovertemplate="<br>".join(["Pressure: %{x}", "Z: %{y}"]),
                       name="")  # this part could be better! size and color.

    zero_list = []
    for i in range(len(active_pressure)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=embedment_depht + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=active_pressure, y=embedment_depht + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(242, 87, 87, 0.7)"
                               ))

    zero_list = []
    for i in range(len(passive_pressure)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=embedment_depht + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=-passive_pressure, y=embedment_depht + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(242, 87, 87, 0.7)"
                               ))

    j = int(len(embedment_depht) / 5)
    arrow6 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[0] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=active_pressure[0],
        ay=embedment_depht[0] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )

    arrow7 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=active_pressure[j],
        ay=embedment_depht[j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow8 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[2 * j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=active_pressure[2 * j],
        ay=embedment_depht[2 * j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow9 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[3 * j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=active_pressure[3 * j],
        ay=embedment_depht[3 * j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow10 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[4 * j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=active_pressure[4 * j],
        ay=embedment_depht[4 * j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow11 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[5 * j - 1] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=active_pressure[5 * j - 1],
        ay=embedment_depht[5 * j - 1] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )

    arrow12 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=-passive_pressure[j],
        ay=embedment_depht[j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow13 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[2 * j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=-passive_pressure[2 * j],
        ay=embedment_depht[2 * j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow14 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[3 * j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=-passive_pressure[3 * j],
        ay=embedment_depht[3 * j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow15 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[4 * j] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=-passive_pressure[4 * j],
        ay=embedment_depht[4 * j] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow16 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depht[5 * j - 1] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=-passive_pressure[5 * j - 1],
        ay=embedment_depht[5 * j - 1] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    list_of_all_arrows = [arrow0, arrow1, arrow2, arrow3, arrow4, arrow5, arrow6, arrow7, arrow8, arrow9, arrow10,
                          arrow11, arrow12, arrow13, arrow14,
                          arrow15, arrow16]
    plot.update_layout(annotations=list_of_all_arrows)

    # plot.add_scatter(x=[i for i in range(10)], y=[j for j in range(10, 20)])

    # plot.write_html("output.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    plot.show()
    return plot
