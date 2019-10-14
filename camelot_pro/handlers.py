import os
import shutil
import tempfile

import PyPDF2
from camelot.handlers import PDFHandler

# TODO : Limit the file
# TODO: Make it easy to check the credits


class PDFSpliter:
    """
    Handle PDF work
    """
    def __enter__(self):
        return self

    def __init__(self, filepath, pages, password=""):
        # TODO: Remove the dependency of camelot.PDFHandler
        self.filepath = filepath
        self.pages = pages
        # Save time by using the real file,
        # if path exists and no password needed and "all" pages
        # or an image file
        if all([os.path.exists(filepath), not password, pages == "all"]) or not filepath.lower().endswith(".pdf"):
            self.temp_dir = ""
        else:
            print("[Info]: Aggregating user defined pages..", self.pages)
            self.temp_dir = tempfile.mkdtemp()
            self.pdf_handle = PDFHandler(filepath, pages, password)
            self.filepath = self.pdf_handle.filepath
            self.filepath = self.pdf_separator()

    def pdf_separator(self):
        merged_pdf = os.path.join(self.temp_dir, "ProTable_" + str(self.pages) + os.path.basename(self.filepath))
        with open(merged_pdf, 'wb') as out_file:
            pdf_reader = PyPDF2.PdfFileReader(self.filepath)
            pdf_writer = PyPDF2.PdfFileWriter()
            for page in self.pdf_handle.pages:
                pdf_writer.addPage(pdf_reader.getPage(page-1))
            pdf_writer.write(out_file)
        return merged_pdf

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)
