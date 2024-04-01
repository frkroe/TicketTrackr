import os
import re

import fastavro
import pytesseract
from pdf2image import convert_from_path

# Get the directory path where the PDF files are stored.
csv_dir = './convert_pdf_to_avro/csvs'
avro_dir = './convert_pdf_to_avro/avros'


class ProductParser:
    pdf_dir = ''
    filename = None
    product_dict = dict()

    def __init__(self, file_path=None):
        self.file_path = file_path
        # Your predefined field types
        self.field_types = {
            'cantidad': 'int',
            'importe': 'float',
            'precio_unitario': 'float',
            'peso': 'float',
            'unidad_kilitro': 'string',
            'precio_kilitro': 'float',
            'unidad_precio_kilitro': 'string',
            'descripcion': 'string',
            'timestamp': 'string'
        }

        def _create_avro_schema(self):
            _fields = []
            for field, type_str in self.field_types.items():
                avro_type = type_str
                # Map Python types to Avro types
                if type_str == 'int':
                    avro_type = 'int'
                elif type_str == 'float':
                    avro_type = 'float'
                elif type_str == 'string':
                    avro_type = 'string'
                _fields.append({"name": field, "type": [avro_type, "null"]})
            schema = {
                "type": "record",
                "name": "Item",
                "fields": _fields
            }
            return schema
        self.schema = _create_avro_schema(self)

    def convert_pdf_to_text(self):
        text = ''
        # Convert PDF to a list of image objects
        _images = convert_from_path(self.file_path)
        # Iterate through each image and extract text using Tesseract OCR
        for image in _images:
            text += pytesseract.image_to_string(image)
        return text

    def get_product_lines(self, text):
        lines = [[line] for line in text.splitlines()]
        for number, line in enumerate(lines):
            line_text = line[0]
            if 'Descrip' in line_text:
                initial_product_line = number + 1
            if 'TOTAL' in line_text:
                final_product_line = number
                break
        product_lines = list(map(lambda sublist: [
            item.replace(',', '') for item in sublist],
            lines[initial_product_line:final_product_line]))
        product_lines = [sublist for sublist in product_lines
                         if any(item.strip() for item in sublist)]
        return product_lines

    def get_timestamp(self, text):
        # Extract timestamp
        timestamp_match = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', text)
        return timestamp_match.group(0) if timestamp_match else None

    def get_quantity(self, product_info):
        quant_pattern = r'^(\d{1,3})\s'
        for info in product_info:
            if re.search(quant_pattern, info):
                self.product_dict['cantidad'] = int(re.
                                                    search(quant_pattern, info).group(1))
            else:
                self.product_dict['cantidad'] = 1

    def get_and_convert_price(self, product_info):
        # Regex pattern for price
        price_pattern = r"\s(\S+\d{2})$"
        for info in product_info:
            match = re.search(price_pattern, info)
            if match and '.' not in match.group(1):
                result = str(format(float(match.group(1)) / 100, '.2f'))
                self.product_dict['importe'] = float(result)
                product_info[0] = re.sub(price_pattern, f" {result}", info)
            else:
                self.product_dict['importe'] = None

    def get_and_convert_price_per_unit(self, product_info):
        # Regex pattern for quantity and price per unit
        quantity_pattern = r'^(\d{1,3})\s'
        price_per_unit_pattern = r"\s([\d.]+)\s\d+\.\d+$"
        for info in product_info:
            match = re.search(quantity_pattern, info)
            if match and int(match.group(1)) > 1 and \
                    re.search(price_per_unit_pattern, info):
                match_price_per_unit = re.search(price_per_unit_pattern, info)
                if match_price_per_unit and '.' not in match_price_per_unit.group(1):
                    result = str(format(
                        float(match_price_per_unit.group(1)) / 100, '.2f'))
                    self.product_dict['precio_unitario'] = float(result)
                    product_info[0] = re.sub(price_per_unit_pattern, f" {result}", info)
            else:
                self.product_dict['precio_unitario'] = None

    def get_and_convert_weight_and_variable_price(self, product_info):
        # Regex pattern for variable price (e.g. 1,50€/kg)
        variable_price_pattern = r"^\d+\s+[a-zA-Z]+\s+(\d+)"
        weight_pattern = r'^(\d+)\s'

        for info in product_info:
            match_weight = re.search(weight_pattern, info)
            if match_weight and len(match_weight.group(1)) > 3:
                # Convert weight to float
                result_weight = format(float(match_weight.group(1)) / 1000, '.3f')
                # Convert variable price to float
                match_variable_price = re.search(variable_price_pattern, info)
                result_variable_price = format(
                    float(match_variable_price.group(1)) / 100, '.2f')
                self.product_dict['peso'] = float(result_weight)
                self.product_dict['unidad_kilitro'] = 'kg'
                self.product_dict['precio_kilitro'] = float(result_variable_price)
                self.product_dict['unidad_precio_kilitro'] = '€/kg'
                product_info[0] = re.sub(variable_price_pattern,
                                         f"{str(result_variable_price)}", info)
                product_info[0] = re.sub(weight_pattern, f"{str(result_weight)} ", info)
            else:
                self.product_dict['peso'] = None
                self.product_dict['unidad_kilitro'] = None
                self.product_dict['precio_kilitro'] = None
                self.product_dict['unidad_precio_kilitro'] = None

    def get_description(self, product_info):
        desc_pattern = r'^\d*\s([+\-%A-Za-z0-9 /%º*.,-ñáéíóúÁÉÍÓÚüÜ]+?)(?=\s\d+\.\d{2})'
        quant_pattern = r'^(\d{1,3})\s'
        for info in product_info:
            # Skip if info start with a weight with 3 decimal places (e.g. 1.456)
            # Skip if info contains 'PESCADO'
            if info == 'PESCADO' or re.match(r'^\d+\.\d{3}', info):
                continue

            # Add description for variable price products, deleting quantity
            elif re.match(r'^[\w\s.,]*[a-zA-Z]+$', info):
                info = re.sub(quant_pattern, '', info)
                self.product_dict['descripcion'] = info

            # Add description for fixed price products
            else:
                self.product_dict['descripcion'] = re.search(desc_pattern, info).group(1)


if __name__ == "__main__":
    pdf_dir = os.getenv('PDF_DIR')
    for file in os.listdir(pdf_dir):
        if file.endswith('.pdf'):
            print(f"Processing file: {file}")
            product_list = list()
            file_path = os.path.join(pdf_dir, file)
            product = ProductParser(file_path)
            text = product.convert_pdf_to_text()
            timestamp = product.get_timestamp(text)
            product_lines = product.get_product_lines(text)
            for product_info in product_lines:
                product.get_quantity(product_info)
                product.get_and_convert_price(product_info)
                product.get_and_convert_price_per_unit(product_info)
                product.get_and_convert_weight_and_variable_price(product_info)
                product.get_description(product_info)
                if product.product_dict['importe']:
                    product.product_dict['timestamp'] = timestamp
                    product_list.append(product.product_dict)
                    product.product_dict = {}
            print(product_list)

            with open(f'{avro_dir}/{file.replace(".pdf", ".avro")}', 'wb') as f:
                fastavro.writer(f, product.schema, product_list)
