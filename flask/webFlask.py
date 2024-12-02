from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

# create an instance of Flask
app = Flask(__name__)
bootstrap = Bootstrap5(app)

@app.route('/')
def home():
  return render_template('index.html')

# EXAMPLE ROUTES
# ______________________________________________________
# @app.route('/Micah_LANK')
# def t_test():
#    return render_template('my_template_1.html')

# @app.route('/countries')
# def show_countries():
#     return render_template('countries.html', countries=countries_info)

if __name__ == '__main__':
   app.run(debug=True)