import PyPDF2


def count_pdf_pages(pdf_file):
    # Open the PDF file
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        # Get the total number of pages
        num_pages = len(reader.pages)

    return num_pages


# Example usage
pdf_file = "raw_label_input/label1.pdf"  # Path to your PDF file
total_pages = count_pdf_pages(pdf_file)
print(f"Total number of pages in the PDF: {total_pages}")
