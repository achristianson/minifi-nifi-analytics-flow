from multiprocessing import Process, Pipe

import dash
import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output

def describe(processor):
  processor.setDescription("Adds an attribute to your flow files")

def onInitialize(processor):
  processor.setSupportsDynamicProperties()
  processor.addProperty("property name","description","default value", True, False)

def start_dash(conn):
  app = dash.Dash('Dash Hello World')

  text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)
  plotly_figure = dict(data=[dict(x=[1,2,3], y=[2,4,8])])

  app.layout = html.Div([ 
      html.H2('NiFi Simulator', style=text_style),
      html.Div([
          html.Button('Start', id='start-button'),
          html.Button('Stop', id='stop-button'),
          html.Button('Reset', id='reset-button'),
        ]),
      html.Div(id='container-button-basic'),
    ])

  @app.callback(
    dash.dependencies.Output('container-button-basic', 'children'),
    [dash.dependencies.Input('start-button', 'n_clicks')])
  def update_output(n_clicks):
    if n_clicks is None:
      output = ''
    else:
      output = 'Sent command: start'
    conn.send(output)
    return output

  app.server.run();

parent_conn, child_conn = Pipe()
p = None

def onSchedule(context):
  p = Process(target=start_dash, args=(child_conn,))
  p.start()

class WriteCallback(object):
  def process(self, output_stream):
    new_content = 'hello'.encode('utf-8')
    output_stream.write(new_content)
    return len(new_content)

def onTrigger(context, session):
  while parent_conn.poll(.1):
    output = parent_conn.recv();
    ff = session.create()
    ff.addAttribute('test-val', output)
    session.transfer(ff, REL_SUCCESS)
