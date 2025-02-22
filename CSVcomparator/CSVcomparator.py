# This Script is used to compare two CSV UTF-8 files with ; separation by checking,
# if the data of a label "x" in row name "x-row" in File 1
# is the same data of in a second File 2 in column "y" with row name "y-row" !

# To do this booth files need to have the column names in the first row and booth files need to have a column in which
# the labels are stored. The labels are used to compare the corresponding values of the columns in the two files.

# Additionally the user have to input a .txt file with the column pairs which should be compared.
# In each row of this .txt file, one pair of column names is stored in the following way:
# "colNameFile1:::colNameFile2"
# The program will then iterate over all labels that are shared in booth Label columns and then compare the values
# of File 1 in "colNameFile1" with the values of File 2 in "colNameFile2" for each label.

# The user can also input a list of values which should be ignored while comparing the values.

# It is also possible to save the console output to a .txt or writing the wrong values found to a csv file
# by providing a path to a directory in which the files should be saved as arguments to -st and -sc.

# The script is used with the following commands:
# python3 CSVsheetComparator.py

# required:
# -f1  "pathToFile1"
# -f2  "pathToFile2"
# -lp  colNameForLabelsFile1:::colNameForLabelFile2

# modes:
# -lc  compares the labels of the two files & reports unique labels of each file
# -cp  "pathToColumnPairs.txt"
# -acp searches all identical column names and adds these columns to the comparison

# optionals:
# -d  delimiter (default is ";") use instead: "," "|" or "\t"
# -ucn prints all unique column names to the console
# -iv  valuesToIgnore
# -st  "pathToDirectoryToSaveTXT"
# -sc  "pathToDirectoryToSaveCSV"

# COPYRIGHT © 2024 Niklas Max G.
# This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
# More details at: https://github.com/AbUndMax/CSVcomparator-Batch-Program/blob/main/LICENSE.md
# For a quick overview, visit https://creativecommons.org/licenses/by-nc/4.0/

import csv
import argparse
import sys
import os
from datetime import datetime
from typing import Tuple, List, Dict, Set


# loads the given csv file into a matrix
def loadCSVcontent(path, delimiter) -> List[List[str]]:
    content = []
    try:
        # open file
        with open(path, "rb") as file:
            for i, row in enumerate(file):
                decoded_row = row.decode("UTF-8")
                if not decoded_row == "":
                    split_row = decoded_row.split(delimiter)
                    content.append(split_row)
        return content
    
    except FileNotFoundError:
        print(f"<<<<<<! the file {path} could not be found !>>>>>>")
        sys.exit(1)
        
    except UnicodeDecodeError:
        split_row = row.split(delimiter.encode("UTF-8"))
        for j, cell in enumerate(split_row):
                        try:
                            cell.decode("UTF-8")
                        except UnicodeDecodeError:
                            cell_content = cell.decode("UTF-8", errors="replace")
                            print(f"<<<<<<! Decode Error in File: {path.split('/')[-1]} !>>>>>>")
                            print(f"Error byte in row {i+1}, column {j+1}")
                            print(f"cell content: {cell_content}")
                            sys.exit(1)
                            
    except Exception as e:
        print(f"<<<<<<! An error occurred: {e} !>>>>>>")
        sys.exit(1)


# splits a columnNamePair (between "":::"")
def splitPair(pair) -> List[str]:
    return pair.split(sep=":::")


# returns lset of all labels of file <fileNumber>
# and a dictionary of {label: index of label in fileContent} (index of label in fileContent starts at 1)
def getLabelSetAndIndexDic(labelColumnNames, fileNumber, content) -> Tuple[Set[str], Dict[str, int], Dict[str, List[int]]]:
    columnNameForLabel = labelColumnNames[fileNumber - 1]
    try:
        labelColIndex = content[0].index(columnNameForLabel)
        # A List of all labels WITHOUT the colName of the LabelCol
        labelList = []
        seen = set()
        labelIndexDic = {}
        duplicates = {}
        for index, row in enumerate(content[1:], start=1): # start = 1 because first row (header) is excluded
            label = row[labelColIndex]
            if label not in seen:
                labelList.append(label)
                labelIndexDic.update({label: index})
                seen.add(label)
            elif label in duplicates:
                duplicates[label].append(index)
            else:
                duplicates[label] = [index]
                

        return set(labelList), labelIndexDic, duplicates

    except ValueError:
        print(f"<<<<<<! {columnNameForLabel} is not contained in file {fileNumber} !>>>>>>")
        sys.exit(1)


# returns a Dictionary with {label: index in header row of content}
def getColNameIndexDic(colPairs, fileContent, fileNumber) -> Dict[str, int]:
    # saves all Names of columns of one File inside a list per file
    inputtedColNamesFile = [name[fileNumber - 1] for name in colPairs]

    try:
        colNameDicFile = {}
        for name in inputtedColNamesFile:
            try:
                colNameDicFile[name] = fileContent[0].index(name)
            except ValueError:
                print(f"<<<<<<! label: '{name}' is not present in file {fileNumber} !>>>>>>")
                sys.exit(1)
        return colNameDicFile
    except Exception as e:
        print(f"<<<<<<! something went wrong {e}")
        sys.exit(1)


# This is the actual comparison of the corresponding values,
# it returns None if all vals are equal
# else it returns a dic with {label: the position of the mismatched values}
def compareValues(colPairs, labelIntersection, file1Content, file2Content, labelDicFile1, labelDicFile2,
                  colNameDicFile1, colNameDicFile2, ignoreValuesList) -> Dict[str, List[List[str]]]:
    wrongValuesCoordinates = {}
    for label in labelIntersection:

        wrongValuesCoordinates.update({label: []})
        noWrongValue = True

        for pair in colPairs:
            file1Value = file1Content[labelDicFile1.get(label)][colNameDicFile1.get(pair[0])]
            file2Value = file2Content[labelDicFile2.get(label)][colNameDicFile2.get(pair[1])]

            file1ValueString = str(file1Value)
            file2ValueString = str(file2Value)

            # if the values are empty or not of type number, we can't compare them as floats.
            try:
                file1Value = float(file1Value)
                file2Value = float(file2Value)
            except ValueError:
                pass

            # if the values are identical or are any value which the user said to ignore, we go to the next value
            if file1Value == file2Value or file1ValueString in ignoreValuesList or file2ValueString in ignoreValuesList:
                wrongValuesCoordinates.get(label).append(None)

            # if the values are not the same, we append the column names and the wrong values to the dic
            else:
                wrongValuesCoordinates.get(label).append([pair[0], file1ValueString, pair[1], file2ValueString])
                noWrongValue = False

        if noWrongValue:
            del wrongValuesCoordinates[label]

    return wrongValuesCoordinates
        
        
# prints all duplicates to the console
def printDuplicatesIfExist(duplicatesFile1, duplicatesFile2):
    head = "\n" + "#" * 17 + " Duplicates " + "#" * 17
    print(head)
    if duplicatesFile1:
        print("#\n### The following labels occured multiple times in file 1:")
        for label, rows in duplicatesFile1.items():
            print("#", label, " in row: ", ", ".join(map(str, rows)))
    if duplicatesFile2:
        print("#\n### The following labels occured multiple times in file 2:")
        for label, rows in duplicatesFile2.items():
            print("#", label, " in row: ", ", ".join(map(str, rows)))
    print("#\n" + "#" * len(head))
    
        
# print all unqiue labels to the console
def printUniqueLabels(unique_labels_file1, indexDicFile1, unique_labels_file2, indesxDicFile2):
    if not unique_labels_file1 and not unique_labels_file2:
        print("\n### All labels are contained in both files ###")
    else:
        head = "\n" + "#" * 17 + " Unique Labels " + "#" * 17
        print(head)
        if unique_labels_file1:
            print("#\n### The following labels are unique to file 1:")
            for label in unique_labels_file1:
                print("#", label, " in row: ", indexDicFile1.get(label))
        else:
            print("#\n### All labels in file 1 contained in file 2")
        if unique_labels_file2:
            print("#\n### The following labels are unique to file 2:")
            for label in unique_labels_file2:
                print("#", label, " in row: ", indesxDicFile2.get(label))
        else:
            print("\n### All labels in file 2 contained in file 1")
        print("#\n" + "#" * len(head))
        
        print("\n<<<<<! Some labels are unique either for File1 or for File2 !>>>>>>")
        print("> see above / scroll up to see details!")
        
        
# print all unqie column names to the console
def printUniqueColNames(uniqueColNamesFile1, uniqueColNamesFile2):
    if uniqueColNamesFile1 or uniqueColNamesFile2:
        head = "\n" + "#" * 17 + " Unique Column Names " + "#" * 17
        print(head)
    if uniqueColNamesFile1:
        print("#\n### The following columns are unique to file 1:")
        for colName in uniqueColNamesFile1:
            print("#", colName)
    if uniqueColNamesFile2:
        print("#\n### The following columns are unique to file 2:")
        for colName in uniqueColNamesFile2:
            print("#", colName)
        print("#\n" + "#" * len(head))
            
            
# prints the given string to the console or to a file
def output(string, file=None):
    if file:
        file.write(string + "\n")
    else:
        print(string)


# prints all found wrong values one after another
def printWrongValues(wrongValues, file=None):
    wrongValuesCounter = 0

    for label in wrongValues.keys():
        header = "\n" + "#" * 17 + f" wrong value(s) found in Label: {label} " + "#" * 17
        output(header, file)
        output("#", file)

        wrongValuesList = [wrongValueCoordinates for wrongValueCoordinates in wrongValues.get(label)
                           if wrongValueCoordinates is not None]

        for wrongValue in wrongValuesList:
            output(f"#   ######################   {label}", file)
            output("#", file)
            output("#   >File 1:", file)
            output(f"#   \tcolumn Name: {wrongValue[0]}", file)
            output(f"#   \t      value: {wrongValue[1]}", file)
            output("#   >File 2:", file)
            output(f"#   \tcolumn Name: {wrongValue[2]}", file)
            output(f"#   \t      value: {wrongValue[3]}", file)
            output("#", file)
            wrongValuesCounter += 1

        output("#" * len(header), file)

    output(f"\n>> there is a total of {wrongValuesCounter} wrong Values\n", file)


# saves the wrong values to a txt file
def saveToTXT(dirPath, wrongValues):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    try:
        if os.path.isdir(dirPath):
            filePath = dirPath + f"/WrongValues_{timestamp}.txt"
            with open(filePath, "w") as file:
                printWrongValues(wrongValues, file)

    except Exception as e:
        print(f"<<<<<<! ERROR: could not write as TXT: {e} !>>>>>>")
        sys.exit(1)

    print("\nsuccessfully saved as TXT to: " + dirPath + f"/WrongValues_{timestamp}.txt")


# saves the wrong values to a csv file
def saveToCSV(dirPath, wrongValues, colPairs):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    try:
        if os.path.isdir(dirPath):
            filePath = dirPath + f"/WrongValues_{timestamp}.csv"
            with open(filePath, "w", newline="") as file:
                writer = csv.writer(file, delimiter=";")

                writer.writerow([colName[0] for colName in colPairs])
                writer.writerow([colName[1] for colName in colPairs])

                sortedLabels = sorted(wrongValues.keys())
                for label in sortedLabels:

                    labelValues = []

                    for value in wrongValues.get(label):
                        if value is None:
                            labelValues.append("")
                        else:
                            labelValues.append(value[1] + " <-> " + value[3])

                    writer.writerow([label] + labelValues)

    except Exception as e:
        print(f"<<<<<<! ERROR: could not write as CSV: {e} !>>>>>>")
        sys.exit(1)

    print("\nsuccessfully saved as CSV to: " + dirPath + f"/WrongValues_{timestamp}.csv")


def main():
    parser = argparse.ArgumentParser(description="CSV comparator script - labels per row and have to be identical!")
    
    # required arguments:
    parser.add_argument("-f1", "--file1", type=str, required=True,
                        help="Path of the file which gets compared to the second one")
    parser.add_argument("-f2", "--file2", type=str, required=True,
                        help="Path of the file which is compared to the first one")
    parser.add_argument("-lp", "--labelColumnNamePair", type=str, required=True,
                        help="name of the columns in which the labels are stored " +
                             "\nthey are inputted in the way: colNameForLabelsFile1:::colNameForLabelFile2")
   
    # modes:
    parser.add_argument("-lc", "--labelComparison", action="store_true",
                        help="compares the labels of the two files & reports unique labels of each file")
    parser.add_argument("-cp", "--columnNamePairs", type=str,
                        help="all pairs of columns which should be compared " +
                             "\nthey are inputted in a .txt such that each pair is in one " +
                             "row: colNameFile1:::colNameFile2 nextPair nextPair ...")
    parser.add_argument("-acp", "--autoColumnPairs", action="store_true", 
                        help="The script will search automatically for identical named columns and include them into the comparison")
   
    # optionals:
    parser.add_argument("-ucn", "--printUniqueColNames", action="store_true", help="Print all unique column names to the console")
    parser.add_argument("-iv", "--ignoreValues", nargs="+", type=str,
                        help="optional Values which can occur in the files and should be ignored " +
                             "while comparing (e.g. Null, NONE, "" or 9999)")
    parser.add_argument("-d", "--delimiter", type=str, default=";",
                        help="delimiter used in the csv files (default is ';') use instead: ',' '|' or '\\t'")
    parser.add_argument("-st", "--saveToTXT", type=str,
                        help="path to directory in which the console printout gets saved into a txt file")
    parser.add_argument("-sc", "--saveToCSV", type=str,
                        help="path to a directory in which wrongValues gets saved as CSV file")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    
    autoPairMode = args.autoColumnPairs
    columnNamePairMode = args.columnNamePairs
    labelComparisonMode = args.labelComparison
    
    if not columnNamePairMode and not autoPairMode and not labelComparisonMode:
        parser.error("\n > Please provide either a column pair file to -cp/--columnNamePairs" + 
                     "\n > use the -acp/--autoColumnPairs flag to compare all columns with the same name" + 
                     "\n > or use the -lc/--labelComparison flag to compare the labels of the two files")
        
    if args.delimiter not in [",", ";", "|", "\t"]:
        parser.error("\n > The delimiter has to be one of the following: ',' ';' '|' or '\\t'")

    file1Content = loadCSVcontent(args.file1, args.delimiter)
    file2Content = loadCSVcontent(args.file2, args.delimiter)

    if args.ignoreValues is None:
        ignoreValues = []
    else:
        ignoreValues = args.ignoreValues

    if args.verbose: print("\n#v# CSV loading successful")

    # saves the names of the columns in which the labels are stored in a
    # list (index 0 = colName of labels in File 1, 
    #       index 1 = colName of labels in File 2)
    labelColumnNames = splitPair(args.labelColumnNamePair)

    # check if labelListFile1 is subset of labelListFile2
    labelSetFile1, labelIndexDicFile1, labelDuplicatesFile1 = getLabelSetAndIndexDic(labelColumnNames, 1, file1Content)
    labelSetFile2, labelIndexDicFile2,  labelDuplicatesFile2 = getLabelSetAndIndexDic(labelColumnNames, 2, file2Content)
    
    if labelDuplicatesFile1 or labelDuplicatesFile2:
        printDuplicatesIfExist(labelDuplicatesFile1, labelDuplicatesFile2)
        print("\n<<<<<<! There are repetitive labels !>>>>>>")
        print("> see above / scroll up to see details!")
        print("> If you proceed with the comparison, the first occurrence of the label will be used!")
        continueEvenWithDuplicates = input("\n> do you want to continue either way? (y/n)\n")
        if continueEvenWithDuplicates != "y":
            sys.exit(0)
    
    unique_labels_file1 = labelSetFile1 - labelSetFile2
    unique_labels_file2 = labelSetFile2 - labelSetFile1
    
    if (labelComparisonMode):
            printUniqueLabels(unique_labels_file1, labelIndexDicFile1, unique_labels_file2, labelIndexDicFile2)
            if not columnNamePairMode and not autoPairMode: # end script if only label comparison mode is used
                sys.exit(0)
        
    if unique_labels_file1 or unique_labels_file2:
        if not labelComparisonMode:
            print("\n<<<<<<! Some labels are unique either for File1 or for File2 !>>>>>>")
            print("> You may want to check the differences with the -lc flag")
        userInput = input("\n> do you want to continue either way? (y/n)\n")
        if userInput != "y":
            sys.exit(0)

    labelIntersection = labelSetFile1 & labelSetFile2
    if args.verbose: print("\n#v# Label Sets & Label Dictionary's loaded! - Label Intersection created")
    
    # save all pairs in a colPairs Matrix [[colNameFile1, colNameFile2] [colNameFile1, colNameFile2], ...]
    colPairs = []
    if columnNamePairMode:
        try:
            with open(columnNamePairMode, "r") as colNamePairFile:
                # only split and append if the line is not empty (last if checks if line is empty)
                colPairs = [splitPair(pair.strip()) for pair in colNamePairFile if pair.strip()]
        except Exception as e:
            print(f"<<<<<<! An error occurred: {e} !>>>>>>")
            sys.exit(1)
    
    # find all unique column names in the files
    if args.printUniqueColNames:
        colNameSetFile1 = set(file1Content[0])
        colNameSetFile2 = set(file2Content[0])
        labelSet = set(labelColumnNames)
        uniqueColNamesFile1 = colNameSetFile1 - colNameSetFile2 - labelSet
        uniqueColNamesFile2 = colNameSetFile2 - colNameSetFile1 - labelSet
      
    # find all columns with the same name that are not already in the ColPairs list and do not occure in the LabelColumnNames
    # first check is to prevent the same column to be compared twice
    # second check is to prevent the label columns to be compared        
    if autoPairMode:
        for colName in file1Content[0]:
            if colName in file2Content[0] and colName not in labelColumnNames and [colName, colName] not in colPairs:
                colPairs.append([colName, colName])
        

    if args.verbose: print("\n#v# column pairs successfully loaded!")

    colNameDicFile1 = getColNameIndexDic(colPairs, file1Content, 1)
    colNameDicFile2 = getColNameIndexDic(colPairs, file2Content, 2)

    if args.verbose: print("\n#v# Column Name Dictionary's successfully loaded!")

    wrongValues = compareValues(colPairs, labelIntersection, file1Content, file2Content, labelIndexDicFile1, labelIndexDicFile2,
                                colNameDicFile1, colNameDicFile2, ignoreValues)

    if args.verbose: print("\n#v# comparison of values successful!")
    
    if args.printUniqueColNames:
        printUniqueColNames(uniqueColNamesFile1, uniqueColNamesFile2)

    if not wrongValues:
        print("\n### all values are identical :D ###")
    else:
        print("\n<<<<<<! there is at least one wrong value !>>>>>>")
        printWrongValues(wrongValues)

    if args.saveToTXT is not None:
        saveToTXT(args.saveToTXT, wrongValues)

    if args.saveToCSV is not None:
        saveToCSV(args.saveToCSV, wrongValues, [labelColumnNames] + colPairs)


if __name__ == "__main__":
    main()
