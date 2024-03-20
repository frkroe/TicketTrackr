import PyPDF2
import os
import re
import csv
import fastavro

# Get the directory path where the PDF files are stored.
pdf_dir = '../gmail_ticket_extraction/emails'
csv_dir = './csvs'
avro_dir = './avros'

def convert_pdf_to_text(filename):    
    # Open the PDF file in read binary mode.
    pdf_file = open(os.path.join(pdf_dir, filename), 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ''

    # Loop over each page in the PDF file and extract the text
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    pdf_file.close()
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
    
def extract_product_info_from_text(text):
    extracted_data = []
    start_extraction = False
    just_encountered = False
    lines = text.split('\n' ) # Split text into lines 

    # Extract timestamp
    timestamp_match = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', text)
    timestamp = timestamp_match.group(0) if timestamp_match else None
    
    # Extract the required info on bought products (BETWEEN 'Descripción P. Unit Importe' and 'TOTAL (€)') from the text
    for line in lines:
        if just_encountered:
            start_extraction = True # If we just encountered the line, start extraction from the next line
            just_encountered = False

        if 'Descripción P. Unit Importe' in line:
            just_encountered = True
            
        if 'TOTAL (€)' in line:
            break
        
        if start_extraction and line.strip():
            extracted_data.append(line.split())

    # Create a list of all the items in the nested data list
    items_strings_list = []

    for text_line in extracted_data:
        for item in text_line:
            items_strings_list.append(item)

    # Create a new list of lists, where each sublist contains info about one product
    product_list = []
    current_product_info_list = []
    current_sublist = []

    for item in items_strings_list:
        # Check if the item starts with both digits and letters and doesn't end with only 'G', 'KG', or 'L'
        if any(char.isdigit() for char in item) and any(char.isalpha() for char in item) and not any(suffix in item for suffix in ['KG', 'L', 'G']):
            if current_product_info_list:
                product_list.append(current_product_info_list)
                current_product_info_list = []
        current_product_info_list.append(item)

    if current_product_info_list:
        product_list.append(current_product_info_list)
    #print('Product as list extracted: ', product_list)

    # Transform the product list into a list of dictionaries
    product_info_list = []
    for product in product_list:
        product_info = dict()

        # Extract the units of each product bought
        unit_match = re.match(r'\d+', product[0])
        if unit_match:
            product_info["unit"] = int(unit_match.group())

        # Extract the price of each product bought (last element in the list)
        product_info["price"] = float(product[-1].replace(',', '.'))

        # Extract the name of each product bought
        name = ''
        for item in product:
            name_match = re.search(r'[A-Za-z]+', item)
            if name_match and name_match.group() not in ['kg', 'g', 'l']:
                name += ' ' + name_match.group()

        product_info["name"] = name.strip() # Remove leading space

        # Extract the weight info of each product bought, if it exists
        if '€/l' in product or '€/g' in product or '€/kg' in product:
            product_info["price_per_unit"] = {'price': float(product[-1].replace(',', '.')), 'unit': product[-2]}
            product_info["weight"] = {'weight': float(product[-5].replace(',', '.')), 'unit': product[-4]}
        else:
            product_info["price_per_unit"] = None

        #print('Product as dict transformed: ', product_info)
        product_info_list.append(product_info)

        # Add timestamp to each product info
        for product in product_info_list:
            product['timestamp'] = timestamp
    
    print('Product info list generated: ', product_info_list)
    return product_info_list

def main():
    # Create directories if they do not exist
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    if not os.path.exists(avro_dir):
        os.makedirs(avro_dir)

    # Loop over all the files in the directory.
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            # Extract text from PDF
            text = convert_pdf_to_text(filename)
            
            # Extract product info from text
            extracted_data = extract_product_info_from_text(text)

            # Save list of dictionaries to csv
            csv_filename = os.path.splitext(os.path.join(csv_dir, filename))[0] + '.csv'
            save_to_csv(csv_filename, extracted_data)

            # Save list of dictionaries to avro
            avro_filename = os.path.splitext(os.path.join(avro_dir, filename))[0] + '.avro'
            save_to_avro(avro_filename, extracted_data)


if __name__ == "__main__":
    main()