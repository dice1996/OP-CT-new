from pyairtable import Table
import pandas as pd


class AirtableData:
    def __init__(self, api_key, base_id, table_name):
        self.table = Table(api_key, base_id, table_name)

    def get_records_from_view(self, view_name):
        records = self.table.all(view=view_name)
        return records

    def get_dataframe_from_view(self, view_name):
        records = self.get_records_from_view(view_name)
        # Convert the list of records (dictionaries) into a DataFrame
        df = pd.DataFrame([record['fields'] for record in records])
        return df

    def print_dataframe_as_json(self, view_name):
        df = self.get_dataframe_from_view(view_name)
        print(df.to_json(orient='records', lines=True))

