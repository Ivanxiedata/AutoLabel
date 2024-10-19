from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from googletrans import Translator
import pandas as pd
import io

class Label_Remarker:
    product_label_mapping = {
        '9868': '8689',
        '8689': '8689',
        '7652': '7652',
        '0090': '0090',
        '20091': '20091',
        'car': '20091',
        'Wrist': 'Wrist ball'
    }

    def find_column_name(self, df, search_term):
        # Search for a column name that contains the search term (case-insensitive)
        for col in df.columns:
            if search_term.lower() in col.lower():  # Case insensitive, partial match
                return col
        raise KeyError(f"Column containing '{search_term}' not found.")

    def contains_chinese(self, text):
        # Check if a string contains any Chinese characters
        return any('\u4e00' <= char <= '\u9fff' for char in text)

    def g_translator(self, product_name):
        # Translate product name if it contains Chinese characters
        if not product_name:
            print('Product name does not exist')
        eng_prod_name = product_name  # Default to original name if no translation needed
        translator = Translator()

        if self.contains_chinese(product_name):
            try:
                eng_prod_name = translator.translate(product_name, src='zh-cn', dest='en').text
            except Exception as e:
                print(f"Translation error: {e}")
        return eng_prod_name

    def validate_product_name(self, translated_product_name):
        # Validate product name by checking for partial matches in product_label_mapping
        for key in self.product_label_mapping:
            if key.lower() in translated_product_name.lower():
                return self.product_label_mapping[key]
        return translated_product_name

    def mark_pdf_with_product_name_and_quantity(self, input_pdf, output_pdf, excel_file):
        # Read the Excel file containing dynamic column names
        df = pd.read_excel(excel_file)

        # Dynamically find the column names for 'Product name' and 'The total'
        product_name_col = self.find_column_name(df, 'The title of the product')  # Adjust for partial matches
        quantity_col = self.find_column_name(df, 'The total')  # Partial match for 'The total'

        # Open the input PDF
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        # Ensure we don't process more pages than exist in either the PDF or the Excel file
        num_pages = len(reader.pages)
        num_rows = len(df)

        # Loop through each page and add the product name and quantity marking
        for i in range(min(num_pages, num_rows)):
            page = reader.pages[i]
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)

            # Check if the Product Name is valid (non-NaN) for the current row
            if pd.notna(df[product_name_col].iloc[i]):
                product_name = df[product_name_col].iloc[i]
                eng_product_name = self.g_translator(product_name)

                # Validate the translated product name using the mapping
                validated_eng_product_name = self.validate_product_name(eng_product_name)
                print(f'The validated product name is {validated_eng_product_name}')

                quantity = df[quantity_col].iloc[i]

                # Add Product Label and quantity in the red box area
                # Adjust X, Y coordinates to fit inside the red box on your label
                label_text = f"Product Label: {validated_eng_product_name}"
                quantity_text = f"Quantity: {quantity}"
                can.drawString(150, 260, label_text)
                can.drawString(150, 240, quantity_text)

            # Finalize the page and save the canvas
            can.showPage()
            can.save()

            # Move to the beginning of the StringIO buffer
            packet.seek(0)
            new_pdf = PdfReader(packet)

            # Merge the new content onto the first page
            page.merge_page(new_pdf.pages[0])

            # Add this page to the writer
            writer.add_page(page)

        # Write the modified PDF
        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

    def main(self):
        # Example usage
        input_pdf = "raw_label_input/label1.pdf"
        output_pdf = "marked_label_output/marked_labels_with_names.pdf"
        excel_file = "raw_label_input/raw_labels.xlsx"  # Excel file with dynamic column names
        self.mark_pdf_with_product_name_and_quantity(input_pdf, output_pdf, excel_file)


if __name__ == "__main__":
    label_remarker = Label_Remarker()
    label_remarker.main()
