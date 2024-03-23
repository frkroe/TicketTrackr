from pdf2image import convert_from_path
import pytesseract
import os
import re
import csv
import fastavro

# Get the directory path where the PDF files are stored.
pdf_dir = '../gmail_ticket_extraction/emails'
csv_dir = './csvs'
avro_dir = './avros'


def convert_pdf_to_text(filename):    
    pdf_file_path = os.path.join(pdf_dir, filename)
    
    # Convert PDF to a list of image objects
    images = convert_from_path(pdf_file_path)

    text = ''
    # Iterate through each image and extract text using Tesseract OCR
    for image in images:
        text += pytesseract.image_to_string(image)

    return text

def save_to_csv(filename, extracted_data):
    keys = ['timestamp','name', 'unit', 'price', 'price_per_unit', 'weight']

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        for data_dict in extracted_data:
            writer.writerow({key: data_dict.get(key, '') for key in keys})

def save_to_avro(filename, extracted_data):
    schema = {
        "type": "record",
        "name": "Product",
        "fields": [
            {"name": "unit", "type": "int"},
            {"name": "price", "type": "float"},
            {"name": "name", "type": "string"},
            {"name": "price_per_unit", "type": ["null", {
                "type": "record",
                "name": "PricePerUnit",
                "fields": [
                    {"name": "price", "type": "float"},
                    {"name": "unit", "type": "string"}
                ]
            }]},
            {"name": "timestamp", "type": "string"},
            {"name": "weight", "type": ["null", {
                "type": "record",
                "name": "Weight",
                "fields": [
                    {"name": "weight", "type": "float"},
                    {"name": "unit", "type": "string"}
                ]
            }]}
        ]
    }

    with open(filename, 'wb') as file:
        fastavro.writer(file, schema, extracted_data)

def get_timestamp(text):
    # Extract timestamp
    timestamp_match = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', text)
    return timestamp_match.group(0) if timestamp_match else None

def get_product_lines(text):
    lines = [[line] for line in text.splitlines()]

    for number, line in enumerate(lines):
        line_text = line[0] 
        if 'Descripcion P. Unit Importe' in line_text:
            initial_product_line = number + 1
        if 'TOTAL (' in line_text:
            final_product_line = number
            break

    # Replacing , by . in all floats in the list and getting only those lines that correspond to products
    product_lines = list(map(lambda sublist: 
                            [item.replace(',', '.') 
                            for item in sublist], 
                            lines[initial_product_line:final_product_line]))

    
    return product_lines

def parser_product_lines(list_products: list)->list:
    parsed_lines = []

    # pattern_cantidad = r'^(\d+)(?!\.\d+)(?=[A-Za-z+*])'
    pattern_cantidad = r'^(\d+)\s'
    pattern_descripcion = r'^\d*([+\-%A-Za-z0-9 /%º.,-ñáéíóúÁÉÍÓÚüÜ]+?)(?=\s\d+\.\d{2})'


    for line in list_products:
        default_keys = {
            'cantidad': None,
            'descripcion': None,
            'peso_volumen': None,
            'unidades': None,
            'precio_unidad': None,
            'unidades_p_unidad': None,
            'importe': None
        }

        content = line[0]
        # Skip specific cases
        if content == 'PESCADO' or re.match(r'^\d+\.\d+\s*(kg|l)', content):
            continue
        if re.search(pattern_cantidad, content):
            default_keys['cantidad'] = re.search(pattern_cantidad, content).group(1)

        if re.search(pattern_descripcion, content):
            default_keys['descripcion'] = re.search(pattern_descripcion, content).group(1)
        
        parsed_lines.append(default_keys)

    return parsed_lines


# def extract_product_info_from_text(text):
#     extracted_data = []
#     start_extraction = False
#     just_encountered = False
#     lines = text.split('\n' ) # Split text into lines 


    
#     # Extract the required info on bought products (BETWEEN 'Descripción P. Unit Importe' and 'TOTAL (€)') from the text
#     for line in lines:
#         if just_encountered:
#             start_extraction = True # If we just encountered the line, start extraction from the next line
#             just_encountered = False

#         if 'Descripción P. Unit Importe' in line:
#             just_encountered = True
            
#         if 'TOTAL (€)' in line:
#             break
        
#         if start_extraction and line.strip():
#             extracted_data.append(line.split())

#     # Create a list of all the items in the nested data list
#     items_strings_list = []

#     for text_line in extracted_data:
#         for item in text_line:
#             items_strings_list.append(item)

#     # Create a new list of lists, where each sublist contains info about one product
#     product_list = []
#     current_product_info_list = []
#     current_sublist = []

#     for item in items_strings_list:
#         # Check if the item starts with both digits and letters and doesn't end with only 'G', 'KG', or 'L'
#         if any(char.isdigit() for char in item) and any(char.isalpha() for char in item) and not any(suffix in item for suffix in ['KG', 'L', 'G']):
#             if current_product_info_list:
#                 product_list.append(current_product_info_list)
#                 current_product_info_list = []
#         current_product_info_list.append(item)

#     if current_product_info_list:
#         product_list.append(current_product_info_list)
#     print('Product as list extracted: ', product_list)

#     # Transform the product list into a list of dictionaries
#     product_info_list = []
#     for product in product_list:
#         product_info = dict()

#         # Extract the units of each product bought
#         unit_match = re.match(r'\d+', product[0])
#         if unit_match:
#             product_info["unit"] = int(unit_match.group())

#         # Extract the price of each product bought (last element in the list)
#         product_info["price"] = float(product[-1].replace(',', '.'))

#         # Extract the name of each product bought
#         name = ''
#         for item in product:
#             name_match = re.search(r'[A-Za-z]+', item)
#             if name_match and name_match.group() not in ['kg', 'g', 'l']:
#                 name += ' ' + name_match.group()

#         product_info["name"] = name.strip() # Remove leading space

#         # Extract the weight info of each product bought, if it exists
#         if '€/l' in product or '€/g' in product or '€/kg' in product:
#             product_info["price_per_unit"] = {'price': float(product[-1].replace(',', '.')), 'unit': product[-2]}
#             product_info["weight"] = {'weight': float(product[-5].replace(',', '.')), 'unit': product[-4]}
#         else:
#             product_info["price_per_unit"] = None

#         #print('Product as dict transformed: ', product_info)
#         product_info_list.append(product_info)

#         # Add timestamp to each product info
#         for product in product_info_list:
#             product['timestamp'] = timestamp
    
#     print('Product info list generated: ', product_info_list)
#     return product_info_list

# def main():
#     # Create directories if they do not exist
#     if not os.path.exists(csv_dir):
#         os.makedirs(csv_dir)

#     if not os.path.exists(avro_dir):
#         os.makedirs(avro_dir)

#     # Loop over all the files in the directory.
#     for filename in os.listdir(pdf_dir):
#         if filename.endswith('.pdf'):
#             print(f"filename: {filename}")
#             # Extract text from PDF
#             text = convert_pdf_to_text(filename)
            
#             # Extract product info from text
#             extracted_data = extract_product_info_from_text(text)

#             # Save list of dictionaries to csv
#             csv_filename = os.path.splitext(os.path.join(csv_dir, filename))[0] + '.csv'
#             save_to_csv(csv_filename, extracted_data)

#             # Save list of dictionaries to avro
#             avro_filename = os.path.splitext(os.path.join(avro_dir, filename))[0] + '.avro'
#             save_to_avro(avro_filename, extracted_data)


if __name__ == "__main__":
    filename = '20240316 Mercadona 103,45 €.pdf'
    # filename = '20240320 Mercadona 11,02 €.pdf'
    text = convert_pdf_to_text(filename)
    print(text)
    time_stamp = get_timestamp(text)
    product_lines = get_product_lines(text)
    print(product_lines)
    parsed_lines = parser_product_lines(product_lines)
    # print(parsed_lines)
    for item in parsed_lines:
        print(f"Cantidad: {item['cantidad']}, Descripcion: {item['descripcion']}")
    dict_count = len([item for item in parsed_lines if isinstance(item, dict)])
    print(dict_count)
