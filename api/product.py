import re
# Defining the ProductAPI class

class ProductAPI:
    def __init__(self, dataframe):
        self.df = dataframe

    def get_product_quantities(self, product_query):
        product_query = re.escape(product_query.lower())

        # Filter the dataframe for the product
        filtered_df = self.df[
            self.df['Artikl4000'].str.lower().str.contains(product_query) |
            self.df['Sifra1000'].astype(str).str.contains(product_query) |
            self.df['Barcode1500'].astype(str).str.contains(product_query)]

        if not filtered_df.empty:
            product_data = filtered_df.iloc[0]
            product_quantities = {}
            # Get quantities from different locations
            for col in self.df.columns[23:46]:
                # Convert int64 to int before sending in response
                product_quantities[col] = self.string_to_int(product_data[col])
            response_data = {
                'product_name': product_data['Artikl4000'],
                'quantities': product_quantities,
                'sifra': int(product_data['Sifra1000']),
                'ean': int(product_data['Barcode1500'])
            }
            return response_data, 200
        else:
            # Debug information to check the input and dataframe
            return {
                'error': 'Product not found',
                'input_query': product_query,
                'df_sample': self.df.head().to_dict(orient='records')
            }, 404

    def get_product_suggestions(self, product_query):
        product_query = product_query.lower()
        queries = product_query.split('+')

        # Start with the full dataframe
        filtered_df = self.df.copy()

        # Iteratively filter the dataframe for each term
        for query in queries:
            filtered_df = filtered_df[
                filtered_df['Artikl4000'].str.lower().str.contains(query) |
                filtered_df['Sifra1000'].astype(str).str.contains(query) |
                filtered_df['Barcode1500'].astype(str).str.contains(query)
                ]

        # Take the top 20 matches
        top_matches = filtered_df.head(30)

        # Extract relevant information
        suggestions = []
        for _, row in top_matches.iterrows():
            product_name = row['Artikl4000']
            if len(product_name) > 60:  # Truncate long product names
                product_name = product_name[:57] + '...'
            suggestions.append({
                'product_name': product_name,
                'product_id': row['Sifra1000'],
                'barcode': row['Barcode1500']
            })

        return {'products': suggestions}, 200

    def string_to_int(self, s: str) -> int:

        float_value = float(s.strip().replace(',', '.'))
        return int(round(float_value))
