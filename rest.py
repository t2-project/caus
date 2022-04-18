from flask import Flask, request
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        return update_stuff()
    if request.method == 'GET':
        return build_start_page()

@app.route('/elasticity')
def say_hello():
    return 'Hello from Server'


def update_stuff():
    a = 1
    return str(a)

def build_start_page():
    a = 0
    return str(a)
