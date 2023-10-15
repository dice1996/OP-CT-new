import base64
from io import BytesIO

from pdf417gen import encode, render_image


class PaymentBarcode:

    def __init__(self, payment_params):
        self.payment_params = payment_params

    def generate_barcode(self):
        # Combine the data into a single string with LF (Line Feed) as the separator
        encoded_data = '\n'.join(self.payment_params)
        # Encode JSON string to PDF417 barcode
        codes = encode(encoded_data)

        # Generate the barcode image
        image = render_image(codes)

        # Convert the image to a base64 string
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # Create an HTML img tag with the base64 string
        img_tag = f'<img src="data:image/png;base64,{img_str}" alt="2D Barcode" style="width: 150px;">'

        return img_str
