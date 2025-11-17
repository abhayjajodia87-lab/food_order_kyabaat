from flask import request, render_template, jsonify, session, redirect, url_for
from app import app, db
from foodmenu.models import FoodMenu
from bson import ObjectId


@app.route('/admin/add-item', methods=['POST'])
def add_food_item():
    fm = FoodMenu()
    return fm.add_item()


@app.route('/admin/menu', methods=['GET'])
def get_menu_items():
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))
    fm = FoodMenu()
    return fm.get_menu()


@app.route('/admin/delete-item', methods=['POST'])
def delete_food_item():
    if not session.get('is_admin'):
        return jsonify({'message': 'Unauthorized'}), 401

    # Accept JSON (AJAX) or form POST (plain HTML form)
    json_payload = request.get_json(silent=True)
    if json_payload:
        db_id = json_payload.get('db_id')
        fm = FoodMenu()
        return fm.delete_item(db_id=db_id)

    # fallback for form submission: perform deletion and redirect back to view
    form_data = request.form.to_dict() or {}
    db_id = form_data.get('db_id')
    if not db_id:
        return redirect(url_for('view_page'))

    fm = FoodMenu()
    # perform deletion (fm.delete_item returns a JSON response, but we redirect for form UX)
    try:
        fm.delete_item(db_id=db_id)
    except Exception:
        pass
    return redirect(url_for('view_page'))


@app.route('/admin/update-item', methods=['POST'])
def update_food_item():
    if not session.get('is_admin'):
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    db_id = data.get('db_id')
    updates = data.get('updates') or {}
    fm = FoodMenu()
    return fm.update_item(db_id=db_id, updates=updates)


@app.route('/admin/update/<db_id>', methods=['GET'])
def admin_update_page(db_id):
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))

    raw = db.foodmenu.find_one({'_id': ObjectId(db_id)})
    if not raw:
        return redirect(url_for('view_page'))
    raw.pop('_id', None)
    raw['db_id'] = db_id
    return render_template('update_item.html', item=raw)


@app.route('/admin/update', methods=['POST'])
def admin_update_submit():
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))

    db_id = request.form.get('db_id')
    name = request.form.get('name')
    if db_id and name is not None:
        db.foodmenu.update_one({'_id': ObjectId(db_id)}, {'$set': {'name': name}})
    return redirect(url_for('view_page'))
