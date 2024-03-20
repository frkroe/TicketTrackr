import PyPDF2
import os
import re
import csv

# Get the directory path where the PDF files are stored.
pdf_dir = './emails'
print("working......")

def process_text_to_csv(text, csv_filename):
    # Extract timestamp
    timestamp_match = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', text)
    timestamp = timestamp_match.group(0) if timestamp_match else ''

    # Find all product lines
    product_lines = re.findall(r'(\d+)([A-Z ]+)([\d,]+)', text)

    # Prepare data for CSV
    csv_data = []
    for line in product_lines:
        quantity = line[0]
        description = line[1].strip()
        importe = line[2].replace(',', '.')
        
        if description:
            csv_data.append([description, quantity, importe, timestamp])

    # Write to CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Descripción', 'Cantidad', 'Importe', 'Timestamp'])  # CSV header
        writer.writerows(csv_data)

# Loop over all the files in the directory.
for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        # Open the PDF file in read binary mode.
        pdf_file = open(os.path.join(pdf_dir, filename), 'rb')

        # Read the PDF file using PyPDF2.
        pdf_reader = PyPDF2.PdfReader(pdf_file)  # Use PdfReader instead of PdfFileReader

        # Initialize an empty string for the extracted text.
        text = ''

        # Loop over each page in the PDF file and extract the text.
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()  # Use extract_text() method

        # Close the PDF file.
        pdf_file.close()

        # Process the extracted text to CSV
        csv_filename = os.path.splitext(os.path.join(pdf_dir, filename))[0] + '.csv'
        process_text_to_csv(text, csv_filename)

print("Processing completed.")
