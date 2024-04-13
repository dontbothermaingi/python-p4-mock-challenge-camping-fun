#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def get_campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        return jsonify([camper.to_dict() for camper in campers]), 200
    
    elif request.method == 'POST':
        data = request.json
        age = data.get('age')

        if (age < 8 or age > 18):
            return jsonify({'errors': ['Age must be between 8 and 18 years old']}), 400
            
        name = data.get('name')

        new_camper = Camper(
            name = name,
            age = age,
        )

        db.session.add(new_camper)
        db.session.commit()

        return jsonify(new_camper.to_dict()), 200
    
    return jsonify({'error': 'An unexpected error occurred while processing your request.'}), 404



@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def get_campers_by_id(id):
    session = db.session
    camper = session.get(Camper, id)

    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    
    if request.method == 'GET':
        return jsonify(camper.to_dict()), 200
    
    elif request.method == 'PATCH':
        data =request.json

        if not data:
            return jsonify({'error': 'No data provided for update'}), 400  
        
        # validates the age attribute
        age = data.get('age')
        if  not (8 < age < 18):
            return jsonify({'errors': ['Age must be between 8 to 18 years old']}), 400
        
        # Update allowed attributes
        allowed_attributes = ['name', 'age']
        for attr,value in data.items():
            if attr in allowed_attributes:
                setattr(camper,attr,value)
            else:
                return jsonify({'error': 'Invalid attribute'}), 400
            
            db.session.commit()

        return jsonify(camper.to_dict()), 202
    
    return jsonify({'error': 'An unexpected error occurred while processing your request.'}), 500
    
@app.route('/activities', methods=['GET'])
def get_activities():
    if request.method == 'GET':
        activities = Activity.query.all()
        return jsonify([activity.to_dict() for activity in activities])
    
@app.route('/activities/<int:id>', methods=["GET", "DELETE"])
def delete_activity(id):
    activity = Activity.query.get(id)

    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    if request.method == "GET":
        return jsonify(activity.to_dict()), 200
    
    elif request.method == "DELETE":
        db.session.delete(activity)
        db.session.commit()
        return '', 204

    
@app.route('/signups', methods=["GET","POST"])
def get_and_post_signups():
    if request.method == "GET":
        signups = Signup.query.all()
        return jsonify([signup.to_dict() for signup in signups]), 200
    elif request.method == 'POST':
        data = request.json
        time = data.get('time')

        if not 0 <= time <= 23:
            return jsonify({'errors': ['Time must be less than 23 hours']}), 400
        
        camper_id = data.get('camper_id')
        activity_id = data.get('activity_id')

        new_signup = Signup(
            time = time,
            camper_id = camper_id,
            activity_id = activity_id,
        )

        db.session.add(new_signup)
        db.session.commit()
        return jsonify(new_signup.to_dict()), 200
    return jsonify({'error': 'An unexpected error occurred while processing your request.'}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
