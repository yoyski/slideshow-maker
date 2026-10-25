"""
Minimal test to debug Flask startup
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello'

if __name__ == '__main__':
    print("Starting Flask...")
    app.run(host='0.0.0.0', port=5001, debug=False)
    print("Flask started!")
