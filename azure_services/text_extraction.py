import PyPDF2
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
#from config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, SEARCH_SERVICE_ENDPOINT, SEARCH_API_KEY, SEARCH_INDEX_NAME

def extract_text_from_pdf_with_pypdf2(local_path):
    with open(local_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        total_pages = len(pdf_reader.pages)
        print(f"Total pages in PDF: {total_pages}")

        all_text = ""
        for page_num in range(total_pages):
            if page_num % 10 == 0:
                print(f"Processing page {page_num+1}/{total_pages}...")
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    all_text += text + "\n\n"
            except Exception as e:
                print(f"Error extracting page {page_num}: {str(e)}")

        print(f"Extracted {len(all_text)} characters of text")
        return all_text

# Function that combines PyPDF2 with Form Recognizer for better results
def extract_text_from_pdf(local_path):
    # First try with PyPDF2 for bulk extraction
    text_from_pypdf2 = extract_text_from_pdf_with_pypdf2(local_path)

    # If PyPDF2 extraction seems insufficient, try Form Recognizer for selected pages
    if len(text_from_pypdf2) < 10000:  # If text seems too short
        print("PyPDF2 extraction may be incomplete, using Form Recognizer for selected pages...")
        document_analysis_client = DocumentAnalysisClient(
            endpoint=FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(FORM_RECOGNIZER_KEY)
        )

        # Process sample pages with Form Recognizer
        with open(local_path, "rb") as pdf_file:
            try:
                poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_file)
                result = poller.result()

                form_recognizer_text = ""
                for page in result.pages:
                    for line in page.lines:
                        form_recognizer_text += line.content + "\n"

                # If Form Recognizer produced more text, use it instead
                if len(form_recognizer_text) > len(text_from_pypdf2):
                    print(f"Using Form Recognizer text ({len(form_recognizer_text)} chars) instead of PyPDF2 text ({len(text_from_pypdf2)} chars)")
                    return form_recognizer_text
            except Exception as e:
                print(f"Form Recognizer error: {str(e)}")

    return text_from_pypdf2

