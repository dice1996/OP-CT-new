import pandas as pd
from pyairtable import Table


class AirtableData:
    def __init__(self, api_key, base_id, table_name):
        self.table = Table(api_key, base_id, table_name)

    def get_records_from_view(self, view_name):
        records = self.table.all(view=view_name)
        return records

    def get_dataframe_from_view(self, view_name):
        records = self.get_records_from_view(view_name)
        # Convert the list of records (dictionaries) into a DataFrame
        df = pd.DataFrame([record['fields'] for record in records if 'Status' not in record['fields']])
        # Check if DataFrame is empty
        if df.empty:
            return None
        else:
            return df

    def print_dataframe_as_json(self, view_name):
        df = self.get_dataframe_from_view(view_name)
        print(df.to_json(orient='records', lines=True))

    def update_record(self, data):
        for index, row in data.iterrows():
            status = "U obradi"
            record_id = row['record_id']

            # Replace NaN values with None
            email = row['Email'] if pd.notnull(row['Email']) else None
            location = [row['location']] if pd.notnull(row['location']) and row['location'] != 'None' else []
            note = None if pd.isna(row.get('note', None)) else row.get('note', None)

            product_titles = row['Naslov']
            products_formatted = '\n'.join([f"- {title.upper()}" for title in product_titles])

            if not location:
                status = "Nema stanja"

            data1 = {
                'Email': email,
                'Mjesto_slanja': location,
                'Zadnji': note,
                'Status': status,
                'Proizvodi': products_formatted
                # Add other fields you want to update
            }
            try:
                self.table.update(record_id, data1)
                # print(f"Record {record_id} updated successfully.")
            except Exception as e:
                print(f"Failed to update record {record_id}: {e}")

    def update_products(self, data):
        for index, row in data.iterrows():
            record_id = row['record_id']

            # Replace NaN values with None
            email = row['Email'] if pd.notnull(row['Email']) else None
            product_titles = row['Naslov']
            products_formatted = '\n'.join([f"- {title.upper()}" for title in product_titles])

            data1 = {
                'Email': email,
                'Proizvodi': products_formatted
                # Add other fields you want to update
            }
            try:
                self.table.update(record_id, data1)
                # print(f"Record {record_id} updated successfully.")
            except Exception as e:
                print(f"Failed to update record {record_id}: {e}")