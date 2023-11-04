import os
import sqlite3
from base64 import b64encode
from datetime import datetime, timedelta
from functools import wraps

from envparse import env
from flask import Flask, jsonify, request, render_template, flash, session, redirect, url_for, make_response
from flask_cors import CORS
from flask_weasyprint import HTML

from api.Barcode import PaymentBarcode
from api.loginService import authenticate
from api.product import ProductAPI
from api.quote import Quote
from utils.excel_loader import ExcelLoader
from utils.helper_func import Helpers

# postavljanje radne datoteke
os.chdir('C:/Users/dinoc/Documents/PyProjects/OP-CT - NEW')

env.read_envfile('.env')

# Inicijaliziraj Flask i omogući CORS
app = Flask(__name__)
CORS(app)
app.secret_key = env.str("SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=72)

# Inicijaliziraj globalne varijable za pomoćne funkcije
helpers = Helpers()


def init_db():
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL
        );
    ''')
    c.execute('''
            CREATE TABLE IF NOT EXISTS status_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_updated BOOLEAN NOT NULL,
                last_update_time TEXT NOT NULL
            );
        ''')
    conn.commit()
    conn.close()


init_db()


def reload_database():
    global excel_loader, df, product_api
    try:
        excel_loader = ExcelLoader(env.str("EXCEL_URL"))
        df = excel_loader.get_df()
        product_api = ProductAPI(df)
        # Insert a new status update entry into the SQLite database
        conn = sqlite3.connect('quotes.db')
        c = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        is_updated = True
        c.execute('''
                    INSERT INTO status_updates (is_updated, last_update_time) 
                    VALUES (?, ?)
                ''', (is_updated, current_time))
        conn.commit()
        conn.close()

        print("Data reloaded successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Dekorator za provjeru je li korisnik prijavljen
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.pop("user_id")
    session.pop("username")
    session.pop("role")
    session.pop("name")
    session.pop("email")
    session.pop("cms_user")
    session.pop("cms_password")
    return redirect(url_for("login"))


# Prikazuje login stranicu
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return authenticate()
    return render_template('login.html')


@app.route('/reload', methods=['GET'])
@login_required
def reload_data():
    if session['role'] == "admin":
        reload_database()
        flash("Data reloaded successfully.", "success")
    return redirect(url_for('index'))


@app.route('/reload-no-auth-needed-1S252E2255DFR', methods=['GET'])
def reload_data_no_auth():
    reload_database()
    flash("Data reloaded successfully.", "success")
    return 'success', 200


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template("zalihe.html", active2="", active1="active", active3="")


@app.route('/messages', methods=['GET'])
@login_required
def mess():
    return render_template("mess.html", active2="", active1="active", active3="")


@app.route('/quote', methods=['GET'])
@login_required
def quote():
    if session["role"] == "admin" or session["role"] == "user":
        year = request.args.get('year')
        month = request.args.get('month')
        offers = Quote.get_offers(year, month)
        return render_template('quote.html', offers=offers, active2="active", active1="")
    else:
        return render_template("zalihe.html", active2="", active1="active", active3="")


@app.route('/get_status', methods=['GET'])
@login_required
def get_status():
    # Connect to the SQLite database
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()

    # Get the latest status update entry
    c.execute('''
        SELECT is_updated, last_update_time FROM status_updates ORDER BY id DESC LIMIT 1
    ''')
    status = c.fetchone()
    conn.close()

    # Check if there was a status update entry
    if status:
        # Return the status as a JSON response
        return jsonify({
            'success': True,
            'is_updated': status[0],
            'last_update_time': status[1]
        })
    else:
        # If no status is found, return an error message
        return jsonify({
            'success': False,
            'message': 'No status updates found.'
        })


@app.route('/create_quote', methods=['POST'])
@login_required
def create_quote():
    try:
        row_id = request.form.get('row_id', None)
        if row_id == '':
            row_id = None

        # Save data to the database
        data_quote = Quote(request.form, session["name"], row_id=row_id)
        data_quote.save_to_db()

        # Convert the saved data to dictionary
        data_dict = data_quote.to_dict()

        # Fetch data to populate into the HTML template
        customer_data = data_dict.get('customer')
        products_data = data_dict.get('products')
        additional_data = {
            'datum': data_dict.get('datum'),
            'operater': data_dict.get('operater'),
            'napomena': data_dict.get('napomena')
        }

        # Calculate the total amount with tax
        total_amount_with_tax = sum(float(product['price']) * float(product['quantity']) for product in products_data)

        # Calculate the discount amount with tax
        discount_amount_with_tax = sum(
            float(product['price']) * float(product['quantity']) * float(product['discount']) / 100 for product in
            products_data if 'discount' in product and product['discount']
        )

        # Calculate Osnovica by removing 25% tax
        osnovica = round((total_amount_with_tax - discount_amount_with_tax) / 1.25, 2)

        # Calculate PDV (25% tax amount)
        pdv = round(total_amount_with_tax - osnovica - discount_amount_with_tax, 2)

        # Calculate Rabat by subtracting 25% tax
        rabat = round(discount_amount_with_tax, 2)

        # Calculate Iznos (Grand Total)
        iznos = round(total_amount_with_tax - discount_amount_with_tax, 2)

        price_wo_pdv = round()

        # Convert Grand Total to Eurocents
        eurocents = int(iznos * 100)
        formatted_eurocents = str(eurocents).rjust(15, '0')
        print(eurocents / 100)

        offer_id, offer_id_str = helpers.format_offer_id(datetime.now().year, datetime.now().month, data_quote.quote_id)

        data = [
            "HRVHUB30",
            "EUR",
            f"{formatted_eurocents}",
            f"{customer_data['name'].strip().upper()}",
            "",  # ulica
            "",  # zip grad (31000 OSIJEK)
            "CENTAR TEHNIKE d.o.o za trgovinu",
            "ŽUPANIJSKA 31",
            "31000 OSIJEK",
            "HR3323400091110533041",
            "HR00",
            f"{offer_id_str}",
            "OTHR",
            f"PLAĆANJE PO PONUDI {offer_id}"
        ]

        img_str = PaymentBarcode(data).generate_barcode()

        rendered = render_template('quote_template.html',
                                   offer_id=offer_id,
                                   offer_id_str=offer_id_str,
                                   img_str=img_str,
                                   customer=customer_data,
                                   additional=additional_data,
                                   products=products_data,
                                   total_amount=osnovica,
                                   discount_amount=rabat,
                                   tax_amount=pdv,
                                   grand_total_amount=iznos)

        # Generate PDF
        pdf = HTML(string=rendered).write_pdf()

        # Convert PDF to base64
        pdf_base64 = b64encode(pdf).decode("utf-8")
        return jsonify({"message": "Quote created", "quote_id": offer_id, "pdf_base64": pdf_base64})
    except Exception as e:
        print(f"An error occurred: {e}")


@app.route('/download/<quote_id>')
@login_required
def download_pdf(quote_id):
    try:
        data_dict = Quote.get_by_id(quote_id)

        if data_dict is None:
            return jsonify({"error": "Quote not found"}), 404

        # Fetch data to populate into the HTML template
        customer_data = data_dict.get('customer')
        products_data = data_dict.get('products')
        additional_data = {
            'datum': data_dict.get('datum'),
            'operater': data_dict.get('operater'),
            'napomena': data_dict.get('napomena')
        }

        # Calculate the total amount with tax
        total_amount_with_tax = sum(float(product['price']) * float(product['quantity']) for product in products_data)

        # Calculate the discount amount with tax
        discount_amount_with_tax = sum(
            float(product['price']) * float(product['quantity']) * float(product['discount']) / 100 for product in
            products_data if 'discount' in product and product['discount']
        )

        # Calculate Osnovica by removing 25% tax
        osnovica = round((total_amount_with_tax - discount_amount_with_tax) / 1.25, 2)

        # Calculate PDV (25% tax amount)
        pdv = round(total_amount_with_tax - osnovica - discount_amount_with_tax, 2)

        # Calculate Rabat by subtracting 25% tax
        rabat = round(discount_amount_with_tax, 2)

        # Calculate Iznos (Grand Total)
        iznos = round(total_amount_with_tax - discount_amount_with_tax, 2)

        # Convert Grand Total to Eurocents
        eurocents = int(iznos * 100)
        formatted_eurocents = str(eurocents).rjust(15, '0')
        print(eurocents / 100)

        datum_str = data_dict.get('datum', '')

        # Parse the date string into a datetime object
        try:
            datum = datetime.strptime(datum_str, '%d.%m.%Y')
            year = datum.year
            month = datum.month
        except ValueError:
            # Handle invalid date format
            print("Invalid date format")
            year, month = datetime.now().year, datetime.now().month

        # Now you can use 'year' and 'month' in your function
        offer_id, offer_id_str = helpers.format_offer_id(year, month, quote_id)

        data = [
            "HRVHUB30",
            "EUR",
            f"{formatted_eurocents}",
            f"{customer_data['name'].strip().upper()}",
            "",  # ulica
            "",  # zip grad (31000 OSIJEK)
            "CENTAR TEHNIKE d.o.o za trgovinu",
            "ŽUPANIJSKA 31",
            "31000 OSIJEK",
            "HR3323400091110533041",
            "HR00",
            f"{offer_id_str}",
            "OTHR",
            f"PLAĆANJE PO PONUDI {offer_id}"
        ]

        img_str = PaymentBarcode(data).generate_barcode()

        rendered = render_template('quote_template.html',
                                   offer_id=offer_id,
                                   offer_id_str=offer_id_str,
                                   img_str=img_str,
                                   customer=customer_data,
                                   additional=additional_data,
                                   products=products_data,
                                   total_amount=osnovica,
                                   discount_amount=rabat,
                                   tax_amount=pdv,
                                   grand_total_amount=iznos)

        # Generate PDF
        pdf = HTML(string=rendered).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={offer_id}.pdf'

        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while generating the PDF"}), 500


@app.route('/quote/<int:row_id>', methods=['DELETE'])
@login_required
def delete_quote(row_id):
    Quote.delete_from_db(row_id)
    return jsonify({"status": "success"}), 200


@app.route('/quote/<int:row_id>', methods=['GET'])
@login_required
def get_quote(row_id):
    quote = Quote.get_by_id(row_id)  # Assuming get_by_id is a method in your Quote class
    if quote:
        return jsonify(quote)
    else:
        return jsonify({"error": "Quote not found"}), 404


@app.route('/quote/update', methods=['GET'])
@login_required
def update_quote():
    quote = Quote.get_offers()
    if quote:
        return jsonify(quote)
    else:
        return jsonify({"error": "Quote not found"}), 404


@app.route('/api/product_quantities', methods=['POST'])
@login_required
def get_product_quantities():
    product_query = request.json.get('product_query', '')
    return jsonify(product_api.get_product_quantities(product_query))


@app.route('/api/product_suggestions', methods=['POST'])
@login_required
def get_product_suggestions():
    product_query = request.json.get('product_query', '')
    return jsonify(product_api.get_product_suggestions(product_query))


# @app.route('/api/update_user_data', methods=['POST'])
# @login_required
# def update_user_data():
#     # Extract the new values from the incoming request
#     cms_user = request.json.get('cms_user')
#     cms_password = request.json.get('cms_password')
#
#     # Assuming 'username' is a unique identifier in your database
#     user_identifier = session.get('user_id')
#
#     # Prepare the data for updating in the NocoDB database
#     updated_data = {
#         "cms_user": cms_user,
#         "cms_password": cms_password
#     }
#
#     # Use the NocodbConnector to update the data
#     response = nocodb_api.update_user_data(user_identifier, updated_data)
#
#     if response.status_code == 200:
#         session['cms_user'] = cms_user
#         session['cms_password'] = cms_password
#
#     return str(response.status_code)


if __name__ == "__main__":
    app.run(host=env.str("FLASK_HOST"), port=env.str("FLASK_PORT"), debug=True, use_reloader=False, threaded=True)
