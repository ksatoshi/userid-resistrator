from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

@app.route('/webhock', methods=['POST'])
def webhock():
    print(request.json)
    return '', 200, {}

if __name__ == '__main__':
    app.run()