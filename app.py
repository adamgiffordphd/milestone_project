from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from bokeh.resources import CDN
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.models import CustomJS, DateSlider
from bokeh.models.tools import HoverTool
from bokeh.layouts import column
from bokeh.resources import CDN
from bokeh.embed import file_html
from datetime import date, timedelta
import simplejson as json
import requests

def get_key(json_file,json_key='alpha_vantage_info'):
    with open(json_file) as f:
        data = json.load(f)
    
    user_values = data[json_key]
    return user_values['api_key']

json_file = 'alpha_vantage_config.json'
api_key = get_key(json_file=json_file)

base_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY'
adj_base_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'

def fetch_response(symbol,api_key,url):
    url_search = '&symbol={}&apikey={}'.format(symbol, api_key)
    url = url + url_search
    return requests.get(url).json()

def make_df(response):
    df = pd.DataFrame.from_dict(response['Time Series (Daily)'], orient='index')
    df.rename(columns=lambda x: x[3:], inplace=True)
    df.index = pd.to_datetime(df.index)
    df.sort_index(ascending=False,inplace=True)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'date'}, inplace=True)
    return df

def create_title(appvars):
    title_str = ''
    for key in appvars.keys():
        if key=='symbol':
            title_str = title_str + appvars['symbol'] + ' stock: '
        else:
            if appvars[key] is not None:
                title_str = title_str + appvars[key] + ', '

    title_str = title_str.split(',')
    print(title_str)
    if title_str[1]!='  ':
      title_str[-2] = '& ' + title_str[-2].strip()
      title_str = ', '.join(title_str)
      title_str = title_str[:-3]
    else:
      title_str = title_str[0]
    
    print(title_str)
    return title_str

def get_x_bounds():
    right = pd.to_datetime(date.today().strftime("%Y-%m-%d"))
    d = date.today() - timedelta(days=30)
    left = pd.to_datetime(d.strftime("%Y-%m-%d"))
    return left, right

colors_dict = {}
colors_dict['open'] = 'red'
colors_dict['close'] = 'blue'
colors_dict['adj_close'] = 'navy'
# colors_dict['open'] = 'firebrick'
# colors_dict['close'] = 'navy'
# colors_dict['adj_close'] = 'darkslateblue'

lines_dict = {}
lines_dict['open'] = 'solid'
lines_dict['close'] = 'solid'
lines_dict['adj_close'] = 'dotted'

def make_line(df,handle,dict_val,color,linedash):
    if dict_val is not None:
        l = handle.line('date', dict_val.lower(), line_width=2, line_color=color, line_dash=linedash, alpha = 0.5, legend_label=dict_val.lower(), source=df)
        ytip = (dict_val.title(), '@{' + dict_val.lower() + '}')
        return l, ytip
    
    return None,None

def make_plot(appvars, df):
    title_str = create_title(appvars)

    TOOLS = 'box_zoom,reset'
    # create a new plot (with a title) using figure
    p = figure(x_axis_type="datetime", title=title_str, plot_height=350, plot_width=700, 
            x_axis_label='Date', y_axis_label='Price ($)', tools=TOOLS)

    tips = [("Date",'@date{%F}')]
    handle_grabbed = False
    for key,val in appvars.items():
        if key!='symbol':
            color = colors_dict[key]
            linedash = lines_dict[key]
            l, tip = make_line(df,p,val,color,linedash)
            if l is not None:
                tips.append(tip)
                if not handle_grabbed:
                    rndr = l
                    handle_grabbed = True            

    hover = HoverTool(tooltips=tips, mode='vline', point_policy='follow_mouse', show_arrow=False, renderers=[rndr], formatters = {'@date':'datetime'})
    p.add_tools(hover)

    left, right = get_x_bounds()
    callback = CustomJS(args=dict(x_range=p.x_range), code="""
      var right = cb_obj.value
      var left = right - 2592000000
      x_range.start = left
      x_range.end = right
    """)
    slider = DateSlider(start=left, end=right, value=right, step=86400000, title='End Date')
    slider.js_on_change('value', callback)

    p.legend.location = "bottom_left"
    p.legend.click_policy="hide"

    p.x_range.start = left
    p.x_range.end = right
    layout = column(slider, p)

    return layout

app = Flask(__name__)
app.vars={}
print(app.vars)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():    
    app.vars['symbol'] = request.form['symbol']
    app.vars['open'] = request.form.get('option1')
    app.vars['close'] = request.form.get('option2')
    app.vars['adj_close'] = request.form.get('option3')
    print(app.vars)
    if app.vars['adj_close'] is not None:
        url = adj_base_url
    else:
        url = base_url

    # get data
    response = fetch_response(app.vars['symbol'],api_key,url)
    df = make_df(response)

    # make plot
    plot = make_plot(app.vars, df)
    # make html template with plot
    html = file_html(plot, CDN, "myplot")
    # return html
    return html


if __name__ == '__main__':
  app.run()


