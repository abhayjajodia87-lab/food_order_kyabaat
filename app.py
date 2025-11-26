

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymongo
from datetime import datetime
from zoneinfo import ZoneInfo
import calendar


# Initialize Flask app
app = Flask(__name__)

# Set a secure secret key for session management
app.secret_key = 'fd8b3f7967e94c308fe15ba8490c1926c85d38e861c84c96'  # This is a secure randomly generated key

# Database connection
try:
    client = pymongo.MongoClient("mongodb+srv://kyabaat:kyabaat@kyabaat.c56e53e.mongodb.net/")
    # Test the connection
    import certifi

    mongo_uri = "mongodb+srv://kyabaat:kyabaat@kyabaat.c56e53e.mongodb.net/"
    client = pymongo.MongoClient(
        mongo_uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000  # 5 second timeout
    )

    # Test the connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
    
    db = client["kyabaat"]
except pymongo.errors.ConnectionFailure as e:
    print("❌ Could not connect to MongoDB:", str(e))
    raise
except pymongo.errors.ServerSelectionTimeoutError as e:
    print("❌ MongoDB server selection timeout:", str(e))
    raise
except pymongo.errors.OperationFailure as e:
    print("❌ MongoDB operation failed:", str(e))
    raise
except Exception as e:
    print("❌ Unexpected error with MongoDB:", str(e))
    raise

# Page Routes (GET requests)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('ordernow.html')

@app.route('/update_item/<db_id>')
def update_item(db_id):
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))

    fm = FoodMenu()
    item = fm.get_item(db_id=db_id)
    print('Updating item:', item)
    if not item:
        # If item not found, redirect back to view page instead of rendering an error template
        return redirect(url_for('view_page'))
    return render_template('update_item.html', item=item)


@app.route('/update_item')
def update_item_root():
    # Friendly fallback when a link doesn't include an id — redirect to admin view
    return redirect(url_for('view_page'))

@app.route('/admin')
def admin_page():
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))
    return render_template('admin.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def registerpage():
    return render_template('register.html')

@app.route('/view', methods=['GET'])
def view_page():
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))
    
    fm = FoodMenu()
    resp = fm.get_menu()
    if resp[1] != 200:
        items = []
    else:
        data = resp[0].get_json()
        items = data.get('menu', [])

    return render_template('view.html', menu=items)

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/menu', methods=['GET'])
def menu_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    

    tz = ZoneInfo("Europe/Helsinki")           
    today = calendar.day_name[datetime.now(tz).weekday()]
    fm = FoodMenu()
    resp = fm.get_menu()
    if resp[1] != 200:
        items = []
    else:
        data = resp[0].get_json()
        items = data.get('menu', [])
    return render_template('menu.html', menu=items, today=today)

@app.route('/about', methods=['GET'])
def about_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('about.html')

@app.route('/contact', methods=['GET'])
def contact_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('contact_us.html')




# Import routes after app is created
from user.route import *
from foodmenu.route import *
from foodmenu.models import FoodMenu

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)