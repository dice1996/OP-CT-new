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
    def edit_data(df_orders_all, df_records):
        # Regular expression pattern for titles containing 'Bonus' and 'Zaštita'
        pattern = r'(?i).*Bonus.*Zaštita.*'
        bonus_pattern = r'B\d+'

        # Merge with the records to get the record ID
        df_parsed = df_records[["Broj_narudzbe", "record_id"]]
        df_merged = pd.merge(df_parsed, df_orders_all, left_on='Broj_narudzbe', right_on='Broj', how='left')

        # Group by 'Broj_narudzbe' and aggregate the necessary information
        df_grouped = df_merged.groupby('Broj_narudzbe').agg({
            'record_id': 'first',  # Assuming the record_id is the same for all products in the order
            'Email': 'first',  # Assuming the email is the same for all products in the order
            'Status': 'first',  # Assuming the status is the same for all products in the order
            'Naslov': lambda x: list(x.unique()),  # Creates a list of unique product titles in the order
            'EAN': lambda x: list(x.unique()),  # Creates a list of unique EANs in the order
            'Naručena količina': lambda x: list(x)  # Creates a list of quantities for each product in the order
        }).reset_index()

        # Combine product title and EAN into a single string for each product
        df_grouped['Naslov_EAN'] = df_grouped.apply(
            lambda row: ["{} | {}".format(title, str(int(ean)))
                         for title, ean in zip(row['Naslov'], row['EAN'])
                         if not re.search(bonus_pattern, title)],axis=1)

        # Flag and list the types of 'Bonus Zaštita'        
        df_grouped['Bonus_Zaštita'] = df_grouped.apply(
            lambda row: ', '.join(set(re.findall(bonus_pattern, ' '.join(row['Naslov'])))), axis=1)

        # Function to filter out 'Bonus Zaštita' and return the remaining items
        def filter_bonus_zaštita(titles, eans):
            filtered_titles = []
            filtered_eans = []
            for title, ean in zip(titles, eans):
                if not re.search(pattern, title):
                    filtered_titles.append(title)
                    filtered_eans.append(ean)
            return filtered_titles, filtered_eans

        # Apply the filtering function and update 'Naslov' and 'EAN'
        df_grouped[['Naslov', 'EAN']] = df_grouped.apply(
            lambda row: filter_bonus_zaštita(row['Naslov'], row['EAN']), axis=1, result_type='expand')

        # Drop the 'Broj' column if it's no longer needed
        df_grouped.drop(columns=['Broj'], inplace=True, errors='ignore')

        return df_grouped

    @staticmethod
    def get_common_location_for_products(df, ean_codes, ordered_quantities, location_columns):
        # Initialize minimum quantities for each location
        location_min_quantities = {location: float('inf') for location in location_columns}

        # Store rows corresponding to the products for potential stock update
        product_rows = []

        for ean_code, quantity_required in zip(ean_codes, ordered_quantities):
            product_query = re.escape(str(int(ean_code)))
            filtered_df = df[
                df['Barcode1500'].astype(str).str.contains(product_query, na=False)
            ]

            if filtered_df.empty:
                print(f"No product found for EAN '{ean_code}'")
                return None

            # Store the row for later stock update
            product_rows.append((filtered_df.iloc[0], quantity_required))
            
            # Inside the loop for each product
            for location in location_min_quantities.keys():
                available_quantity = float(filtered_df.iloc[0][location].replace('\t', '').replace(',', '.'))
                if available_quantity >= quantity_required:
                    location_min_quantities[location] = min(location_min_quantities[location], available_quantity)
        
        # Finding the best location
        best_location = None
        max_min_quantity = -1
        for location, quantity in location_min_quantities.items():
            if quantity != float('inf') and quantity > max_min_quantity:
                max_min_quantity = quantity
                best_location = location
        
        if max_min_quantity == float('inf') or max_min_quantity <= 0:
            return None

        # Decrement stock for the chosen location based on ordered quantities
        for product_row, quantity_required in product_rows:
            current_quantity = float(product_row[best_location].replace('\t', '').replace(',', '.'))
            updated_quantity = current_quantity - quantity_required
            df.loc[product_row.name, best_location] = str(updated_quantity).replace('.', ',')

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
