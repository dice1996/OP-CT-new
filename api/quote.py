import json
import sqlite3
from datetime import datetime as dt


class Quote:
    def __init__(self, form_data, user, row_id=None):
        self.customer = {
            'name': form_data.get('customer_name'),
            'oib': form_data.get('customer_oib'),
            'address': form_data.get('customer_address'),
            'phone': form_data.get('customer_phone'),
            'email': form_data.get('customer_email'),
        }
        self.products = [
            {
                'product_id': form_data.getlist('product_id[]')[i],
                'product_name': form_data.getlist('product_name[]')[i],
                'quantity': form_data.getlist('quantity[]')[i],
                'price': form_data.getlist('price[]')[i],
                'discount': form_data.getlist('rabat[]')[i],
                'note': form_data.getlist('note[]')[i],
            }
            for i in range(len(form_data.getlist('product_id[]')))
        ]
        self.napomena = form_data.get('napomena')
        self.date = dt.now().strftime("%d.%m.%Y")
        self.user = user
        self.row_id = row_id

    def save_to_db(self):
        conn = sqlite3.connect('quotes.db')
        c = conn.cursor()
        # Serialize the Python dictionary to a JSON-formatted string
        json_string = json.dumps(self.to_dict())

        if self.row_id is None:
            # Insert new record
            c.execute("INSERT INTO quotes (data) VALUES (?)", (json_string,))
            self.quote_id = c.lastrowid
        else:
            # Update existing record
            c.execute("UPDATE quotes SET data = ? WHERE id = ?", (json_string, self.row_id))
            self.quote_id = self.row_id

        try:
            conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)

        conn.close()

    def to_dict(self):
        return {
            'customer': self.customer,
            'products': self.products,
            'napomena': self.napomena,
            'datum': self.date,
            'operater': self.user
        }

    @staticmethod
    def format_offer_id(year, month, offer_id):
        year_str = str(year)[2:]  # Take the last two digits of the year
        month_str = str(month).zfill(2)  # Pad the month with zeros if necessary
        offer_id_str = str(offer_id).zfill(4)  # Pad the offer ID with zeros to have a length of 4
        return f"{year_str}{month_str}-WEB-{offer_id_str}", f"{year_str}{month_str}-{offer_id_str}"

    @staticmethod
    def get_offers(year=None, month=None):
        con = sqlite3.connect('quotes.db')
        cur = con.cursor()

        query = 'SELECT id, data FROM quotes'
        params = []

        if year or month:
            query += ' WHERE'
            if year:
                query += ' strftime("%Y", data) = ?'
                params.append(year)
            if month:
                if year:
                    query += ' AND'
                query += ' strftime("%m", data) = ?'
                params.append(month)

        cur.execute(query, params)
        rows = cur.fetchall()
        con.close()

        offers = []
        for row in rows:
            try:
                row_id = row[0]
                offer_id = row[0]
                # Replacing single quotes with double quotes before decoding
                offer_data_str = row[1].replace("'", '"')
                offer_data = json.loads(offer_data_str)
                # rest of your code
            except json.JSONDecodeError:
                print(f"Failed to decode JSON for row {row[0]}: {row[1]}")
                continue

            # Assuming that 'datum' in the offer_data is in the format 'dd.mm.yyyy'
            date_parts = offer_data['datum'].split('.')
            year = int(date_parts[2])
            month = int(date_parts[1])

            # Format the offer ID
            formatted_offer_id, _ = Quote.format_offer_id(year, month, offer_id)

            total_amount = 0
            for product in offer_data['products']:
                price = float(product['price'])
                quantity = float(product['quantity'])
                discount = float(product['discount']) if product[
                    'discount'] else 0.0  # discount might be an empty string
                discounted_price = price - (price * discount / 100.0)
                total_amount += discounted_price * quantity

            rounded_total_amount = "{:.2f}".format(round(total_amount, 2))  # Format to 2 decimal places
            offers.append({
                'row_id': row_id,
                'id': formatted_offer_id,
                'customer_name': offer_data['customer']['name'].upper(),
                'total_amount': rounded_total_amount
            })

        return offers

    @staticmethod
    def delete_from_db(row_id):
        conn = sqlite3.connect('quotes.db')
        c = conn.cursor()
        c.execute("DELETE FROM quotes WHERE rowid = ?", (row_id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, row_id):
        conn = sqlite3.connect('quotes.db')
        c = conn.cursor()

        c.execute("SELECT data FROM quotes WHERE rowid=?", (row_id,))
        row = c.fetchone()

        conn.close()

        if row:
            quote_data = row[0].replace("'", '"')
            # Assuming the data is stored as a JSON string, decode it back into a Python dict
            quote_dict = json.loads(quote_data)
            return quote_dict
        else:
            return None
