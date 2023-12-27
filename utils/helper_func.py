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
            lambda row: ["{} | {}".format(title, int(ean) if pd.notna(ean) else 'Fali EAN')
                         for title, ean in zip(row['Naslov'], row['EAN'])
                         if not re.search(pattern, title)], axis=1)

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
        # Initialize dictionaries to track locations that can fulfill the entire order
        suitable_locations = {location: 0 for location in location_columns}
        lowest_stock_at_location = {location: float('inf') for location in location_columns}

        for ean_code, quantity_required in zip(ean_codes, ordered_quantities):
            if pd.isna(ean_code):
                print("Encountered NaN EAN code")
                return None, None
            product_query = re.escape(str(int(ean_code)))
            filtered_df = df[
                df['Barcode1500'].astype(str).str.contains(product_query, na=False)
            ]

            if filtered_df.empty:
                print(f"No product found for EAN '{ean_code}'")
                return None, None

            for location in location_columns:
                available_quantity = float(filtered_df.iloc[0][location].replace('\t', '').replace(',', '.'))
                if available_quantity >= quantity_required:
                    suitable_locations[location] += available_quantity
                    lowest_stock_at_location[location] = min(lowest_stock_at_location[location], available_quantity)
                else:
                    # Mark location as unsuitable by setting its lowest stock to zero
                    lowest_stock_at_location[location] = 0

        # Filter out locations that cannot fulfill the entire order or have any product with zero stock
        suitable_locations = {loc: stock for loc, stock in suitable_locations.items() if lowest_stock_at_location[loc] > 0}

        if not suitable_locations:
            print("No single location can fulfill the entire order.")
            return None, None

        # Find the location with the highest stock among suitable ones
        best_location = max(suitable_locations, key=suitable_locations.get)
        min_max_quantity = lowest_stock_at_location[best_location]

        # Decrement stock for the chosen location
        for ean_code, quantity_required in zip(ean_codes, ordered_quantities):
            product_query = re.escape(str(int(ean_code)))
            row_index = df[df['Barcode1500'].astype(str).str.contains(product_query, na=False)].index[0]
            updated_quantity = max(0, float(df.at[row_index, best_location].replace('\t', '').replace(',', '.')) - quantity_required)
            df.at[row_index, best_location] = str(updated_quantity).replace('.', ',')

        return best_location.strip(), min_max_quantity




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
