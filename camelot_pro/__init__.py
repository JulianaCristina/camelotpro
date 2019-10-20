# -*- coding: utf-8 -*-
from .helpers import *
from ExtractTable import ExtractTable


def check_usage(api_key):
    return ExtractTable(api_key).check_usage()


def read_pdf(
        filepath,
        pages: str = "1",
        password: str = '',
        flavor: str = "camelotPro",
        pro_kwargs: dict = None,
        suppress_stdout: bool = False,
        layout_kwargs: dict = None,
        **kwargs
):
    """
    Read PDF and return extracted tables.
    Parameters described below are exclusive for CamelotPro.
    Please refer to the docstrings from Camelot.read_pdf for information on other parameters
    <https://github.com/atlanhq/camelot/blob/master/camelot/io.py#L9>

    Parameters
    ----------
    flavor : str (default: 'lattice') [Case-Insensitive]
        The parsing method to use ('lattice' or 'stream' or 'CamelotPro').

    pro_kwargs: dict, Must Need (if flavor is "CamelotPro")
        A dict of (
            {
                "api_key": str,
                Mandatory, to trigger "CamelotPro" flavor, to process Scan PDFs and images, also text PDF files

                "job_id": str,
                    empty, to process a new file
                    Mandatory, to retrieve the result of the already submitted file

                "dup_check": bool, default: False - to bypass the duplicate check
                    Useful to handle duplicate requests, check based on the FileName

                "max_wait_time": int, default: 300
                    Checks for the output every 15 seconds until successfully processed or for a maximum of 300 seconds.
            }
        )

    Returns
    -------
    tables : camelot.core.TableList
    """
    pro_flavors = tuple(["camelotpro", "camelot_pro", "pro"])

    if pro_kwargs is None:
        pro_kwargs = {}

    flavor = flavor.lower()
    if flavor in pro_flavors or any([kwa.lower() in pro_flavors for kwa in kwargs]):
        if kwargs.pop("password", ""):
            raise IOError("Pro version does not support the password protected files")

        max_wait_time = int(pro_kwargs.pop("max_wait_time", 300))
        dup_check = pro_kwargs.pop("dup_check", False)

        et_sess = ExtractTable(api_key=pro_kwargs["api_key"])
        if not pro_kwargs.get("job_id", ""):
            et_sess.process_file(
                filepath,
                output_format="df",
                dup_check=dup_check,
                max_wait_time=max_wait_time,
                pages=kwargs.pop("pages", "1")
            )
        else:
            et_sess.get_result(pro_kwargs["job_id"], max_wait_time=max_wait_time)

        gp_resp = et_sess.ServerResponse.json()
        from camelot_pro.doppelganger import table_list
        tables = table_list(gp_resp)
    else:
        from camelot.io import read_pdf
        tables = read_pdf(
            filepath=filepath,
            pages=pages,
            password=password,
            flavor=flavor,
            suppress_stdout=suppress_stdout,
            layout_kwargs=layout_kwargs if layout_kwargs else {},
            **kwargs
        )
        if not tables:
            notify(try_pro)
    return tables
