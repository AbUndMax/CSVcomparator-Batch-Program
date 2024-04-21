# This Script is used to compare two CSV files by checking if the data of a label x in File 1 is the same data of label x in File 2!
# This is done in the following pattern:
### by starting the skript, the path of two CSV files is provided with the first one beeing the one which gets compared two the second one!
### the programm will then ask in which column the label is put in the first file
### then it will aks hwo the column of the labels is called in the second file
### then the program wants pairs of names. These pairs are the mathcing column names
###### eg.: in File 1 a column may be named "uno" but in the second file the column with the same data is called "u"
######      the pair is written like this: "uno:u" or: "firstFileColName:SecondFileColName"


import csv
import argparse
import sys
from typing import Tuple, List, Dict

# loads the given csv file into a matrix
def loadCSVcontent(path) -> List[str]:
    content = []
    try:
        # open first file
        with open(path, newline="", encoding="UTF-8") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=";")
            for row in csvreader:
                if any(field.strip() for field in row): # checks rather row is empty or not
                    content.append(row)
        return content
    except FileNotFoundError:
        print(f"<<<<<<! the file {path} could not be found !>>>>>>")
        sys.exit(1)
    except Exception as e:
        print(f"<<<<<<! An error occured: {e} !>>>>>>")
            
# splits a columnNamePair (between "":::"")
def splitPair(pair) -> List[str]:
    return pair.split(sep=":::")

# returns labelList and dic of {label: index of label in fileContent}
def getColNameForLabelsFromUser(labelColumnNames, fileNumber, content) -> Tuple[List[str], Dict[str, int]]:
    columnNameForLabel = labelColumnNames[fileNumber - 1]
    try:
        labelColIndex = content[0].index(columnNameForLabel)
        # A List of all labels WITHOUT the colName of the LabelCol
        labelList = [row[labelColIndex] for row in content[1:]]
        labelDic = {}
        for index, label in enumerate(labelList):
            labelDic.update({label: index + 1}) # +1 because the colname is index 0 whch is missing in the label list
        
        return set(labelList), labelDic
    except ValueError:
        print(f"<<<<<<! {columnNameForLabel} is not contained in file {fileNumber} !>>>>>>")
        
# returns a Tuple with a List of all columnNamePairs, and two Dictionarys with {label: index in file1 or file2 content}
def getColNamePairsFromUser(columnNamePairs, file1Content, file2Content) -> tuple[List[List[str]], Dict[str, int], Dict[str, int]]:
    # save all pairs in a colPairs Matrix [[colNameFile1, colNameFile2] [colNameFile1, colNameFile2], ...]
    colPairs = []
    for pair in columnNamePairs:
        colPairs.append(splitPair(pair))
    
    # saves all Names of columns of one File inside a list per file
    inputtedColNamesFile1 = [name[0] for name in colPairs]
    inputtedColNamesFile2 = [name[1] for name in colPairs]
    
    try:
        colNameDicFile1 = {name: file1Content[0].index(name) for name in inputtedColNamesFile1}
        colNameDicFile2 = {name: file2Content[0].index(name) for name in inputtedColNamesFile2}
        return colPairs, colNameDicFile1, colNameDicFile2
    except ValueError:
        print("some inputted pairs aren't valid!")
    except Exception as e:
        print(f"soemthing went wrong {e}")
    
# This is the actual comparison of the corresponding values, it returns None if all vals are equal else it returns the position of the mismatched value
def compareValues(colPairs, labelIntersection, file1Content, file2Content, labelDicFile1, labelDicFile2, colNameDicFile1, colNameDicFile2, ignoreValuesList) -> Dict[str, List[List[str]]]:
    wrongValuesCoordinates = {}
    for label in labelIntersection:
        for pair in colPairs:
            file1Value = file1Content[labelDicFile1.get(label)][colNameDicFile1.get(pair[0])]
            file2Value = file2Content[labelDicFile2.get(label)][colNameDicFile2.get(pair[1])]
            
            # if the values are identical or are any value which the user said to ignore, we go to the next value
            if file1Value == file2Value or str(file1Value) in ignoreValuesList or str(file2Value) in ignoreValuesList:
                continue
            
            # if the values are not the same, they have to be diffrent which means we just check if label already has wrong Values, and if so append it to the dic in the corresponding label
            elif label in wrongValuesCoordinates: 
                wrongValuesCoordinates.get(label).append([pair[0], pair[1]])
                
            #else we make a new key with the current label
            else:
                wrongValuesCoordinates.update({label: [[pair[0], pair[1]]]})
                
    return wrongValuesCoordinates

def main():
    parser = argparse.ArgumentParser(description="CSV comparator script - labels per row and have to be identical!")
    parser.add_argument("-f1", "--file1", type=str, required=True, help="Path of the file which gets compared to the second one")
    parser.add_argument("-f2", "--file2", type=str, required=True, help="Path of the file which is compared to the first one")
    parser.add_argument("-lp", "--labelColumnNamePair", type=str, required=True, help="name of the columns in which the labels are stored \nthey are inputted in the way: colNameForLabelsFile1:::colNameForLabelFile2")
    parser.add_argument("-cp", "--columnNamePairs", nargs="+", type=str, required=True, help="all pairs of columns which should be compared \nthey are inputted in the way: colNameFile1:::colNameFile2 nextPair nextPair ...")
    parser.add_argument("-iv", "--ignoreValues", nargs="+", type=str, help="optional Values which can occure in the files and should be ignored while comparing (e.g. Null, NONE, "" or 9999)")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
            
    file1Content = loadCSVcontent(args.file1)
    file2Content = loadCSVcontent(args.file2)

    
    print("\n################################################ FILE 1 CONTENT ####################################################")
    print(file1Content)
    print("####################################################################################################################")

    print("\n################################################ FILE 2 CONTENT ####################################################")
    print(file2Content)
    print("####################################################################################################################\n")        

    labelColumnNames = splitPair(args.labelColumnNamePair) # saves the names of the columns in which the labels are stored in a list (index 0 = colName File 1, index 1 0 colName File 2)

    ## check if labelListFile1 is subset of labelListFile2
    is_LabelListFile1_SubSet = False
    while not is_LabelListFile1_SubSet:
        labelSetFile1, labelDicFile1 = getColNameForLabelsFromUser(labelColumnNames, 1, file1Content)
        labelSetFile2, labelDicFile2 = getColNameForLabelsFromUser(labelColumnNames, 2, file2Content)
        labelIntersection = labelSetFile1 & labelSetFile2
        
        if labelSetFile1 != labelIntersection:
            print("<<<<<<! some of the labels in File1 may not exist in File2! (or typo) !>>>>>>")
            userInput = input("do you want to continue either way? (y/n)")
            if userInput == "y":
                is_LabelListFile1_SubSet = True
            else:
                continue
        else:
            is_LabelListFile1_SubSet = True
            
    # build a intersection of 

    # DEBUG
    def printDic(dic):
        for key, value in dic.items():
            print(key + ": " + str(value))
        print("### END\n")

    printDic(labelDicFile1)
    printDic(labelDicFile2)

    colPairs, colNameDicFile1, colNameDicFile2 = getColNamePairsFromUser(args.columnNamePairs, file1Content, file2Content)
    
    wrongValues = compareValues(colPairs, labelIntersection, file1Content, file2Content, labelDicFile1, labelDicFile2, colNameDicFile1, colNameDicFile2, args.ignoreValues)
                
    if not wrongValues:
        print("\n### all values are identical :D ###")
    else:
        print("\n<<<<<<! there is at least one wrong value !>>>>>>")
        wrongValuesCounter = 0
        for label in wrongValues.keys():
            restString = 20 - len(label)
            print("\n" + "#" * (restString//2) + f" wrong value was found while comparing label {label} " + "#" * (restString//2))
            wrongValuesList = wrongValues.get(label)
            numberOfWrongValuesInLabel = len(wrongValuesList)
            for wrongValue in wrongValuesList:
                # TODO we remove empty lines in the csv hence we canÄt give the exact coordinat as number (i.e. row num: / col num:)
                # insted we have to give label number which equals row name and colName.
                # TODO additionally we can give the exact value which is in file 1 and in file 2 so we can be sure we have the correct cell if we manually compare them in the original sheets
                print("#")
                print("#   >File 1:")
                print(f"#   \trow number:  {labelDicFile1.get(label) + 1}")
                print(f"#   \tcolumn Name: {wrongValue[0]}")
                print("#   >File 2:")
                print(f"#   \trow number:  {labelDicFile2.get(label) + 1}")
                print(f"#   \tcolumn Name: {wrongValue[1]}")
                wrongValuesCounter += 1
                numberOfWrongValuesInLabel -= 1
                
                if numberOfWrongValuesInLabel != 0:
                    print("#")
                    print("#   ######################")
                
            print("#")
            print("#################################################################")
            
        print(f"\n>>there are a total of {wrongValuesCounter} wrong Values\n")

if __name__ == "__main__":
    main()