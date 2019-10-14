"""
Purpose: To create a Doppelganger objects
"""

import pandas as pd
from camelot.core import TableList


class Table(object):
    """Defines a table with coordinates relative to a left-bottom
    origin. (PDF coordinate space)

    Attributes
    ----------
    flavor: str
        Default "CamelotPro", certainly!!
    df : :class:`pandas.DataFrame`
    cols : int
        Number of columns in the table
    rows : int
        Number of rows in the table
    shape : tuple
        Shape of the table.
    accuracy : float
        Accuracy of text assignment to the cell
    accuracy_character : float
        Accuracy of Characters recognized from the image
    accuracy_layout : float
        Accuracy of table layout's design decision
    whitespace : float
        Percentage of Error in Character recognition
    order : int
        Table number on PDF page.
    page : int
        PDF page number.

    """

    def __init__(self, pro_table):
        self.flavor = "CamelotPro"
        self.df = pd.DataFrame.from_dict(pro_table["TableJson"]).T
        self.rows, self.cols = self.shape = self.df.shape
        self.cells = self.df.size
        self.accuracy = self.accuracy_layout = round(pro_table["LayoutConfidence"], 2)
        self.accuracy_character = round(pro_table["CharacterConfidence"], 2)
        self.whitespace = round(100 - self.accuracy_character, 2)
        self.order = pro_table["Order"]
        self.page = pro_table["Page"]

    def __repr__(self):
        return "<{} shape={}>".format(self.__class__.__name__, self.shape)

    def __lt__(self, other):
        if self.page == other.page:
            if self.order < other.order:
                return True
        elif self.page < other.page:
            return True

    @property
    def data(self):
        """Returns two-dimensional list of strings in table.
        """
        return self.df.values.tolist()

    @property
    def parsing_report(self):
        """Returns a parsing report with %accuracy, %whitespace,
        table number on page and page number.
        """
        report = {
            "accuracy": round(self.accuracy, 2),
            "whitespace": round(self.whitespace, 2),
            "order": self.order,
            "page": self.page,
        }
        return report

    def set_all_edges(self):
        """Sets all table edges to True.
        """
        return self

    def set_edges(self):
        """Sets a cell's edges to True depending on whether the cell's
        coordinates overlap with the line's coordinates within a
        tolerance.
        """
        return self

    def set_border(self):
        """Sets table border edges to True.
        """
        return self

    def set_span(self):
        """Sets a cell's hspan or vspan attribute to True depending
        on whether the cell spans horizontally or vertically.
        """
        return self

    def to_csv(self, path, **kwargs):
        """Writes Table to a comma-separated values (csv) file.

        For kwargs, check :meth:`pandas.DataFrame.to_csv`.

        Parameters
        ----------
        path : str
            Output filepath.

        """
        kw = {"encoding": "utf-8", "index": False, "header": False, "quoting": 1}
        kw.update(kwargs)
        self.df.to_csv(path, **kw)

    def to_json(self, path, **kwargs):
        """Writes Table to a JSON file.

        For kwargs, check :meth:`pandas.DataFrame.to_json`.

        Parameters
        ----------
        path : str
            Output filepath.

        """
        kw = {"orient": "records"}
        kw.update(kwargs)
        json_string = self.df.to_json(**kw)
        with open(path, "w") as f:
            f.write(json_string)

    def to_excel(self, path, **kwargs):
        """Writes Table to an Excel file.

        For kwargs, check :meth:`pandas.DataFrame.to_excel`.

        Parameters
        ----------
        path : str
            Output filepath.

        """
        kw = {
            "sheet_name": "page-{}-table-{}".format(self.page, self.order),
            "encoding": "utf-8",
        }
        kw.update(kwargs)
        writer = pd.ExcelWriter(path)
        self.df.to_excel(writer, **kw)
        writer.save()

    def to_html(self, path, **kwargs):
        """Writes Table to an HTML file.

        For kwargs, check :meth:`pandas.DataFrame.to_html`.

        Parameters
        ----------
        path : str
            Output filepath.

        """
        html_string = self.df.to_html(**kwargs)
        with open(path, "w") as f:
            f.write(html_string)

    def to_sqlite(self, path, **kwargs):
        """Writes Table to sqlite database.

        For kwargs, check :meth:`pandas.DataFrame.to_sql`.

        Parameters
        ----------
        path : str
            Output filepath.

        """
        import sqlite3
        kw = {"if_exists": "replace", "index": False}
        kw.update(kwargs)
        conn = sqlite3.connect(path)
        table_name = "page-{}-table-{}".format(self.page, self.order)
        self.df.to_sql(table_name, conn, **kw)
        conn.commit()
        conn.close()


def table_list(gp_response):
    """
    Convert Camelot GoPro's response to Camelot's TableList type object
    :param gp_response: Response received from Camelot GoPro
    :return: Camelot's TableList like object with extra

      Attributes
    ----------
    Regular Camelot's TableList object
    Pages: int
            Total number of input pages in pdf or 1 if image
    JobStatus    : str ('Success'|'Failed'|'Processing'|'Incomplete')
                Job status of finding tables
    """
    prev_page = 0
    order = 1
    if gp_response["JobStatus"].lower().startswith("succe"):
        pass
    elif gp_response["JobStatus"].lower().startswith("process"):
        print("-=- "*15)
        print(f'[Info]: Table Extraction process is {gp_response["JobStatus"]}')
        print("Check more info using '__dict__' descriptor on the result object.")
        print("Use the 'JobId' from the response, to check and retrieve the output when the 'Processing' is 'Success'")
        print("JobId is:", gp_response["JobId"])
        print("Follow the last step in link: "
              "https://github.com/ExtractTable/camelotpro/blob/master/how%20to%20code.ipynb")
        print("-=- "*15)
    elif gp_response["JobStatus"].lower().startswith("fail"):
        print("[Info]: Table Extraction is Failed. Complete Response Below")
        for k, v in gp_response.items():
            print(f"{k}: {v}")
    elif not any([gp_response["JobStatus"].lower().startswith("succe"), gp_response.get("Tables", [])]):
        print("[Info]: Table Extraction is not completed. Status:", gp_response["JobStatus"])
        print("Check more info using '__dict__' descriptor on the result object.\n")

    for each in gp_response.get("Tables", []):
        if each["Page"] == prev_page:
            order += 1
        else:
            prev_page = each["Page"]
            order = 1
        each["Order"] = order
    tmp_tbl_list = TableList([Table(gp_table) for gp_table in gp_response.get("Tables", [])])
    tmp_tbl_list.Pages = gp_response.pop("Pages", "NA")
    for k, v in gp_response.items():
        if k != "Tables":
            tmp_tbl_list.__setattr__(k, v)
    return tmp_tbl_list
