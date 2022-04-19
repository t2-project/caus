from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    return build_start_page()

@app.route('/elasticity')
def returnElasticity():
    return 'Hello from Server'

@app.route('/scalingmethod',methods=['GET','POST'])
def handle_scalingmethods():
    if request.method == 'GET':
        return 'Return possible scaling methods here'
    else:
        return 'Change scaling method to sent method'

@app.route('/explainability', methods=['GET', 'POST'])
def handle_explainability():
    if request.method == 'GET':
        return 'return possible explainability methods here (depending on the machine learning method'
    else:
        return 'change explainability method to chosen method'
