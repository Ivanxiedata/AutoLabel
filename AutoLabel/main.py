from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from googletrans import Translator
from loguru import logger
import pandas as pd
import io
import PyPDF2
import re

class Label_Remarker:
    def __init__(self):
        logger.add('file.log', rotation='1 MB')

        self.product_label_mapping = {
            '9868': '8689',
            '8689': '8689',
            '7652': '7652',
            '0090': '0090',
            '20091': '20091',
            'Block Bigdi': '0090',
            '9686Technical': '8689',
            '7348': '7348',
            'Wrist': 'Wrist ball',
            'Glass':  'Glass oil',
            'Tree': '7652',
            'Storage Rack': 'Car Tray',
            'Steering wheel': 'Car Tray',
            'penyouhu': 'Glass oil',
            'wanliqiu': 'Wrist ball'

        }

    def count_pdf_pages(self,pdf_file):
        # Open the PDF file
        try:
            with open(pdf_file, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                # Get the total number of pages
                num_pages = len(reader.pages)
            logger.info('f"There are {num_pages} pages in the PDF file.")')
            return num_pages
        except Exception as e:
            logger.error(f"An error counting pages occurred in PDF {pdf_file}: {e}")
            return 0

    def find_column_name(self, df, search_term):
        logger.debug(f"Searching for column with term '{search_term}' in DataFrame columns: {df.columns.tolist()}")
        # Search for a column name that contains the search term (case-insensitive)
        for col in df.columns:
            if search_term.lower() in col.lower(): # Case insensitive, partial match
                logger.info(f"Found column '{col}' for search term '{search_term}'.")
                return col
        logger.error(f"Column containing '{search_term}' not found.")
        raise KeyError(f"Column containing '{search_term}' not found.")

    def contains_chinese(self, text):
        # Check if a string contains any Chinese characters
        return any('\u4e00' <= char <= '\u9fff' for char in text)

    def g_translator(self, product_name):
        # Translate product name if it contains Chinese characters
        if not product_name:
            print('Product name does not exist')
            logger.info(f"Product name does not exist.")
        eng_prod_name = product_name  # Default to original name if no translation needed
        translator = Translator()

        if self.contains_chinese(product_name):
            try:
                eng_prod_name = translator.translate(product_name, src='zh-cn', dest='en').text
                logger.info(f"Translated product progress completed.")
            except Exception as e:
                print(f"Translation error: {e}")
                logger.error(f"Translated product progress failed.")
        return eng_prod_name

    def translate_dataframe(self, df):
        # Translate column names
        logger.info(f"Translating dataframe.")
        translated_cols = []
        for col in df.columns:
            translated_col = self.g_translator(col)  # Use the existing g_translator method
            translated_cols.append(translated_col)

        # Assign the translated column names to the DataFrame
        df.columns = translated_cols

        # Translate values in specific columns, if required (e.g., 'Product name')
        for col in df.columns:
            if df[col].dtype == object:  # Only process columns with object type (likely strings)
                df[col] = df[col].apply(
                    lambda x: self.g_translator(str(x)) if pd.notna(x) and self.contains_chinese(str(x)) else x)
        logger.info(f"Translating dataframe completed.")
        return df



    def mapping_product_name(self, translated_product_name):
        # Validate product name by checking for partial matches in product_label_mapping
        for key in self.product_label_mapping:
            if key.lower() in translated_product_name.lower():
                return self.product_label_mapping[key]
        return translated_product_name

    def split_order_numbers(self, df, order_col = 'Order Number'):
        if order_col in df.columns:
            df[order_col] = df[order_col].astype(str).str.split()
            df = df.explore(order_col).reset_index(drop=True)
        else:
            print('no need to splot order numbers')
        return df

    def detect_and_relabel_product_names_with_quantity(self, product_info):
        """
        Detects and splits product names with quantities from a formatted string.
        """

        #split the input string by newline character
        product_lines = product_info.strip().split('\n')

        #initialize an empty list to store the relabeled products
        relabeled_products = []

        for line in product_lines:
            match = re.match(r"(\S+)\*(\d+)", line.strip())
            if match:
                product_name = match.group(1)
                quantity = match.group(2)
                relabeled_products.append((product_name, quantity))
            else:
                logger.warning(f"Failed to parse line: {line}")

        logger.info(f"Relabeled products: {relabeled_products}")
        return relabeled_products


    def mark_pdf_with_product_name_and_quantity(self, input_pdf, output_pdf, excel_file):
        # Read the Excel file containing dynamic column names
        df = pd.read_excel(excel_file)

        df = self.translate_dataframe(df)
        print(f'translated dataframe:\n {df}')
        df = self.split_order_numbers(df, order_col='Order Number')


        # Dynamically find the column names for 'Product name' and 'The total'
        product_name_col = self.find_column_name(df, 'Multi -name')  # Adjust for partial matches
        quantity_col = self.find_column_name(df, 'Total product')  # Partial match for 'The total'

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
            can.setFont("Helvetica", 6)

            # Check if the Product Name is valid (non-NaN) for the current row
            if pd.notna(df[product_name_col].iloc[i]):
                product_info = df[product_name_col].iloc[i]
                products_with_quantities = self.detect_and_relabel_product_names_with_quantity(product_info)

                # Add each product name and quantity to the PDF
                for idx, (product, qty) in enumerate(products_with_quantities):
                    validated_product = self.mapping_product_name(product)
                    label_text = f"Product Label: {validated_product}"
                    quantity_text = f"Quantity: {qty}"
                    y_offset = 260 - (idx * 10)  # Adjust Y-coordinate for each product
                    can.drawString(200, y_offset, label_text)
                    can.drawString(200, y_offset -35, quantity_text)


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
        output_pdf = "marked_label_output/marked_new_labels.pdf"
        excel_file = "raw_label_input/label1.xlsx"  # Excel file with dynamic column names
        self.mark_pdf_with_product_name_and_quantity(input_pdf, output_pdf, excel_file)
        total_pages = self.count_pdf_pages(input_pdf)
        print(f"Total number of pages in the PDF: {total_pages}")


if __name__ == "__main__":
    label_remarker = Label_Remarker()
    label_remarker.main()
