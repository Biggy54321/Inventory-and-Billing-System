from flask import Flask, render_template, request, redirect
import sys
sys.path += ['../']
from CmsLib import *

app = Flask(__name__ , template_folder = '../html_src/', static_folder = '../html_src/')
pysql = PySql(app, 'db.yaml')

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')



if __name__ == "__main__" :
    app.run(debug = True)