import requests
from flask import request, redirect, url_for, flash, session, make_response 

NOCO_DB_URL = "https://db.ceky.me/api/v1/db/data/v1/"
API_TOKEN = "jpgFE3jk3pN9R4S52be05kEG9D-EQbBjiFNrig4x"
HEADERS = {
    "xc-auth": f"{API_TOKEN}",
    "xc-token": f"{API_TOKEN}",
    "Content-Type": "application/json",
    "X-Api-Version": "1.0.0"
}


def get_user_from_nocodb(username):
    # Define the endpoint for fetching users
    endpoint = f"{NOCO_DB_URL}ct_zalihe/users/views/users"
    response = requests.get(endpoint, headers=HEADERS)
    if response.status_code == 200:
        users = response.json()["list"]
        return next((user for user in users if user["username"] == username), None)
    return None


def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    # Fetch the user from NocoDB
    user = get_user_from_nocodb(username)

    if user and user["password"] == password:
        session['user_id'] = user["Id"]
        session['username'] = user['username']
        session['role'] = user['role']
        session['name'] = user['name']
        session['email'] = user['email']
        session['cms_user'] = user['cms_user']
        session['cms_password'] = user['cms_password']
        
        if 'remember-me' in request.form:
            # Set a persistent HTTP cookie to maintain the user's logged-in state
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('remember-me', str(user["Id"]), max_age=86400 * 30)
            return resp
        else:
            # Clear the "remember-me" cookie if it exists
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('remember-me', '', max_age=0)
            return resp
        
        #flash(f"Logged in as {user['username']} with role {user['role']}", "success")
        #return redirect(url_for('index'))  # Redirect to the main page after successful login
    else:
        flash("Invalid username or password", "danger")
        return redirect(url_for('login'))  # Redirect back to the login page with an error message
