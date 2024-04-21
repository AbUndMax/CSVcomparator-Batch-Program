# CSV comparing batch program
This script was written in the purpose of comparing two CSV files for identity.
It will output all values and positions which are diffrent in booth provided files.

### Assumptions
- **Label Columns**: Both files must include a specific column that holds "labels" for each row (e.g., sample name). The labels in both files must match exactly.
- **Column Mapping**: Users should know which column in File 1 corresponds to which in File 2.
- **Handling of Empty Lines**: Empty lines are automatically handled by the script.
- **Partial Matches**: If not all labels from File 1 are present in File 2, the script compares only the intersecting labels and notifies if any labels from File 1 are missing in File 2.

## How it works
There are 4 required parameters at startup and 3 optionals:  

#### Required Parameters
- `-f1`, `--file1`: Path to the first file.
- `-f2`, `--file2`: Path to the second file.
- `-lp`, `--labelColumnNamePairs`: Column names containing labels, formatted as `label1:::label2` (e.g., `labels:::sampleID`). Notice that label of file 1 is leading!
- `-cp`, `--columnNamePairs`: Column names to compare, formatted similarly to label pairs.

#### Optional Parameters
- `-iv`, `--ignoreValues`: Values to ignore during comparison (e.g., NONE, 9999, "").
- `-dbg`, `--printDebugLines`: Prints the content of files after loading.
- `-v`, `--verbose`: Provides confirmation after significant operations.

## Example
```bash 
-f1 pathToFileAuszugDatenFalse.csv -f2 pathToFileALLEDaten.csv -lp l:::label -cp u:::uno d:::dos t:::tres q:::quadro -iv Null
```

which will result in a printout like this:
```bash
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