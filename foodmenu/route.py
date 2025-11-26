from flask import request, render_template, jsonify, session, redirect, url_for
from app import app, db
from foodmenu.models import FoodMenu
from bson import ObjectId
from decimal import Decimal
from datetime import datetime


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





@app.route('/admin/update', methods=['POST'])
def admin_update_submit():
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))

    db_id = request.form.get('db_id')
    # Collect partial updates from the form. Only include fields that were provided (non-empty).
    allowed = ['name', 'description', 'price', 'img', 'specialday']
    updates = {}
    for key in allowed:
        if key in request.form:
            val = request.form.get(key)
            # empty string means "don't change" for specialday; for other fields skip if empty
            if val is None or val == '':
                continue
            updates[key] = val

   

    if db_id and updates:
        fm = FoodMenu()
        try:
            fm.update_item(db_id=db_id, updates=updates)
        except Exception as e:
            print('Error updating item in admin_update_submit:', str(e))
    return redirect(url_for('view_page'))


# ----- Cart (session-based) -----
@app.route('/cart', methods=['GET'])
def cart_page():
    # Get cart from session (dict of db_id -> {name,img,price,qty,db_id})
    cart = session.get('cart', {})
    # compute totals
    total = 0.0
    for db_id, entry in cart.items():
        try:
            price = float(entry.get('price', 0) or 0)
        except Exception:
            price = 0.0
        qty = int(entry.get('qty', 0) or 0)
        total += price * qty

    return render_template('cart.html', cart=cart, total=total)


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    # Accept form POSTs from the menu page
    db_id = request.form.get('db_id') or (request.get_json(silent=True) or {}).get('db_id')
    qty = request.form.get('qty') or (request.get_json(silent=True) or {}).get('qty') or 1
    try:
        qty = int(qty)
    except Exception:
        qty = 1

    if not db_id:
        return redirect(url_for('menu_page'))

    fm = FoodMenu()
    item = fm.get_item(db_id=db_id)
    if not item:
        return redirect(url_for('menu_page'))

    # Ensure price is numeric
    try:
        price = float(item.get('price') or 0)
    except Exception:
        price = 0.0

    cart = session.get('cart', {})
    if db_id in cart:
        cart[db_id]['qty'] = int(cart[db_id].get('qty', 0)) + qty
    else:
        cart[db_id] = {
            'db_id': db_id,
            'name': item.get('name'),
            'img': item.get('img'),
            'price': price,
            'qty': qty
        }

    session['cart'] = cart
    # redirect back to menu for simple UX
    return redirect(url_for('menu_page'))


@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    db_id = request.form.get('db_id') or (request.get_json(silent=True) or {}).get('db_id')
    if not db_id:
        return redirect(url_for('cart_page'))

    cart = session.get('cart', {})
    if db_id in cart:
        cart.pop(db_id, None)
        session['cart'] = cart

    return redirect(url_for('cart_page'))


@app.route('/cart/update', methods=['POST'])
def update_cart():
    db_id = request.form.get('db_id') or (request.get_json(silent=True) or {}).get('db_id')
    qty = request.form.get('qty') or (request.get_json(silent=True) or {}).get('qty')
    try:
        qty = int(qty)
    except Exception:
        qty = None

    if not db_id:
        return redirect(url_for('cart_page'))

    cart = session.get('cart', {})
    if db_id in cart:
        if qty is None or qty <= 0:
            cart.pop(db_id, None)
        else:
            cart[db_id]['qty'] = qty
        session['cart'] = cart

    return redirect(url_for('cart_page'))


# ----- Checkout / Order -----
@app.route('/checkout', methods=['GET'])
def checkout():
    # Show checkout form with cart contents
    cart = session.get('cart', {})
    total = 0.0
    for entry in cart.values():
        try:
            price = float(entry.get('price', 0) or 0)
        except Exception:
            price = 0.0
        qty = int(entry.get('qty', 0) or 0)
        total += price * qty

    return render_template('checkout.html', cart=cart, total=total)


@app.route('/checkout', methods=['POST'])
def process_checkout():
    # Collect simple billing info
    name = request.form.get('name')
    address = request.form.get('address')
    phone = request.form.get('phone')
    payment_method = request.form.get('payment_method') or 'cash'

    cart = session.get('cart', {})
    if not cart or len(cart) == 0:
        return redirect(url_for('cart_page'))

    # Recompute totals server-side
    total = 0.0
    items = []
    for db_id, entry in cart.items():
        try:
            price = float(entry.get('price', 0) or 0)
        except Exception:
            price = 0.0
        qty = int(entry.get('qty', 0) or 0)
        subtotal = price * qty
        total += subtotal
        items.append({
            'db_id': db_id,
            'name': entry.get('name'),
            'price': price,
            'qty': qty,
            'subtotal': subtotal
        })

    order = {
        'items': items,
        'total': total,
        'customer': {
            'name': name,
            'address': address,
            'phone': phone
        },
        'payment_method': payment_method,
        'status': 'pending',
        # Attach user identity when available in session
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name'),
        'created_at': datetime.utcnow()
    }

    try:
        res = db.orders.insert_one(order)
        order_id = str(res.inserted_id)
    except Exception as e:
        print('Error creating order:', str(e))
        return redirect(url_for('cart_page'))

    # Clear cart after successful order
    session.pop('cart', None)

    return redirect(url_for('order_success', order_id=order_id))


@app.route('/order_success/<order_id>')
def order_success(order_id):
    # Simple success page showing order id
    return render_template('order_success.html', order_id=order_id)
