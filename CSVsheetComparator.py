# This Script is used to compare two CSV UTF-8 files with ; seperation by checking,
# if the data of a label "x" in row name "x-row" in File 1
# is the same data of in a second File 2 in column "y" with row name "y-row" !

# To do this booth files need to have the column names in the first row and booth files need to have a column in which
# the labels are stored. The labels are used to compare the corresponding values of the columns in the two files.

# Additionally the user have to input a .txt file with the column pairs which should be compared.
# In each row of this .txt file, one pair of column names is stored in the following way:
# "colNameFile1:::colNameFile2"
# The program will then iterate over all labels that are shared in booth Label columns and then compare the values
# of File 1 in "colNameFile1" with the values of File 2 in "colNameFile2" for each label.

# The script is used with the following command:
# python3 CSVsheetComparator.py
# -f1 "pathToFile1"
# -f2 "pathToFile2"
# -lp "colNameForLabelsFile1:::colNameForLabelFile2"
# -cp "pathToColumnPairs.txt"
# -iv "optionalValuesToIgnore"

import csv
import argparse
import sys
from typing import Tuple, List, Dict, Set


# loads the given csv file into a matrix
def loadCSVcontent(path) -> List[List[str]]:
    content = []
    try:
        # open first file
        with open(path, newline="", encoding="UTF-8-sig") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=";")
            for row in csvreader:
                if any(field.strip() for field in row): # checks rather row is empty or not
                    content.append(row)
        return content
    except FileNotFoundError:
        print(f"<<<<<<! the file {path} could not be found !>>>>>>")
        sys.exit(1)
    except Exception as e:
        print(f"<<<<<<! An error occurred: {e} !>>>>>>")
        sys.exit(1)


# splits a columnNamePair (between "":::"")
def splitPair(pair) -> List[str]:
    return pair.split(sep=":::")


# returns labelList and dic of {label: index of label in fileContent}
def getLabelSetAndDic(labelColumnNames, fileNumber, content) -> Tuple[Set[str], Dict[str, int]]:
    columnNameForLabel = labelColumnNames[fileNumber - 1]
    try:
        labelColIndex = content[0].index(columnNameForLabel)
        # A List of all labels WITHOUT the colName of the LabelCol
        labelList = [row[labelColIndex] for row in content[1:]]
        labelDic = {}
        for index, label in enumerate(labelList):
            labelDic.update({label: index + 1}) # +1 because the colName is index 0 which is missing in the label list

        return set(labelList), labelDic

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


# This is the actual comparison of the corresponding values, it returns None if all vals are equal else it returns
# the position of the mismatched value
def compareValues(colPairs, labelIntersection, file1Content, file2Content, labelDicFile1, labelDicFile2,
                  colNameDicFile1, colNameDicFile2, ignoreValuesList) -> Dict[str, List[List[str]]]:
    wrongValuesCoordinates = {}
    for label in labelIntersection:
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
                continue

            # if the values are not the same, they have to be different which means we just check if label already has
            # wrong Values, and if so append it to the dic in the corresponding label
            elif label in wrongValuesCoordinates:
                wrongValuesCoordinates.get(label).append([pair[0], file1ValueString, pair[1], file2ValueString])

            # else we make a new key with the current label
            else:
                wrongValuesCoordinates.update({label: [[pair[0], file1ValueString, pair[1], file2ValueString]]})

    return wrongValuesCoordinates


# prints all found wrong values one after another
def printWrongValues(wrongValues):
    wrongValuesCounter = 0

    for label in wrongValues.keys():
        print("\n" + "#" * 17 + f" wrong value(s) found in Label: " + "#" * 17)
        print("#")

        wrongValuesList = wrongValues.get(label)

        for wrongValue in wrongValuesList:
            print(f"#   ######################   {label}")
            print("#")
            print("#   >File 1:")
            print(f"#   \tcolumn Name: {wrongValue[0]}")
            print(f"#   \t      value: {wrongValue[1]}")
            print("#   >File 2:")
            print(f"#   \tcolumn Name: {wrongValue[2]}")
            print(f"#   \t      value: {wrongValue[3]}")
            print("#")
            wrongValuesCounter += 1

        print("##################################################################")

    print(f"\n>> there is a total of {wrongValuesCounter} wrong Values\n")


def main():
    parser = argparse.ArgumentParser(description="CSV comparator script - labels per row and have to be identical!")
    parser.add_argument("-f1", "--file1", type=str, required=True,
                        help="Path of the file which gets compared to the second one")
    parser.add_argument("-f2", "--file2", type=str, required=True,
                        help="Path of the file which is compared to the first one")
    parser.add_argument("-lp", "--labelColumnNamePair", type=str, required=True,
                        help="name of the columns in which the labels are stored " +
                             "\nthey are inputted in the way: colNameForLabelsFile1:::colNameForLabelFile2")
    parser.add_argument("-cp", "--columnNamePairs", type=str, required=True,
                        help="all pairs of columns which should be compared " +
                             "\nthey are inputted in a .txt such that each pair is in one " +
                             "row: colNameFile1:::colNameFile2 nextPair nextPair ...")
    parser.add_argument("-iv", "--ignoreValues", nargs="+", type=str,
                        help="optional Values which can occur in the files and should be ignored " +
                             "while comparing (e.g. Null, NONE, "" or 9999)")
    parser.add_argument("-dbg", "--printDebugLines", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    file1Content = loadCSVcontent(args.file1)
    file2Content = loadCSVcontent(args.file2)

    if args.ignoreValues is None:
        ignoreValues = []
    else:
        ignoreValues = args.ignoreValues

    if args.verbose:
        print("\n#v# CSV loading successful")

    if args.printDebugLines:
        print("\n################################################ FILE 1 CONTENT ####################################################")
        print(file1Content)
        print("####################################################################################################################")

        print("\n################################################ FILE 2 CONTENT ####################################################")
        print(file2Content)
        print("####################################################################################################################\n")

    # saves the names of the columns in which the labels are stored in a
    # list (index 0 = colName File 1, index 1 0 colName File 2)
    labelColumnNames = splitPair(args.labelColumnNamePair)

    ## check if labelListFile1 is subset of labelListFile2
    labelSetFile1, labelDicFile1 = getLabelSetAndDic(labelColumnNames, 1, file1Content)
    labelSetFile2, labelDicFile2 = getLabelSetAndDic(labelColumnNames, 2, file2Content)
    labelIntersection = labelSetFile1 & labelSetFile2

    if args.verbose:
        print("\n#v# Label Sets & Label Dictionary's loaded! - Label Intersection created")

    if labelSetFile1 != labelIntersection:
        print("<<<<<<! some of the labels in File1 may not exist in File2 !>>>>>>")
        userInput = input("do you want to continue either way? (y/n)\n")
        if userInput != "y":
            sys.exit(1)

    # save all pairs in a colPairs Matrix [[colNameFile1, colNameFile2] [colNameFile1, colNameFile2], ...]
    try:
        with open(args.columnNamePairs, "r") as colNamePairFile:
            # only split and append if the line is not empty (last if checks if line is empty
            colPairs = [splitPair(pair.strip()) for pair in colNamePairFile if pair.strip()]
    except Exception as e:
        print(f"<<<<<<! An error occurred: {e} !>>>>>>")
        sys.exit(1)

    colNameDicFile1 = getColNameIndexDic(colPairs, file1Content, 1)
    colNameDicFile2 = getColNameIndexDic(colPairs, file2Content, 2)

    if args.verbose:
        print("\n#v# Column Name Dictionary's successfully loaded!")

    wrongValues = compareValues(colPairs, labelIntersection, file1Content, file2Content, labelDicFile1,
                                labelDicFile2, colNameDicFile1, colNameDicFile2, ignoreValues)

    if not wrongValues:
        print("\n### all values are identical :D ###")
    else:
        print("\n<<<<<<! there is at least one wrong value !>>>>>>")
        printWrongValues(wrongValues)


if __name__ == "__main__":
    main()