from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import os
import re

# Specify the directory where your PDFs are stored
pdf_dir = '../gmail_ticket_extraction/emails'

def convert_pdf_to_text_with_ocr(filename):
    pdf_file_path = os.path.join(pdf_dir, filename)
    
    images = convert_from_path(pdf_file_path)
    
    text = ''
    for image in images:

        #save image as png
        image.save(f'{filename}.png', 'PNG')

        # # Convert image to grayscale first
        # image = image.convert('L')
        
        # # Enhance the contrast on the grayscale image
        # image = ImageEnhance.Contrast(image).enhance(2)
        
        # # Then, if needed, binarize the image
        # image = image.point(lambda x: 0 if x<128 else 255, '1')
        
        # # Apply noise reduction
        # image = image.filter(ImageFilter.MedianFilter())
        
        # # Resize the image using Image.Resampling.LANCZOS for high-quality resampling
        # image = image.resize([2 * _ for _ in image.size], Image.LANCZOS)
        
        # Extract text using Tesseract OCR with custom configurations
        custom_config = r'--oem 3 --psm 6'
        text += pytesseract.image_to_string(image)
    
    return text
if __name__ == "__main__":
    filename = '20240316 Mercadona 103,45 €.pdf'
    # filename = '20240109 Mercadona 7,10 €.pdf'
    extracted_text = convert_pdf_to_text_with_ocr(filename)
    print(extracted_text)
