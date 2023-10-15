import re
from io import BytesIO

import pandas as pd
import requests


class ExcelLoader:
    def __init__(self, file_path_or_url):
        self.file_path_or_url = file_path_or_url
        self.df = None
        self.load_excel()

    def load_excel(self):
        if re.match(r'^https?://', self.file_path_or_url):
            response = requests.get(self.file_path_or_url)
            response.raise_for_status()
            self.df = pd.read_excel(BytesIO(response.content))
        else:
            self.df = pd.read_excel(self.file_path_or_url)
        print("Excel sheet loaded!")

    def get_df(self):
        return self.df.copy()
