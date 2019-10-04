# CamelotPro: Pro-version of [Camelot](https://github.com/atlanhq/camelot)  
**Latest verions: 0.7.4**
  
[![image](https://img.shields.io/github/license/extracttable/camelotpro)]() [![image](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue)]()  
  
**CamelotPro** is a layer on [camelot-py](https://github.com/atlanhq/camelot) library to extract tables from **Scan PDFs and Images**. 


## CamelotPro vs Camelot
  
**CamelotPro** is no different from the original Camelot to code. It comes with extra **`flavor="CamelotPro"`** in read_pdf(), along with regular "*lattice*" and "*stream*".


## Installation  

As the library itself is dependent on Camelot which has software dependencies, the developer is expected to install them *(listed below)*, to use the regular Camelot flavors *("stream", "lattice")* along with "CamelotPro".  

Please follow the **OS-specific instructions** 

-  [Tkinter](https://camelot-py.readthedocs.io/en/master/user/install-deps.html#os-specific-instructions)
- [GhostScript](https://camelot-py.readthedocs.io/en/master/user/install-deps.html#for-ghostscript) 


>***ProTip**: Ignore the dependencies above, if you choose to extract tables from Images, Scan PDFs, text PDFs with CamelotPro* 


### Using pip  
After  for Camelot, you can simply use pip to install CamelotPro:  
  
    $ pip install -U CamelotPro  

or  
  
### From the source code  
  
    $ git clone https://www.github.com/extracttable/camelotpro.git


## Prerequisites

The developer needs an **api_key** ([free credits here](https://extracttable.com/camelotpro.html)) to use CamelotPro. Each Image file or one PDF page consumes one credit to trigger the process.

**api_key** should be passed through `pro_kwargs`, a `dict` type argument that accepts *api_key*, *job_id*, *dup_check*, *wait_for_output* as keys, can be used as below

    {
        "api_key": str,
            Mandatory, to trigger "CamelotPro" flavor, to process Scan PDFs and images, also text PDF files
        "job_id": str,
            optional, if processing a new file
            Mandatory, to retrieve the result of the already submitted file
        "dup_check": bool, default: False
            Useful to handle duplicate requests, check based on the FileName
        "wait_for_output": bool, default: True
            Loops and check for the output for a maximum of 300 seconds, before the process exits as an output.
            with 20 second gap in between retries
                - If the process will return the output before 300 seconds, when the processing is successful
                - Alternatively, a big file process can always be tracked using the ".JobId" from the output
    }



## Let's code


**Here's how you can extract tables from Image files.** 


The example image (*foo_image.**jpg***)  used in the code below, can be found [here](https://github.com/extracttable/camelotpro/blob/master/samples/foo-image.jpg).  Notice that *foo_image.jpg* is the image version of Camelot's example, [foo.pdf](https://github.com/camelot-dev/camelot/blob/master/docs/_static/pdf/foo.pdf).
  
    from camelot_pro import read_pdf
    api_key = "YOUR_API_KEY_HERE"
    pro_tables = read_pdf('foo-image.jpg', flavor="CamelotPro", pro_kwargs={'api_key': api_key, 'dup_check': False})  


Now that you have triggered the process to find tables from the image, you can find the status of it from the  `JobStatus` attribute, which returns any of *Success, Failed, Processing, Incomplete*.

    pro_tables.JobStatus
    [Out]: "Success"


If the `JobStatus` status is "Success", just like Camelot, the output gives the gist of the process.

    pro_tables
    [Out]: <TableList n=1>                                # Will be <TableList n=0> for any other JobStatus

   
>***ProTip**: Very useful to check out all attributes of the output, when the `JobStatus` is **not "Success"**.

    pro_tables.__dict__

    [Out]: 
    {
        '_tables': [<Table shape=(7, 7)>],        # List of tables found with their shapes
        'Pages': 1,                                # Number of Input pages, equivalent to credits used
        'JobStatus': 'Success'                    # Success | Failed | Processing | Incomplete
    }


Most of the image file processes result in an instant 'Success' job status, at times, a blurry/big/bad file may take ~15 seconds and PDF file process time depends on the page count. In these cases, the `JobStatus` is **"Processing"** and the `JobId` attribute of the output is used to retrieve tables as shown below.


    pro_tables.JobStatus
    [Out]: "Processing"
    
    job_id = pro_tables.JobId
    print(job_id)
    [Out]: "d93e9af0f632084394099dabeb150ead7ee2ed5250377cb4772a358abcc21cf2"

    retrieve_output = read_pdf('', flavor="CamelotPro", pro_kwargs={'api_key': api_key, 'job_id': job_id})
    print(retrieve_output.JobStatus)
    [Out]: "Success"



> ***ProTip**: To receive **immediate Success on image files**, use `'dup_check': False` in `pro_kwargs`*

    instant_pro_tables = read_pdf('foo-image.jpg', flavor="CamelotPro", pro_kwargs={'api_key': api_key, 'dup_check': False})


... and then there are the regular Camelot functions and attributes


    pro_tables.export('foo.csv', f='csv', )         # json, excel, html, sqlite  
    
    pro_tables[0]
    [Out]: <Table shape=(7, 7)>
    
    pro_tables[0].parsing_report  
    [Out]: {  
        'accuracy': 75.12,  
        'whitespace': 0.86,  
        'order': 1,  
        'page': 1  
    }
    
    pro_tables[0].to_csv('foo.csv')             # to_json, to_excel, to_html, to_sqlite  
    
    pro_tables[0].df                  # get a pandas DataFrame!  


  
| Col_1 | Col_2 | Col_3 | Col_4 | Col_5 | Col_6 | Col_7 |
|------------|-----------|---------------|----------------------|-----------------|-----------------|----------------|
| Cycle Name | KI (1/km) | Distance (mi) | Percent Fuel Savings |                 |                 |                |
|            |           |               | Improved Speed       | Decreased Accel | Eliminate Stops | Decreased Idle |
| 2012_2     | 3.30      | 1.3           | 5.9%                 | 9.5%            | 29.2%           | 17.4%          |
| 2145_1     | 0.68      | 11.2          | 2.4%                 | 0.1%            | 9.5%            | 2.7%           |
| 4234_1     | 0.59      | 58.7          | 8.5%                 | 1.3%            | 8.5%            | 3.3%           |
| 2032_2     | 0.17      | 57.8          | 21.7%                | 0.3%            | 2.7%            | 1.2%           |
| 4171_1     | 0.07      | 173.9         | 58.1%                | 1.6%            | 2.1%            | 0.5%           |


## New and Re-defined Attributes of CamelotPro


|Attribute|Explanation|
|----|----|
|`pro_tables.Pages` |Total number of input pages processed. Equivalent to credits used
|`pro_tables.JobStatus` | "**Success**" - Check output for tables or Use "JobId" to retrieve tables<br> "**Failed**" - Process Failed, No Credits used<br> "**Processing**" - Still in process, use "JobId" to retrieve the output later<br> "**Incomplete**" - Process finished, but all pages are not processed. Partial output|
|`pro_tables.Message`|Gives the reason for failure or issue,
|`pro_tables.ProTip`|Hints on how to avoid the errors, if it can be rectified with developer input|
|`pro_tables[0].accuracy`|Accuracy of text assignment to the cell|
|`pro_tables[0].accuracy_character`|Accuracy of Characters recognized from the image|
|`pro_tables[0].accuracy_layout` |Accuracy of table layout's design decision|
|`pro_tables[0].whitespace`|Percentage of Error in Character recognition

  
  
## Pull Requests & Rewards

Pull requests are most welcome and greatly appreciated. 


## License  
  
This project is licensed under the GNU-3.0 License, see the [LICENSE](https://github.com/extracttable/camelotpro/blob/master/LICENSE) file for details.


## Credits

Last but not least, we want to be thankful to the contributors of [camelot-py](https://github.com/atlanhq/camelot/)
