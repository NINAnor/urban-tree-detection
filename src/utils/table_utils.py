##---------------------------------------------------------------------------------------------------------------------------------------------------------------------
## excel-csv-txt.py
##
## author: Willeke A'Campo (VMG)
## created: 22 july 2022
## last updated: 26 september 2022.
## save script in: 'C:\\Data\\Python_modules' or in same directory as your python project.
##
## task of script:
## contains Excel, CSV and TXT class with attributes and methods that convert .xlsx, .csv, .txt file formats to gis-tables, pandas dataframes etc.
##
##---------------------------------------------------------------------------------------------------------------------------------------------------------------------


import os

import arcpy
import pandas as pd


class Excel:
    def __init__(self, input_dir, file_name):
        """
        initializes an Excel object

        variables:
        -------
        path : str
        - path to excel sheet

        name : str
        - name of excel sheet
        """
        self.input_dir = input_dir
        self.file_name = file_name
        self.file_path = os.path.join(input_dir, file_name)

    def __repr__(self):
        """
        returns the object's information instead of id number of the memory space

        variables:
        -------
        no variables
        """
        return f"Location: {self.input_dir}, Name: {self.file_name}"

    def importSheets(self):
        """
        imports the Excel sheets into a list

        -------
        variables:
        -------
        no variables
        """
        if self.file_path.endswith(".xlsx"):
            workbook = pd.ExcelFile(self.file_path)
            self.ListSheet = workbook.sheet_names
            print(
                "File {} contains {} sheets: {}".format(
                    self.file_name,
                    len(self.ListSheet),
                    " , ".join(self.ListSheet),
                )
            )
        else:
            print("An Excel Workbook of format .xlsx is required.")
        return self.ListSheet

    def toDic(self):
        """
        imports the Excel sheets as dataframes and stores them in a dictionairy

        variables:
        -------
        no variables
        """

        dic = {}
        for key in self.ListSheet:
            # open excel sheet as dataframe
            df = pd.read_excel(self.file_path, sheet_name=key)
            # store dataframe into dictionary with corresponding name.
            dic[key] = df
        return dic

    def toPoint(self, output_dir, start, end):
        """
        creates a file geodatabase using the excel file name and
        converts the excel sheets first to geodatabase tables and
        then to point feature classes

        variables:
        -------
        output_dir : str
        - path to output directory where the file gdb will be created

        start : int
        - number of the first excel sheet with XY coordinates

        end: int
        - number of the last excel sheet with XY coordinates
        """
        # self.output_dir = output_dir
        arcpy.env.overwriteOutput = True  # overwrite files
        arcpy.env.workspace = output_dir
        print("ArcPy Workspace for creating the GDB:", arcpy.env.workspace)

        # Create a file GDB
        # The GDB is based on the Excel file name
        gdb_name = os.path.join(os.path.splitext(self.file_name)[0] + ".gdb")
        gdb_path = os.path.join(output_dir, gdb_name)
        arcpy.CreateFileGDB_management(output_dir, gdb_name)
        arcpy.env.workspace = gdb_path

        print(
            "ArcPy Workspace for importing the excel sheets:",
            arcpy.env.workspace,
        )

        for sheet in self.ListSheet[start:end]:
            # Perform conversion from Excel to GDB table
            out_table = os.path.join(gdb_path, sheet)  # table name
            print(
                'Converting "{}" excel sheet to "{}" gdb table.'.format(
                    sheet, out_table
                )
            )
            arcpy.conversion.ExcelToTable(self.file_path, out_table, sheet)

            # Perform conversion from GDB table to XY point feature class
            out_feature = os.path.join(out_table + "_POINT")  # feature name
            print(
                'Converting "{}" gdb table to "{}" point feature class.'.format(
                    sheet, out_feature
                )
            )
            arcpy.management.XYTableToPoint(
                out_table, out_feature, "longitude", "latitude", "altitude"
            )


class Csv_file(Excel):
    ## TO DO:
    ## add methods

    def __init__(self, input_dir, file_name, delimiter):
        super().__init__(input_dir, file_name)
        self.delimiter = delimiter


class Txt_file(Excel):
    ## TO DO:
    ## add methods

    def __init__(self, input_dir, file_name):
        super().__init__(input_dir, file_name)
