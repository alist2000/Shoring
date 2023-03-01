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


def plotter_load(depth_final, sigma_final, embedment_depth, active_pressure, passive_pressure, surcharge_pressure, Th,
                 h1, water_active, water_passive, total_depth, x_title, y_title,
                 unit_system):
    if unit_system == "us":
        x_unit = "lb/ft"
        y_unit = "ft"
        point_load = "lb"
    else:
        x_unit = "N/m"
        y_unit = "m"
        point_load = "N"

    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["rgba(242, 87, 87, 0.7)"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top", "tickfont": {"size": 16},
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True, "tickfont": {"size": 16},
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

    plot.add_scatter(x=surcharge_pressure, y=depth_final, showlegend=False,
                     marker=dict(color='rgba(255, 178, 107, 0.5)'))

    j = int((len(depth_final) - 1) / 5)
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
        arrowcolor="rgba(242, 87, 87,1)", )
    )
    list_of_all_arrows = [arrow0]
    for i in range(1, 6):
        arrow = go.layout.Annotation(dict(
            x=0.01,
            y=depth_final[j * i],
            xref="x", yref="y",
            text="",
            showarrow=True,
            axref="x", ayref='y',
            ax=sigma_final[j * i],
            ay=depth_final[j * i],
            arrowhead=3,
            arrowwidth=1.5,
            arrowcolor="rgba(242, 87, 87,1)", )
        )
        list_of_all_arrows.append(arrow)

    # list_of_all_arrows = [arrow0, arrow1, arrow2, arrow3, arrow4, arrow5]
    # plot.update_layout(annotations=list_of_all_arrows)

    plot.update_layout(title_text='Load Diagram', title_y=0.96)

    plot.add_scatter(x=active_pressure, y=embedment_depth + depth_final[-1], showlegend=False,
                     marker=dict(color='rgba(242, 146, 29, 0.6)'))
    plot.add_scatter(x=-passive_pressure, y=embedment_depth + depth_final[-1], showlegend=False,
                     marker=dict(color='rgba(242, 146, 29, 0.6)'))

    plot.add_scatter(x=water_active, y=total_depth, showlegend=False,
                     marker=dict(color='rgba(70, 194, 203, 0.5)'))
    plot.add_scatter(x=-water_passive, y=total_depth, showlegend=False,
                     marker=dict(color='rgba(70, 194, 203, 0.5)'))

    plot.update_traces(hovertemplate="<br>".join(["Pressure: %{x}", "Z: %{y}"]),
                       name="")  # this part could be better! size and color.

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=True,
                               name="Trapezoidal Pressure",
                               fillcolor="rgba(242, 87, 87, 0.4)", marker=dict(color="rgba(242, 87, 87,0.9)")
                               ))

    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=surcharge_pressure, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=True,
                               name="Surcharge Pressure",
                               fillcolor="rgba(255, 212, 212, 0.5)", marker=dict(color="rgba(255, 212, 212, 0.5)")
                               ))

    zero_list = []
    for i in range(len(active_pressure)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=embedment_depth + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=active_pressure, y=embedment_depth + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=True,
                               name="Soil Pressure - active",
                               fillcolor="rgba(255, 178, 107, 0.4)", line_color='rgba(255, 178, 107,1)'
                               ))

    zero_list = []
    for i in range(len(passive_pressure)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=embedment_depth + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=-passive_pressure, y=embedment_depth + depth_final[-1],
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=True,
                               name="Soil Pressure - passive",
                               fillcolor="rgba(255, 178, 107, 0.4)", line_color='rgba(255, 178, 107,1)'
                               ))

    zero_list = []
    for i in range(len(water_active)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=total_depth,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=water_active, y=total_depth,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=True,
                               name="Water pressure - active",
                               fillcolor="rgba(70, 194, 203, 0.2)", line_color="#969696"
                               ))
    zero_list = []
    for i in range(len(water_passive)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=total_depth,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=-water_passive, y=total_depth,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=True,
                               name="Water pressure - passive",
                               fillcolor="rgba(70, 194, 203, 0.2)", line_color="#969696"
                               ))

    j = int((len(embedment_depth) - 1) / 3)
    arrow6 = go.layout.Annotation(dict(
        x=0.01,
        y=embedment_depth[0] + depth_final[-1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=active_pressure[0],
        ay=embedment_depth[0] + depth_final[-1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#F2921D', )
    )
    list_of_all_arrows.append(arrow6)
    for i in range(1, 4):
        arrow = go.layout.Annotation(dict(
            x=0.01,
            y=embedment_depth[j * i] + depth_final[-1],
            xref="x", yref="y",
            text="",
            showarrow=True,
            axref="x", ayref='y',
            ax=active_pressure[j * i],
            ay=embedment_depth[j * i] + depth_final[-1],
            arrowhead=3,
            arrowwidth=1.5,
            arrowcolor='#F2921D', )
        )

        arrow1 = go.layout.Annotation(dict(
            x=0.01,
            y=embedment_depth[j * i] + depth_final[-1],
            xref="x", yref="y",
            text="",
            showarrow=True,
            axref="x", ayref='y',
            ax=-passive_pressure[j * i],
            ay=embedment_depth[j * i] + depth_final[-1],
            arrowhead=3,
            arrowwidth=1.5,
            arrowcolor='#F2921D', )
        )

        list_of_all_arrows.append(arrow)
        list_of_all_arrows.append(arrow1)

    j = int((len(total_depth) - 1) / 5)

    for i in range(6):
        arrow_water = go.layout.Annotation(dict(
            x=0.01,
            y=total_depth[i * j],
            xref="x", yref="y",
            text="",
            showarrow=True,
            axref="x", ayref='y',
            ax=water_active[i * j],
            ay=total_depth[i * j],
            arrowhead=3,
            arrowwidth=1.5,
            arrowcolor="rgba(70, 194, 203, 1)", )
        )
        list_of_all_arrows.append(arrow_water)

    j = int((len(embedment_depth) - 1) / 3)
    if type(Th) == list or type(Th) == np.ndarray:
        # for multi anchor
        for i in range(len(Th)):
            arrow_T = go.layout.Annotation(dict(
                x=0.1,
                y=sum(h1[:i + 1]),
                xref="x", yref="y",
                text="",
                showarrow=True,
                axref="x", ayref='y',
                ax=-active_pressure[2 * j],
                ay=sum(h1[:i + 1]),
                arrowhead=5,
                arrowwidth=4,
                arrowcolor='#595959', )
            )
            list_of_all_arrows.append(arrow_T)


    else:
        arrow_T = go.layout.Annotation(dict(
            x=0.1,
            y=h1[0],
            xref="x", yref="y",
            text="",
            showarrow=True,
            axref="x", ayref='y',
            ax=-active_pressure[2 * j],
            ay=h1[0],
            arrowhead=5,
            arrowwidth=4,
            arrowcolor='#595959', )
        )
        list_of_all_arrows.append(arrow_T)

        plot.add_annotation(dict(font=dict(color="#595959", size=16),
                                 # x=x_loc,
                                 x=-active_pressure[2 * j] * 18 / 20,
                                 y=12 * h1[0] / 13,
                                 showarrow=False,
                                 text=f'<b>{round(Th, 1)} {point_load}</b>',
                                 textangle=0
                                 # xref="x",
                                 # yref="paper"
                                 ))

    plot.update_layout(annotations=list_of_all_arrows)

    # NOTE annotation must be added after arrows to show all arrows.
    if type(Th) == list or type(Th) == np.ndarray:
        for i in range(len(Th)):
            plot.add_annotation(dict(font=dict(color="#595959", size=16),
                                     # x=x_loc,
                                     x=-active_pressure[2 * j] * 18 / 20,
                                     # this value can define better to look good in output.
                                     y=12 * sum(h1[:i + 1]) / 13,
                                     # this value can define better to look good in output.
                                     showarrow=False,
                                     text=f'<b>{round(Th[i], 1)} {point_load}</b>',
                                     textangle=0
                                     # xref="x",
                                     # yref="paper"
                                     ))

    # plot.update_layout(annotations=list_of_all_arrows_new, )

    # plot.add_scatter(x=[i for i in range(10)], y=[j for j in range(10, 20)])

    # plot.write_html("load.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


def plotter_load_result(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top", "tickfont": {"size": 16},
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True, "tickfont": {"size": 16},
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

    j = int((len(depth_final) - 1) / 5)
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
    list_of_all_arrows = [arrow0, arrow1, arrow2, arrow3, arrow4, arrow5]
    plot.update_layout(annotations=list_of_all_arrows)

    plot.update_layout(title_text='Load Diagram', title_y=0.96)

    # plot.write_html("output.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


def plotter_shear(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top", "tickfont": {"size": 16},
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True, "tickfont": {"size": 16},
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

    plot.update_traces(hovertemplate="<br>".join(["V: %{x}", "Z: %{y}"]),
                       name="")  # this part could be better! size and color.

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(152, 193, 217, 0.7)"
                               ))

    plot.update_layout(title_text='Shear Diagram', title_y=0.96)

    # plot.write_html("output.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


def plotter_moment(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top", "tickfont": {"size": 16},
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True, "tickfont": {"size": 16},
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

    plot.update_traces(hovertemplate="<br>".join(["M: %{x}", "Z: %{y}"]),
                       name="")  # this part could be better! size and color.

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(93, 211, 158, 0.7)"
                               ))

    plot.update_layout(title_text='Moment Diagram', title_y=0.96)

    # plot.write_html("moment.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


def plotter_deflection(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top", "tickfont": {"size": 16},
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True, "tickfont": {"size": 16},
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

    plot.update_traces(hovertemplate="<br>".join(["Δ: %{x}", "Z: %{y}"]),
                       name="")

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(247, 200, 224, 0.5)"
                               ))
    # this part could be better! size and color.

    # plot.write_html("output1.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot
