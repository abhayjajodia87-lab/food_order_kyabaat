# Kyabaat - Local Setup (Beginner Friendly)

This is a small Flask app that uses MongoDB (PyMongo).

Quick start (macOS / Linux):

1. (Optional but recommended) Create and activate a virtual environment:

   python3 -m venv venv
   source venv/bin/activate

2. Install dependencies:

   python3 -m pip install -r requirements.txt

3. Start the app:

   python3 app.py

4. Open the app in your browser: http://127.0.0.1:4000

Notes:
- The admin page is at `/admin` (the app uses a simple `is_admin` session flag for development).
- The admin form submits to `/admin/add-item` and works with or without JavaScript.
- If the server fails at startup, ensure you have network access to your MongoDB URI and that `pymongo` and `certifi` are installed.

If you get errors, copy the terminal traceback and paste it here and I'll help debug it.
