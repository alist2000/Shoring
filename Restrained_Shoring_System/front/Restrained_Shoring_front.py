# max_general_plot = 3
# general_plot = []
# for i in range(max_general_plot):
#     general_plot.append(open(f"../plot/general_output{i + 1}.html", "r").read())


def generate_html_response_restrained_shoring(titles, values):
    # otitle = titles[0]
    # header_general = titles[1]
    # header_specific = titles[2]
    # excel_names = titles[3]

    max_general_plot = 3
    general_plot = []
    for i in range(max_general_plot):
        general_plot.append(f"https://civision.balafan.com/unrestrained_shoring/plot/general_output{i + 1}")
        # general_plot.append(
        #     open(f"/app/app/Shoring/Unrestrained_Shoring_System/soldier_pile/plot/general_output{i + 1}.html",
        #          "r").read())

    general_values = values[0]
    specific_values = values[1]

    max_specific_plot = len(specific_values)  # this value can be changed according to site inputs
    specific_plot = []
    for i in range(max_specific_plot):
        # specific_plot.append(
        #     open(f"/app/app/Shoring/Unrestrained_Shoring_System/soldier_pile/plot/deflection_output{i + 1}.html",
        #          "r").read())
        specific_plot.append(f"https://civision.balafan.com/unrestrained_shoring/plot/deflection_output{i + 1}")

    html = "<html>"
    html_end = "</html>"

    head = """<head>
	<title>Output Summary</title>
	<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
	<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
	<script src="/app/app/HTML/plotly.js"></script> 
	<script>
      function ShowAndHide(id) {
        var x = document.getElementById(id);
        if (x.style.display == "none") {
          x.style.display = "block";
        } else {
          x.style.display = "none";
        }
      }
    </script>
	<style type="text/css">
		* {font-size: 10px; }
		body {
			font: 10px Arial, Helvetica, sans-serif;
			line-height: 1.0;
		}
		@media print {
			.pagebreak { page-break-before: always; }
		}
		@page {
			size: letter;
			margin: 1.5cm;
			@bottom-right {
				content: "Page " counter(page) " of " counter(pages);
			}
		}
		.custom-page-start {
			margin-top: 0px;
			margin-bottom: 0px;
		}
		h1 {color: #2f4f6e; font-size: 15px;}
		h2 {
			background: #96B9D0; font-size: 13px;
			padding-top: 3px;
			padding-bottom: 3px;
			padding-left: 3px;
			margin-bottom: 5px; margin-top: 5px;
			margin-left: -1px; margin-right: -1px;
		}
		h3 {
			background: #84c1ff; font-size: 13px;
			font-size: 10px; 
			margin-bottom: -1px; margin-top: -1px;
			margin-left: -1px; margin-right: -1px;
			padding-top: 8px;
			padding-bottom: 8px;
			padding-left: 8px;
		}
		t1 {display: block; font-size: 15px; font-style: italic; padding-left: 3px;}
		t1b {font-size: 15px; font-style: italic; font-weight: bold;}
		t2 {font-size: 15px;}
		t2b {font-size: 15px;font-weight: bold;}
		p {font-size: 10px;}
		td {vertical-align: top;}
	</style>
	<style>
      .menu {
        background: #84c1ff;
        height: 4rem;
      }
      .menu ol {
        list-style-type: none;
        margin: 0 auto;
        padding: 0;
      }
      .menu > ol {
        max-width: 1000px;
        padding: 0 2rem;
        display: flex;
      }
      .menu > ol > .menu-item {
        flex: 1;
        padding: 0.75rem 0;
      }
      .menu > ol > .menu-item:after {
        content: "";
        position: absolute;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        bottom: 5px;
        left: calc(50% - 2px);
        background: #feceab;
        will-change: transform;
        transform: scale(0);
        transition: transform 0.2s ease;
      }
      .menu > ol > .menu-item:hover:after {
        transform: scale(1);
      }
      .menu-item {
        position: relative;
        line-height: 2.5rem;
        text-align: center;
      }
      .menu-item a {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        display: block;
        color: #fff;
      }
      .sub-menu .menu-item {
        padding: 0.75rem 0;
        background: #84c1ff;
        opacity: 0;
        transform-origin: bottom;
        animation: enter 0.2s ease forwards;
      }
      .sub-menu .menu-item:nth-child(1) {
        animation-duration: 0.2s;
        animation-delay: 0s;
      }
      .sub-menu .menu-item:nth-child(2) {
        animation-duration: 0.3s;
        animation-delay: 0.1s;
      }
      .sub-menu .menu-item:nth-child(3) {
        animation-duration: 0.4s;
        animation-delay: 0.2s;
      }
      .sub-menu .menu-item:hover {
        background: #c4ddff;
      }
      .sub-menu .menu-item a {
        padding: 0 0.75rem;
      }
      @media screen and (max-width: 600px) {
        .sub-menu .menu-item {
          background: #c06c84;
        }
      }

      @media screen and (max-width: 600px) {
        .menu {
          position: relative;
        }
        .menu:after {
          content: "";
          position: absolute;
          top: calc(50% - 2px);
          right: 1rem;
          width: 30px;
          height: 4px;
          background: #fff;
          box-shadow: 0 10px #fff, 0 -10px #fff;
        }
        .menu > ol {
          display: none;
          background: #f67280;
          flex-direction: column;
          justify-content: center;
          height: 100vh;
          animation: fade 0.2s ease-out;
        }
        .menu > ol > .menu-item {
          flex: 0;
          opacity: 0;
          animation: enter 0.3s ease-out forwards;
        }
        .menu > ol > .menu-item:nth-child(1) {
          animation-delay: 0s;
        }
        .menu > ol > .menu-item:nth-child(2) {
          animation-delay: 0.1s;
        }
        .menu > ol > .menu-item:nth-child(3) {
          animation-delay: 0.2s;
        }
        .menu > ol > .menu-item:nth-child(4) {
          animation-delay: 0.3s;
        }
        .menu > ol > .menu-item:nth-child(5) {
          animation-delay: 0.4s;
        }
        .menu > ol > .menu-item + .menu-item {
          margin-top: 0.75rem;
        }
        .menu > ol > .menu-item:after {
          left: auto;
          right: 1rem;
          bottom: calc(50% - 2px);
        }
        .menu > ol > .menu-item:hover {
          z-index: 1;
        }
        .menu:hover > ol {
          display: flex;
        }
        .menu:hover:after {
          box-shadow: none;
        }
      }

      .sub-menu {
        position: absolute;
        width: 100%;
        top: 100%;
        left: 0;
        display: none;
        z-index: 1;
      }
      .menu-item:hover > .sub-menu {
        display: block;
      }

      @media screen and (max-width: 600px) {
        .sub-menu {
          width: 100vw;
          left: -2rem;
          top: 50%;
          transform: translateY(-50%);
        }
      }

      html,
      * {
        box-sizing: border-box;
      }
      *:before,
      *:after {
        box-sizing: inherit;
      }

      a {
        text-decoration: none;
      }
      buttom {
        cursor: pointer;
      }
      @keyframes enter {
        from {
          opacity: 0;
          transform: scaleY(0.98) translateY(10px);
        }
        to {
          opacity: 1;
          transform: none;
        }
      }
      @keyframes fade {
        from {
          opacity: 0;
        }
        to {
          opacity: 1;
        }
      }
    </style>
    <style>
    .dropdown-caret {
        border-bottom-color: #0000;
        border-left-color: #0000;
        border-right-color: #0000;
        border-style: solid;
        border-width: var(--primer-borderWidth-thicker, 4px) var(--primer-borderWidth-thicker, 4px) 0;
        content: "";
        display: inline-block;
        height: 0;
        vertical-align: middle;
        width: 0;
        }
    </style>
  </head>"""

    body = "<body>"
    body_end = "</body>"
    div = """<div class="custom-page-start"> <hr>"""
    div_start = """<div class="custom-page-start" style="width: 50%; : padding-right: 5px">"""
    div_end = "</div>"
    h1 = "<h1>"
    h1_title = "<h1 style='font-size: 15px'>"
    h1_end = "</h1>"
    table = "<table border=1>"
    table_end = "</table>"
    tbody = "<tbody>"
    tbody_end = "</tbody>"
    hr = "<hr>"
    tr = "<tr>"
    tr_height_92 = '<tr height="92.4">'
    tr_height_115 = '<tr height="115.5">'
    tr = "<tr>"
    tr_end = "</tr>"
    th = "<th>"
    th_end = "</th>"
    td = "<td>"
    td_end = "</td>"
    empty_line = "<p></p>"

    def title():

        t1 = """		<table border="0" style="border-collapse: collapse; width: 100%;">
			<tbody>
				<tr>
					<td style="width: 100%;font-size: 15px;">
						<h2>"""

        t2 = """</h2>
            </td>
          </tr>
        </tbody>
      </table>
    <hr>"""

        title = h1_title + titles[0][0] + h1_end + t1 + titles[0][1] + t2

        return title

    m1 = """
                 <table border="0" style="border-collapse: collapse; width: 100%;">
                     <tbody>
                       <tr>
                         <td style="width: 100%;"><t1b></t1b></td>
                       </tr>
                     </tbody>
                   </table>
                     """
    m2 = """
                 <table border="0" style="border-collapse: collapse; width: 100%;">
                     <tbody>
                       <tr>
                         <td style="width: 100%; height: 20; background-image: linear-gradient(white, #84c1ff);"><t1b></t1b></td>
                       </tr>
                     </tbody>
                   </table>
                     """
    h3 = """
                    <table border="1" bordercolor="#C0C0C0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
            			<tbody style="width: 100%;padding: 5px;border: 5px solid white;background-color: #e7eff6 ">
                      """
    start_table = """<table border="0" style="border-collapse: collapse; width: 100%;">
                    			<tbody>
                    				<tr>"""

    excel_start = """

                    					<td style="width: 7%;text-align: center; vertical-align: middle"><t1b>Download Values:</t1b></td>
                    					<td style="width: 7%;text-align: center; vertical-align: middle"><a href="https://civision.balafan.com/report/unrestrained_shoring/excel/"""
    excel_start_specific = """

                    					<td style="width: 12%;text-align: left; vertical-align: middle"><t1b>Download Report:</t1b></td>
                    					<td style="width: 8%;text-align: left; vertical-align: middle"><a href="https://civision.balafan.com/report/unrestrained_shoring/excel/"""
    report_start = """

                        					<td style="width: 8%;text-align: left; vertical-align: middle"><a href="https://civision.balafan.com/report/unrestrained_shoring/"""

    excel_end = """
                            " target="_blank" ><img height = "20px" src="https://civision.balafan.com/icon/CSV_data"></a></td>
                            """
    space_td = """<td style="width:1%"></td>"""
    excel_end_specific = """
                               " target="_blank" ><img height = "20px" src="https://civision.balafan.com/icon/CSV_data"></a></td>
                               """

    report_end = """
                                   " target="_blank" ><img height = "20px" src="https://civision.balafan.com/icon/PDF_Detailed"></a></td><td style="width:79%"></td>
                                   """
    end_table = """</tr>
                              </tbody>
                            </table>"""

    def general():
        general_t1 = """<table border="0" style="border-collapse: collapse; width: 100%;">
                			<tbody>
                				<tr><td style="width: 32.5%; vertical-align: text-top;font-size: 15px;  padding: 0px"><h3>
                				"""
        general_t1_end = """</h3></td>
                                  </tr>
                                </tbody>
                              </table>"""

        h2 = """
                  </t2b></td>
                  </tr>
                </tbody>
              </table>
                  """

        h4 = """
                  </tbody>
              </table>
                  """

        plot_row = """
                        <td style="width: 33.33%;text-align: center; vertical-align: middle" ><t2>
                        """
        three_inline = """
                                <td style="width: 33.33%;text-align: center; vertical-align: middle;height: 50px" ><t2>
                                """
        end_plot_row = end_three_inline = """
                        </t2></td>
                        """

        s = ""
        for header in range(len(titles[1])):
            s += general_t1 + titles[1][header] + general_t1_end
            s += m1
            s += h3
            if header == 0:  # general plots
                s += tr
                for plot in range(len(general_plot)):
                    s += plot_row + f'<img src="{general_plot[plot]}" width="100%" height="auto">' + end_plot_row

                #  download values for general plots
                s += start_table
                for plot_title in range(len(general_plot)):
                    s += excel_start + titles[3][plot_title] + excel_end
                s += end_table
            if header == 1:  # general values
                for i in range(len(general_values)):
                    if i == 0 or i == 3:  # three value in every line
                        s += tr
                    s += three_inline + general_values[i] + end_three_inline
                    if i == 2 or i == 5:
                        s += tr_end

        return s

    def final_solution(s):
        specific_t1 = """<table border="0" style="border-collapse: collapse; width: 100%;">
                    			<tbody>
                    				<tr>
                    				"""
        drop_down_1 = """<nav ">
        <ol>
        <h3 class="menu-item" style="cursor: pointer">"""
        drop_down_2 = """<ol class="sub-menu">"""
        drop_down_end = """</ol>
              </h3>
             </ol>
            </nav>"""
        specific_t1_mid1 = """<td  class="menu" style="width: 20%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_mid2 = """<td  class="menu" style="width: 35%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_mid3 = """<td  class="menu" style="width: 45%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_mid_end = """</h3></td>"""
        specific_t1_end = """</h3></td>
                                      </tr>
                                    </tbody>
                                  </table>"""

        first_column = """
                                <td style="width: 20%;text-align: center; vertical-align: middle" ><t2>
                                """

        second_column = """
                                        <td style="width: 35%;text-align: center; vertical-align: middle"><t2>
                                        """
        second_column_white = """
                                                <td style="background-color:white; width: 35%;text-align: center; vertical-align: middle"><t2>
                                                """
        third_column = """
                                                <td style="width: 11.25%;text-align: center; vertical-align: middle", height="90" ><t2>
                                                """
        image_column = """
                                        <td style="width: 33.75%;text-align: center; vertical-align: middle;background-color: white" colspan="3"  ><img src="https://civision.balafan.com/section" width="80%" height="auto"></td>
                                        """
        image_column_prop = """
                                                <td style="width: 11.25%;text-align: center; vertical-align: middle;background-color: white" ><t2>
                                                """
        end_column = """
                                </t2></td>
                                """
        # create titles
        s += specific_t1 + specific_t1_mid1 + titles[2][0] + specific_t1_mid_end + specific_t1_mid2 + titles[2][
            1] + specific_t1_mid_end + specific_t1_mid3 + \
             titles[2][
                 2] + specific_t1_end

        for i in range(len(specific_values)):
            drop_down_values = f"""<div style="display:block" id="{specific_values[i][0]}">"""
            s += drop_down_values

            # create reports
            s += start_table + excel_start_specific + titles[4][i] + excel_end_specific + space_td + report_start + \
                 titles[5][
                     i] + report_end + end_table
            # s += start_table + report_start + titles[5][i] + excel_end_specific + end_table

            # add values
            s += m1
            s += h3
            ''' 0, 1 -> section name, max def
                2 -> PLOT
                3,4,5 -> DCR moment, shear and deflection
                '''
            s += tr
            s += first_column + specific_values[i][0] + end_column
            s += second_column + "" + end_column
            # s += second_column + f'<img src="{specific_plot[i]}" height="20px">' + end_column
            for j in range(2, 6):
                s += third_column + specific_values[i][j] + end_column
            s += tr_end + tr + first_column + specific_values[i][1] + end_column
            s += second_column_white + f'<img src="{specific_plot[i]}" width="100%" height="auto">' + end_column
            s += image_column_prop + specific_values[i][6] + empty_line + specific_values[i][7] + empty_line + \
                 specific_values[i][8] + empty_line + specific_values[i][9] + empty_line + specific_values[i][
                     10] + end_column
            s += image_column + tr_end + tbody_end + table_end
            s += m2
            s += div_end

        return s

    S = general()
    export = html + head + body + div + title() + final_solution(S) + \
             div_end + body_end + html_end

    return export


def generate_html_response_restrained_shoring_no_solution(output):
    html = "<html>"
    html_end = "</html>"

    head = """<head>
	<title>Output Summary</title>
	<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
	<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
	<style type="text/css">
		* {font-size: 10px; }
		body {
			font: 10px Arial, Helvetica, sans-serif;
			line-height: 1.0;
		}
		@media print {
			.pagebreak { page-break-before: always; }
		}
		@page {
			size: letter;
			margin: 1.5cm;
			@bottom-right {
				content: "Page " counter(page) " of " counter(pages);
			}
		}
		.custom-page-start {
			margin-top: 0px;
			margin-bottom: 0px;
		}
		h1 {color: #2f4f6e; font-size: 15px;}
		h2 {
			background: #96B9D0; font-size: 13px;
			padding-top: 3px;
			padding-bottom: 3px;
			padding-left: 3px;
			margin-bottom: 5px; margin-top: 5px;
			margin-left: -1px; margin-right: -1px;
		}
		h3 {
			background: #84c1ff; font-size: 13px;
			font-size: 10px; 
			margin-bottom: -1px; margin-top: -1px;
			margin-left: -1px; margin-right: -1px;
			padding-top: 8px;
			padding-bottom: 8px;
			padding-left: 8px;
		}
		t1 {display: block; font-size: 15px; font-style: italic; padding-left: 3px;}
		t1b {font-size: 15px; font-style: italic; font-weight: bold;}
		t2 {font-size: 15px;}
		t2b {font-size: 15px;font-weight: bold;}
		p {font-size: 10px;}
		td {vertical-align: top;}
	</style>
  </head>"""

    body = "<body>"
    body_end = "</body>"
    div = """<div class="custom-page-start"> <hr>"""
    div_start = """<div class="custom-page-start" style="width: 50%; : padding-right: 5px">"""
    div_end = "</div>"
    h1 = "<h1>"
    h1_title = "<h1 style='font-size: 15px'>"
    h1_end = "</h1>"
    table = "<table border=1>"
    table_end = "</table>"
    tbody = "<tbody>"
    tbody_end = "</tbody>"
    hr = "<hr>"
    tr = "<tr>"
    tr_end = "</tr>"
    th = "<th>"
    th_end = "</th>"
    td = "<td>"
    td_end = "</td>"

    def title():
        t1 = """		<table border="0" style="border-collapse: collapse; width: 100%;">
			<tbody>
				<tr>
					<td style="width: 100%;font-size: 15px;">
						<h2>"""

        t2 = """</h2>
            </td>
          </tr>
        </tbody>
      </table>
    <hr>"""

        title = h1_title + output[0][0] + h1_end + t1 + output[0][1] + t2

        return title

    def solutions():
        m1 = """
      <table border="0" style="border-collapse: collapse; width: 100%;">
          <tbody>
            <tr>
              <td style="width: 100%;"><t1b></t1b></td>
            </tr>
          </tbody>
        </table>
          """

        h1 = """
          <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
			<tbody>
				<tr>
					<td style="width: 15%;padding: 5px;border: 5px solid white;background-color: #bfd6f6  ;"><t2b>
          """
        h2 = """
          </t2b></td>
          <td style="width: 85%;padding: 5px;border: 5px solid white;background-color: #bfd6f6  ;"><t2b>
          """
        h1_2_end = """
          </t2b></td>
          </tr>
        </tbody>
      </table>
          """

        h3 = """
        <table border="1" bordercolor="#C0C0C0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
			<tbody style="width: 100%;padding: 5px;border: 5px solid white;background-color: #e7eff6 ">
          """

        h4 = """
          </tbody>
      </table>
          """

        h8 = """
        <td style="width: 15%;text-align: center;" ><t2>
        """
        h8_1 = """
                <td style="width: 85%;text-align: center;"><t2>
                """

        h9 = """
        </t2></td>
        """

        s = ""
        s += h1 + output[1][0] + h2 + output[1][1] + h1_2_end + h3
        for i in range(len(output[2])):
            s += tr + h8 + str(output[2][i][0]) + h9 + h8_1 + str(output[2][i][1]) + h9
            s += tr_end
        s = s + tbody_end + table_end
        s = s + m1 + hr

        return s

    export = html + head + body + div + title() + solutions() + \
             div_end + body_end + html_end

    return export


def unrestrained_front_checker(titles, values):
    if values == "NO SOLUTION":
        response = generate_html_response_restrained_shoring_no_solution(titles)
    else:
        response = generate_html_response_restrained_shoring(titles, values)
    return response


generate_html_response_restrained_shoring_output = generate_html_response_restrained_shoring(
    [['Cantilever Soldier Pile - Output Summary', 'Final Solution Alternatives'], ['General Plots', 'General Values'],
     ['Section', 'Deflection Plot', 'Checks'], ['load', 'shear', 'moment'],
     ['deflection1', 'deflection2', 'deflection3'],
     ['Rep_Unrestrained_Shoring_Section_1', 'Rep_Unrestrained_Shoring_Section_2',
      'Rep_Unrestrained_Shoring_Section_3']], [
        ['Embedment Depth ( ft ) = -212.01', 'maximum Shear ( lb ) = 6962.11', 'maximum Moment ( lb-ft ) = 21330.17',
         'Y zero Shear ( ft ) = 12.46', 'Required Area ( in^2 ) = 0.44', 'Required Sx ( in^3 ) = 10.77'], [
            ['W40X149', 'Maximum Deflection ( in ) = 0.0', 'DCR Moment = 0.02', 'DCR Shear = 0.01',
             'DCR Deflection = 0.0', 'Timber Size 1 x 2: \n\nFail! Your timber fail in moment design.',
             'd = 42.0 ( in )', 'h = 38.2 ( in )', 'b = 11.8 ( in )', 'tw = 0.63 ( in )', 'tf = 0.83 ( in )'],
            ['W36X135', 'Maximum Deflection ( in ) = 0.0', 'DCR Moment = 0.02', 'DCR Shear = 0.01',
             'DCR Deflection = 0.0', 'Timber Size 1 x 2: \n\nFail! Your timber fail in moment design.', 'd = 36 ( in )',
             'h = 35.6 ( in )', 'b = 12.0 ( in )', 'tw = 0.6 ( in )', 'tf = 0.79 ( in )'],
            ['W33X118', 'Maximum Deflection ( in ) = 0.0', 'DCR Moment = 0.03', 'DCR Shear = 0.01',
             'DCR Deflection = 0.01', 'Timber Size 1 x 2: \n\nFail! Your timber fail in moment design.',
             'd = 36 ( in )', 'h = 32.9 ( in )', 'b = 11.5 ( in )', 'tw = 0.55 ( in )', 'tf = 0.74 ( in )']]])
a = open("output.html", "w", encoding='UTF8')
a.write(generate_html_response_restrained_shoring_output)
a.close()
