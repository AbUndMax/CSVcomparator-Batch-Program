# CSV comparing batch program
This script was written in the purpose of comparing two CSV files for identity.
It will output all values and positions which are different in booth provided files.

### Assumptions
- **Label Columns**: Both files must include a specific column that holds "labels" for each row (e.g., sample name). The labels in both files must match exactly.
- **Column Mapping**: Users should know which column in File 1 corresponds to which in File 2 and provide this information in a separate .txt file. (see below)
- **Handling of Empty Lines**: Empty lines are automatically handled by the script.
- **Partial Matches**: If not all labels from File 1 are present in File 2, the script compares only the intersecting labels and notifies if any labels from File 1 are missing in File 2.

## How it works
There are 4 required parameters at startup and 4 optionals:  

#### Required Parameters
- `-f1`, `--file1`: Path to the first file.
- `-f2`, `--file2`: Path to the second file.
- `-lp`, `--labelColumnNamePairs`: Column names containing labels, formatted as `label1:::label2` (e.g., `labels:::sampleID`). Notice that label of file 1 is leading!
- `-cp`, `--columnNamePairs`: A .txt file with names of column pairs that correspond to each other, formatted as `columnNameFile1:::columnNameFile2`. Notice that column of file 1 is leading!
  
#### Optional Parameters
- `-iv`, `--ignoreValues`: Values to ignore during comparison (e.g., NONE, 9999, "").
- `-v`, `--verbose`: Provides confirmation after significant operations.
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