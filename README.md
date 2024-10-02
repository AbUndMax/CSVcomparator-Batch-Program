[![GitHub](https://img.shields.io/badge/GitHub-CSVcomparator-blue?logo=github)](https://github.com/AbUndMax/CSVcomparator-Batch-Program)
[![License](https://img.shields.io/badge/License-CC_BY--NC_4.0-blue)](https://github.com/AbUndMax/CSVcomparator-Batch-Program/blob/main/LICENSE.md)
[![Java](https://img.shields.io/badge/Python-3.6+-blue?logo=python)](https://openjdk.org/projects/jdk/11/)
[![Badge](https://img.shields.io/github/v/release/AbUndMax/CSVcomparator-Batch-Program?color=brightgreen)](https://github.com/AbUndMax/CSVcomparator-Batch-Program/releases/latest)


# CSV comparing batch program
This script was written in the purpose of comparing two CSV files for identity.
It first searches all matching row names (refferred to as labels) and then compares the values of the specified columns for all matching labels.
It will output all values and positions which are different in booth provided files.

## Features
- **variable delimiter**: The script can handle different delimiters (",", "|", "\t", deafualt: ";").
- **Column Mapping**: Users can specify which columns should be compared.
- **Automatic Column Mapping**: If the column names are identical in both files, the script can automatically map them and compare their values.
- **Handling of Empty Lines**: Empty lines are automatically handled by the script.
- **Partial Matches**: If not all labels from File 1 are present in File 2, the script compares only the intersecting labels and notifies if any labels from File 1 are missing in File 2.
- **Ignoring Values**: Users can specify values to ignore during comparison.
- **List Unique Columns**: The script can list all columns that are unique for each file.
- **Output Formats**: The script prints the differences to the console and can save them as a .txt or .csv file.

## Installation
The script is a cli Tool:
- **UNIX executable**: The script provided in the latest release as an runnable for UNIX (macOS & Linux) system.  
Make the file executable  
`chmod +x CSVcomparator.sh`  
and run it with  
`./CSVcomparator.sh`.
- **Python script**: The script can be run on any system with Python 3.6 or higher installed. Download the CSVcomparator.py file and run it with `python CSVcomparator.py` in the folder where the file is located.

## Prerequisites
- **Label Columns**: Both files must include a specific column that holds "labels" for each row (e.g., sample name). For the values of a label to be compared, the labels must be identical in both files.
- **Column Name Pairs**: Users should know which column in File 1 corresponds to which in File 2 and provide this information in a separate .txt file (see below) as input to specify which columns should be compared.

## How it works
There are 4 required parameters at startup and 4 optionals:  

### Required Parameters
- `-f1`, `--file1`: Path to the first file.
- `-f2`, `--file2`: Path to the second file.
- `-lp`, `--labelColumnNamePairs`: Column names containing labels, formatted as `label1:::label2` (e.g., `labels:::sampleID`). Notice that label of file 1 is leading!

### Modes

- `-cp`, `--columnNamePairs`: A .txt file with names of column pairs that correspond to each other, with each pair in one row: 
    ```
    columnNameFile1:::columnNameFile2
    columnNameFile1:::columnNameFile2
    columnNameFile1:::columnNameFile2
    ...
    ```
    Notice that column of file 1 is leading!
- `-acp`, `--autoColumnPairs`: If this parameter is set, the script will automatically map columns with identical names in both files.
- `-lc`, `--labelComparison`: With this parameter, the script will additionally compare the labels of both files and print out the labels that are unique to each file. 

**Notice**: 
- all three paraemters `-cp`, `-acp` and `-lc` are optional, but at least one of them must be set.
- If `-cp` and `-acp` are set, the script will use the `-cp` (specified pairs) parameter and expand its search by all found matching column names.
- `-lc`can be combined with all other modes.
  
### Optional Parameters
- `-ucn`, `--printUniqueColNames`: If this parameter is set, the script will print all column names that are unique to each file.
- `-iv`, `--ignoreValues`: Values to ignore during comparison (e.g., NONE, 9999, "").
- `-v`, `--verbose`: Provides confirmation after significant operations.
- `-d`, `--delimiter`: Delimiter used in the CSV files (e.g., ",", "|", "\t"), default: ";".
- `-st`, `--saveToTXT`: path to **directory** in which .txt output should be saved.
- `-sc`. `--saveToCSV`: path to **directory** in which .csv output should be saved.
  
#### Output formats
- **Console**: The output will be printed to the console no matter which parameter is set.
- **TXT**: If the `-st` parameter is set, the output will be saved as a .txt file in the provided directory formatted in the same way as the console output.
- **CSV**: If the `-sc` parameter is set, the output will be saved as a .csv file in the provided directory which can be opened in a spreadsheet program like excel or numbers.

## Example
```bash 
-f1 pathToFileAuszugDatenFalse.csv -f2 pathToFileALLEDaten.csv -lp pathToFileColumnPairs -iv Null
```

which will result in a printout like this:
```
<<<<<<! there is at least one wrong value !>>>>>>

################# wrong value(s) found in Label: #################
#
#   ######################   #1224
#
#   >File 1:
#       column Name: u
#             value: 43,4
#   >File 2:
#       column Name: uno
#             value: 43
#
##################################################################

################# wrong value(s) found in Label: #################
#
#   ######################   #1113
#
#   >File 1:
#       column Name: u
#             value: 1243
#   >File 2:
#       column Name: uno
#             value: 12,43
#
#   ######################   #1113
#
#   >File 1:
#       column Name: q
#             value: 15,557
#   >File 2:
#       column Name: quadro
#             value: 15,55
#
##################################################################

>> there is a total of 3 wrong Values
```
