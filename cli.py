import argparse
import logging
import os
import subprocess
import yaml

from dotenv import load_dotenv

logger = logging.getLogger('cli')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

dotenv_path = "../secrets/.env"
load_dotenv(dotenv_path)


class TicketTrackrETL:

    def gmail_tickets_extraction(self):
        subprocess.run(['python3', './gmail_tickets_extraction/main.py'], check=True)

    def convert_pdf_to_avro(self, pdf_dir):
        os.environ['PDF_DIR'] = pdf_dir
        subprocess.run(['python3', './convert_pdf_to_avro/main.py'], check=True)

    def upload_files_to_nas(self, avro_dir):
        os.environ['AVRO_DIRECTORY'] = avro_dir
        subprocess.run(['python3', './upload_files_to_nas/main.py'], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gmail_tickets_extraction",
                        action="store_true",
                        help="Execute gmail tickets extraction")
    parser.add_argument("--convert_pdf_to_avro",
                        action="store_true",
                        help="Execute convert pdfs to avros")
    parser.add_argument("--upload_files_to_nas",
                        action="store_true",
                        help="Execute uplaod files to nas")
    args = parser.parse_args()
    ticket_tracker = TicketTrackrETL()
    if args.gmail_tickets_extraction:
        logger.info('Starting gmail ticket extraction')
        ticket_tracker.gmail_tickets_extraction()
    if args.convert_pdf_to_avro:
        logger.info('Starting conversion from pdf to avro')
        pdf_dir = '../gmail_ticket_extraction/emails'
        ticket_tracker.convert_pdf_to_avro(pdf_dir)
    if args.upload_files_to_nas:
        logger.info('Starting load of files to NAS')
        avro_dir = ''
        ticket_tracker.upload_files_to_nas(avro_dir)
