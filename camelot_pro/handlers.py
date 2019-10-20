import os
import shutil
import tempfile

import requests
import PyPDF2


class PDFSpliter:
    """
    Handle PDF work
    """
    def __enter__(self):
        return self

    def __init__(self, filepath: os.PathLike, pages: str, password=""):
        self.filepath = filepath
        self.password = password
        self.temp_dir = tempfile.mkdtemp()
        if self.filepath.startswith(("http://", "https://")):
            self.filepath = self.download_file(self.filepath)
        self.pages = pages
        # Save time by using the real file,
        # if no password needed and "all" pages
        # or an image file
        if all([not password, pages == "all"]) or not self.filepath.lower().endswith(".pdf"):
            pass
        else:
            print("[Info]: Aggregating user defined pages..", self.pages)
            gather_pages = self._get_pages(filepath, pages)
            self.filepath = self.pdf_separator(gather_pages)

    def pdf_separator(self, gather_pages: set):
        merged_pdf = os.path.join(self.temp_dir, str(self.pages) + os.path.basename(self.filepath))
        with open(merged_pdf, 'wb') as out_file:
            pdf_reader = PyPDF2.PdfFileReader(self.filepath)
            if pdf_reader.isEncrypted:
                pdf_reader.decrypt(self.password)
            pdf_writer = PyPDF2.PdfFileWriter()
            for page in gather_pages:
                try:
                    pdf_writer.addPage(pdf_reader.getPage(page-1))
                except IndexError:
                    raise EOFError(f"File has only {pdf_reader.numPages} pages, but asked for {self.pages}")
            pdf_writer.write(out_file)
        return merged_pdf

    def _get_pages(self, filepath: os.PathLike, pages: str) -> set:
        # Credits to camelot library - lifted and customized
        """Converts pages string to list of ints.

        Parameters
        ----------
        filepath : Pathlike
            Filepath or URL of the PDF file.
        pages : str, optional (default: '1')
            Comma-separated page numbers.
            Example: '1,3,4' or '1,4-end' or 'all'.

        Returns
        -------
        P : list
            List of int page numbers.

        """
        page_numbers = []
        pages_needed = []

        if pages == "1":
            page_numbers.append({"start": 1, "end": 1})
        else:
            with open(filepath, "rb") as file_obj:
                infile = PyPDF2.PdfFileReader(file_obj, strict=False)
                if infile.isEncrypted:
                    infile.decrypt(self.password)
                if pages == "all":
                    page_numbers.append({"start": 1, "end": infile.getNumPages()})
                else:
                    for r in pages.split(","):
                        if "-" in r:
                            a, b = r.split("-")
                            if b == "end":
                                b = infile.getNumPages()
                            page_numbers.append({"start": int(a), "end": int(b)})
                        else:
                            page_numbers.append({"start": int(r), "end": int(r)})

        for p in page_numbers:
            pages_needed.extend(range(p["start"], p["end"] + 1))

        return set(pages_needed)

    def download_file(self, url: str):
        """
        Download file to local
        :param url: PDF file path
        :return: downloaded file local filepath
        """
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            _, r_ext = r.headers['Content-Type'].rsplit('/', 1)
            fname, f_ext = os.path.basename(url).rsplit('.', 1)
            ext = r_ext if r_ext else f_ext
            ext = ext.lower()
            # TODO use filetype lib to find extension
            tmp_fname = os.path.join(self.temp_dir, f"{fname}.{ext}")
            with open(tmp_fname, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:   # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
        return tmp_fname

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)
