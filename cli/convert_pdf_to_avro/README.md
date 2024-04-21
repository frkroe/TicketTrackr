# PDF to CSV to Avro

This is a simple example of how to convert a PDF file to a CSV file and then to an Avro file.

## Setup

1. Make sure to have given access to your Gmail account and have downloaded the PDF files from the emails. If not, run the code in the [gmail_ticket_extraction directory](../gmail_ticket_extraction/).

2. In a virtual environment, install the required packages and run the code.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Run the code
python pdf_to_csv_to_avro.py

# Deactivate the virtual environment
deactivate
```

## Code Structure

- The `pdf_to_csv_to_avro.py` file contains the code to convert a PDF file both to a CSV file and to an Avro file.

