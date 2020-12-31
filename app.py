from flask import Flask, render_template, request, redirect, url_for
# from flask import (
#     Blueprint, flash, g , session
# )

app = Flask(__name__)
app.vars={}

@app.route('/index', methods=['GET','POST'])
def index():
  if request.method == 'GET':
    return render_template('index.html')
  else: # request was a POST
    app.vars['symbol'] = request.form['symbol']
    # close          = option1
    # adjusted close = option2
    # open           = option3
    # adjusted open  = option4
    app.vars['close'] = request.form.get('option1')
    app.vars['ajd_close'] = request.form.get('option2')
    app.vars['open'] = request.form.get('option3')
    app.vars['adj_open'] = request.form.get('option4')

    return redirect(url_for('app.makeplot'))

@app.route('/makeplot', methods=['GET'])
def makeplot():
  # call/do whatever to get the data and make the visualizations
  # return render_template('about.html')

  return redirect(url_for('app.display'))

@app.route('/display', methods=['GET','POST'])
def display():
  # call/do whatever to display the visualizations
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507, debug=True)


