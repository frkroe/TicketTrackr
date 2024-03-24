from pdf2image import convert_from_path
import pytesseract
import os
import re

# Get the directory path where the PDF files are stored.
csv_dir = './csvs'
avro_dir = './avros'

class ProductParser:
    pdf_dir = ''
    filename = None
    text = '' # str() no le gusta a Miguel

    product_dict = {
        'cantidad': None,
        'descripcion': None,
        'peso': None,
        'unidad_kilitro': None, # kilitro: kg o l
        'precio_unitario': None,
        'precio_kilitro': None,
        'unidad_precio_kilitro': None,
        'importe': None,
        'timestamp': None
    }

    def __init__(self, file_path):
        self.file_path = file_path

    def convert_pdf_to_text(self):    
        # Convert PDF to a list of image objects
        _images = convert_from_path(self.file_path)
        # Iterate through each image and extract text using Tesseract OCR
        for image in _images:
            self.text += pytesseract.image_to_string(image)    

    def get_product_lines(self):
        lines = [[line] for line in self.text.splitlines()]
        for number, line in enumerate(lines):
            line_text = line[0] 
            if 'Descripcion P. Unit' in line_text:
                initial_product_line = number + 1
            if 'TOTAL (' in line_text:
                final_product_line = number
                break
        product_lines = list(map(lambda sublist: 
                                [item.replace(',', '') 
                                for item in sublist], 
                                lines[initial_product_line:final_product_line]))
        return product_lines

    def get_timestamp(self):
        # Extract timestamp
        timestamp_match = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', self.text)
        self.product_dict['timestamp'] = timestamp_match.group(0) if timestamp_match else None

    def get_quantity(self, product_info):
        quant_pattern = r'^(\d{1,3})\s'
        for info in product_info:
            if re.search(quant_pattern, info):
                self.product_dict['cantidad'] = re.search(quant_pattern, info).group(1)

    def get_and_convert_price(self, product_info):
        # Regex pattern for price
        price_pattern = r"\s(\S+\d{2})$" 
        for info in product_info:
            match = re.search(price_pattern, info)
            if match and '.' not in match.group(1):
                result = format(float(match.group(1))/100, '.2f')
                self.product_dict['importe'] = result
                product_info[0] = re.sub(price_pattern, f" {str(result)}", info)
            else:
                self.product_dict['importe'] = None
                
    def get_and_convert_price_per_unit(self, product_info):
        # Regex pattern for quantity and price per unit
        quantity_pattern = r'^(\d{1,3})\s'
        price_per_unit_pattern = r"\s([\d.]+)\s\d+\.\d+$"
        for info in product_info:
            match = re.search(quantity_pattern, info)
            if match and int(match.group(1)) > 1 and re.search(price_per_unit_pattern, info):
                match_price_per_unit = re.search(price_per_unit_pattern, info)
                if match_price_per_unit and '.' not in match_price_per_unit.group(1):
                    result = str(format(float(match_price_per_unit.group(1))/100, '.2f'))
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
                result_weight = format(float(match_weight.group(1))/1000, '.3f')
                # Convert variable price to float
                match_variable_price = re.search(variable_price_pattern, info)
                result_variable_price = format(float(match_variable_price.group(1))/100, '.2f')
                self.product_dict['peso'] = result_weight
                self.product_dict['unidad_kilitro'] = 'kg'
                self.product_dict['precio_kilitro'] = result_variable_price
                self.product_dict['unidad_precio_kilitro'] = '€/kg'
                product_info[0] = re.sub(variable_price_pattern, f"{str(result_variable_price)}", info)
                product_info[0] = re.sub(weight_pattern, f"{str(result_weight)} ", info)
            else:
                self.product_dict['peso'] = None
                self.product_dict['unidad_kilitro'] = None
                self.product_dict['precio_kilitro'] = None
                self.product_dict['unidad_precio_kilitro'] = None

    def get_description(self, product_info):
        desc_pattern = r'^\d*\s([+\-%A-Za-z0-9 /%º.,-ñáéíóúÁÉÍÓÚüÜ]+?)(?=\s\d+\.\d{2})'
        quant_pattern = r'^(\d{1,3})\s'
        for info in product_info:
            print(info)
            if info == 'PESCADO':
                self.product_dict['descripcion'] = None
                pass
            elif  re.match(r'\d+\.\d{3}', info):
                pass
            elif re.match(r'^[\w\s]*[a-zA-Z]$', info):
                info = re.sub(quant_pattern, '', info)
                self.product_dict['descripcion'] = info
            else:
                self.product_dict['descripcion'] = re.search(desc_pattern, info).group(1)

if __name__ == "__main__":
    filename = '20240316 Mercadona 103,45 €.pdf'
    pdf_dir = '../gmail_ticket_extraction/emails'
    product_list = list()
    file_path = os.path.join(pdf_dir, filename)
    product = ProductParser(file_path)

    product.convert_pdf_to_text()
    product.get_timestamp()
    product_lines = product.get_product_lines()
    for product_info in product_lines:
        product.get_quantity(product_info)
        product.get_and_convert_price(product_info)
        product.get_and_convert_price_per_unit(product_info)
        product.get_and_convert_weight_and_variable_price(product_info)
        product.get_description(product_info)
        if product.product_dict['importe']:
            product_list.append(product.product_dict)
    