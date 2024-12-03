from PyPDF2 import PdfReader
from refextract import extract_references_from_string

# Charger le PDF et extraire son texte
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

pdf_path = 'data/2024.nlp4call-1.15.pdf'
pdf_text = extract_text_from_pdf(pdf_path)

# Extraire les références à partir du texte
references = extract_references_from_string(pdf_text)
for ref in references:
    print(ref)