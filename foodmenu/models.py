from flask import jsonify, request
import uuid
from app import db
import pymongo
from bson import ObjectId


class FoodMenu:
    def __init__(self):
        # Ensure the collection exists
        if 'foodmenu' not in db.list_collection_names():
            db.create_collection('foodmenu')

    def _sanitize_doc(self, doc: dict) -> dict:
        """Remove or convert Mongo-specific types so the doc is JSON serializable.

        - removes '_id' if present
        - converts any ObjectId values at the top level to strings
        """
        if not isinstance(doc, dict):
            return doc

        doc.pop('_id', None)

        for k, v in list(doc.items()):
            if isinstance(v, ObjectId):
                doc[k] = str(v)

        return doc

    def add_item(self):
        # Accept JSON payloads (preferred) or fall back to form data for plain HTML form posts
        data = request.get_json(silent=True) or request.form.to_dict() or {}

        item_id = uuid.uuid4().hex
        new_item = {
            'item_id': item_id,
            'name': data.get('name'),
            'description': data.get('description'),
            'price': data.get('price'),
            'img': data.get('img'),
            'specialday': data.get('specialday')
        }

        result = db.foodmenu.insert_one(new_item)

        # Add serializable db id for client
        if getattr(result, 'inserted_id', None):
            new_item['db_id'] = str(result.inserted_id)

        # Defensive: ensure no raw ObjectId or _id remains
        sanitized = self._sanitize_doc(new_item)

        return jsonify({
            'message': 'Food item added successfully!',
            'item': sanitized
        }), 200
    def get_menu(self):
        """Return full menu as JSON-serializable list."""
        try:
            raw_items = list(db.foodmenu.find({}))
            items = []
            for it in raw_items:
                # keep a string id for client use
                oid = it.get('_id')
                if oid:
                    it['db_id'] = str(oid)
                # remove raw _id
                it.pop('_id', None)
                items.append(self._sanitize_doc(it))

            return jsonify({'message': 'Menu fetched successfully!', 'menu': items}), 200

        except pymongo.errors.PyMongoError as e:
            print('Database error while fetching menu:', str(e))
            return jsonify({'message': 'Database error occurred'}), 500
        except Exception as e:
            print('Error during fetching menu:', str(e))
            return jsonify({'message': 'An error occurred'}), 500

    def delete_item(self, db_id=None, item_id=None):
        """Delete an item by db_id (stringified _id) or item_id."""
        try:
            if db_id:
                result = db.foodmenu.delete_one({'_id': ObjectId(db_id)})
            elif item_id:
                result = db.foodmenu.delete_one({'item_id': item_id})
            else:
                return jsonify({'message': 'No id provided'}), 400

            if result.deleted_count:
                return jsonify({'message': 'Item deleted successfully'}), 200
            else:
                return jsonify({'message': 'Item not found'}), 404

        except Exception as e:
            print('Error deleting item:', str(e))
            return jsonify({'message': 'An error occurred'}), 500

    def update_item(self, db_id=None, item_id=None, updates=None):
        """Update top-level fields for an item and return the updated doc."""
        try:
            if not updates:
                return jsonify({'message': 'No updates provided'}), 400

            query = None
            if db_id:
                query = {'_id': ObjectId(db_id)}
            elif item_id:
                query = {'item_id': item_id}
            else:
                return jsonify({'message': 'No id provided'}), 400

            # Prevent modifying db identifiers
            updates.pop('db_id', None)
            updates.pop('item_id', None)

            # Try to coerce price to a number if provided
            if 'price' in updates:
                try:
                    updates['price'] = float(updates['price'])
                except Exception:
                    # keep original if conversion fails
                    pass

            result = db.foodmenu.update_one(query, {'$set': updates})

            if result.matched_count:
                # fetch updated document
                updated = db.foodmenu.find_one(query)
                if updated:
                    oid = updated.get('_id')
                    if oid:
                        updated['db_id'] = str(oid)
                    updated.pop('_id', None)
                    return jsonify({'message': 'Item updated', 'item': self._sanitize_doc(updated)}), 200

            return jsonify({'message': 'Item not found'}), 404

        except Exception as e:
            print('Error updating item:', str(e))
            return jsonify({'message': 'An error occurred'}), 500
