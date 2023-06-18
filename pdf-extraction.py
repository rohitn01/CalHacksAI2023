import PyPDF2

pdf_file_path = 'sample-pdf.pdf'
paragraphs_per_section = 3

def extract_paragraphs_from_pdf(pdf_file_path, paragraphs_per_section=3):
    pdf_file = open(pdf_file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    num_pages = len(pdf_reader.pages)
    extracted_paragraphs = []
    current_section_paragraphs = []
    section_counter = 0

    for page_number in range(num_pages):
        page = pdf_reader.pages[page_number]
        text = page.extract_text()

        paragraphs = text.split('\n\n')  

        for paragraph in paragraphs:
            if paragraph.strip():
                current_section_paragraphs.append(paragraph.strip())

                if len(current_section_paragraphs) == paragraphs_per_section:
                    extracted_paragraphs.append(current_section_paragraphs)
                    current_section_paragraphs = []
                    section_counter += 1

    pdf_file.close()

    return extracted_paragraphs

if __name__ == "__main__":

    extracted_paragraphs = extract_paragraphs_from_pdf(pdf_file_path, paragraphs_per_section)

    for section, paragraphs in enumerate(extracted_paragraphs):
        print(f"Section {section + 1}:")
        for paragraph in paragraphs:
            print(paragraph)
        print()