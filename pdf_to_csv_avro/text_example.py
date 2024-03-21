import PyPDF2
import os

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

        # Write to CSV
    with open("Output.txt", "w") as text_file:
        text_file.write(text)

    pdf_file.close()
    return text

if __name__ == "__main__":
    filename = '20240219 Mercadona 24,08 €.pdf'
    convert_pdf_to_text(filename)