import re

import pandas as pd


class Helpers:
    def __init__(self):
        pass

    @staticmethod
    def format_offer_id(year, month, offer_id):
        year_str = str(year)[2:]  # Take the last two digits of the year
        month_str = str(month).zfill(2)  # Pad the month with zeros if necessary
        offer_id_str = str(offer_id).zfill(4)  # Pad the offer ID with zeros to have a length of 4
        return f"{year_str}{month_str}-WEB-{offer_id_str}", f"{year_str}{month_str}-{offer_id_str}"

    @staticmethod
    def edit_data(df_orders_all, df_products_all, df_records):
        # Regular expression pattern for titles containing 'Bonus' and 'Zaštita'
        pattern = r'(?i).*Bonus.*Zaštita.*'

        # Filter out rows in df_orders_all that match the pattern
        df_orders_filtered = df_orders_all[~df_orders_all['Naslov'].str.contains(pattern, regex=True)]

        # Merge with the records to get the record ID
        df_parsed = df_records[["Broj_narudzbe", "record_id"]]
        df_merged = pd.merge(df_parsed, df_orders_filtered, left_on='Broj_narudzbe', right_on='Broj', how='left')

        # Merge with the products to get the product codes
        df_merged = df_merged.merge(df_products_all[['Naslov', 'Šifra / kat. broj ***']], on='Naslov', how='left')

        # Group by 'Broj_narudzbe' and aggregate the necessary information
        df_grouped = df_merged.groupby('Broj_narudzbe').agg({
            'record_id': 'first',  # assuming the record_id is the same for all products in the order
            'Email': 'first',  # assuming the email is the same for all products in the order
            'Naslov': lambda x: list(x.unique()),  # creates a list of unique product titles in the order
            'Šifra / kat. broj ***': lambda x: list(x.unique())  # creates a list of unique product codes in the order
        }).reset_index()

        # Rename columns as necessary
        df_grouped.rename(columns={'Šifra / kat. broj ***': 'Sifra'}, inplace=True)

        # Drop the 'Broj' column if it's no longer needed
        df_grouped.drop(columns=['Broj'], inplace=True, errors='ignore')

        return df_grouped

    @staticmethod
    def get_common_location_for_products(df, product_codes, location_columns):
        # This dictionary will store the minimum available quantity for each location
        location_min_quantities = {location: float('inf') for location in location_columns}

        product_rows = []  # This will store the rows of the products found

        for product_code in product_codes:
            product_query = re.escape(str(product_code))
            filtered_df = df[
                df['Artikl4000'].str.contains(product_query, case=False, na=False) |
                df['Sifra1000'].astype(str).str.contains(product_query, na=False) |
                df['Barcode1500'].astype(str).str.contains(product_query, na=False)
                ]

            if filtered_df.empty:
                print(f"No product found for code '{product_code}'")
                return None

            product_data = filtered_df.iloc[0]
            product_rows.append(product_data)

            for location in location_min_quantities.keys():
                quantity = float(product_data[location].replace('\t', '').replace(',', '.'))
                if 1 <= quantity < location_min_quantities[location]:
                    location_min_quantities[location] = quantity
                elif quantity < 1:
                    location_min_quantities[location] = 0  # Ignore locations with insufficient quantity

        # Find the location with the highest minimum quantity
        best_location = None
        max_min_quantity = -1
        for location, quantity in location_min_quantities.items():
            if quantity > max_min_quantity:
                max_min_quantity = quantity
                best_location = location

        if max_min_quantity == float('inf') or max_min_quantity == 0:
            return None

        # Decrement the stock in the dataframe
        for product_row in product_rows:
            current_quantity = float(product_row[best_location].replace('\t', '').replace(',', '.'))
            if current_quantity >= 1:
                df.loc[product_row.name, best_location] = str(current_quantity - 1).replace('.', ',')

        return best_location.strip(), max_min_quantity

    @staticmethod
    def map_locations(data):
        location_mapping = {
            "000 VELEPRODAJA 10700": "VP",
            "002 REZ. DIJELOVI0700": "VP",
            "001 CENTAR TEHNIKE 001 OSIJEK0700": "Osijek",
            "002 CENTAR TEHNIKE 002 VALPOVO0700": "Valpovo",
            "004 CENTAR TEHNIKE 004 ĐAKOVO0700": "Đakovo",
            "005 CENTAR TEHNIKE 005 NAŠICE0700": "Našice",
            "006 CENTAR TEHNIKE 006 SLAVONSKI BROD0700": "Slavonski Brod",
            "008 CENTAR TEHNIKE 008 BELI MANASTIR0700": "Beli Manastir",
            "009 CENTAR TEHNIKE 009 VUKOVAR0700": "Vukovar"
        }
        data['location'] = data['location'].map(location_mapping)
        return data
