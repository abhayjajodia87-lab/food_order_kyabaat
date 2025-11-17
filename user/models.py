from flask import jsonify, request, session
import uuid
from app import db
import pymongo

class User:
    def __init__(self):
        # Make sure users collection exists
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
    
    def signUp(self):
        try:
            # Get data from form
            data = request.get_json()
            
            # Check if we got data
            if not data:
                print("No data received from form")
                return jsonify({"message": "No data received"}), 400
                
            id = uuid.uuid4().hex
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            
            # Check if email already exists
            if db.users.find_one({"email": email}):
                print(f"Email {email} already exists")
                return jsonify({"message": "Email already registered"}), 400
            
            # Create new user
            new_user = {
                "id": id,
                "name": name,
                "email": email,
                "password": password
            }
            
            # Insert into database
            print(f"Attempting to insert user: {name} ({email})")
            result = db.users.insert_one(new_user)
            
            # Verify insertion
            if result.inserted_id:
                print(f"Successfully inserted user with ID: {result.inserted_id}")
                return jsonify({
                    "message": "Registration successful!",
                    "user": new_user
                }), 200
            else:
                print("Failed to insert user into database")
                return jsonify({"message": "Failed to create user"}), 500
                
        except pymongo.errors.PyMongoError as e:
            print(f"Database error: {str(e)}")
            return jsonify({"message": "Database error occurred"}), 500
        except Exception as e:
            print(f"Error during signup: {str(e)}")
            return jsonify({"message": "An error occurred"}), 500
    
    def login(self):
        try:
            # Get data from form
            data = request.get_json()
            
            if not data:
                print("No data received from login form")
                return jsonify({"message": "No data received"}), 400
                
            email = data.get('email')
            password = data.get('password')
            
            # Find user in database
            print(f"Attempting to find user with email: {email}")
            user = db.users.find_one({"email": email, "password": password})

            # Hardcoded admin credentials (development). Replace with proper admin user in DB for production.
            if email == "admin@kyabaat.com" and password == "admin123":
                session['user_id'] = "admin"
                session['user_name'] = "Admin"
                session['user_email'] = email
                session['is_admin'] = True

                return jsonify({
                    "message": "Admin login successful!",
                    "user": {"id": "admin", "name": "Admin", "email": email, "is_admin": True}
                }), 200

            if user:
                print(f"User found: {user['name']}")
                # Remove _id before sending (it's not JSON serializable)
                user.pop('_id', None)
                # Store minimal user info in session (do NOT store password)
                session['user_id'] = user.get('id')
                session['user_name'] = user.get('name')
                session['user_email'] = user.get('email')
                session['is_admin'] = False

                return jsonify({
                    "message": "Login successful!",
                    "user": {
                        "id": user.get('id'),
                        "name": user.get('name'),
                        "email": user.get('email'),
                        "is_admin": False
                    }
                }), 200
            
            print(f"No user found with email: {email}")
            return jsonify({
                "message": "Invalid email or password"
            }), 400
            
        except pymongo.errors.PyMongoError as e:
            print(f"Database error during login: {str(e)}")
            return jsonify({"message": "Database error occurred"}), 500
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return jsonify({"message": "An error occurred"}), 500


