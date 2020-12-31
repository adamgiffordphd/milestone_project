from flask import Flask, render_template, request, redirect

# from flask import Flask
# app_lulu = Flask(__name__)

# @app_lulu.route('/hello_page_lulu')
# def hello_world_lulu():
#     # this is a comment, just like in Python
#     # note that the function name and the route argument
#     # do not need to be the same.
#     return 'Hello World!'

# if __name__ == '__main__':
#     app_lulu.run(debug=True)


app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)


