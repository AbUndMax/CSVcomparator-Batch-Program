# This Script is used to compare two CSV files by checking if the data of a label x in File 1 is the same data of label x in File 2!
# This is done in the following pattern:
### by starting the skript, the path of two CSV files is provided with the first one beeing the one which gets compared two the second one!
### the programm will then ask in which column the label is put in the first file
### then it will aks hwo the column of the labels is called in the second file
### then the program wants pairs of names. These pairs are the mathcing column names
###### eg.: in File 1 a column may be named "uno" but in the second file the column with the same data is called "u"
######      the pair is written like this: "uno:u" or: "firstFileColName:SecondFileColName"


import csv
import time
import argparse
import sys
from typing import Tuple, List, Dict, Optional

parser = argparse.ArgumentParser(description="CSV comparator script - labels per row and have to be identical!")
# TODO add colname pairs and label ColName pairs as parameters (make a batch programm)
parser.add_argument("-f1", "--file1", type=str, required=True, help="Path of the file which gets compared to the second one")
parser.add_argument("-f2", "--file2", type=str, required=True, help="Path of the file which is compared to the first one")
parser.add_argument("-v", "--verbose", action="store_true")

args = parser.parse_args()

# loads the given csv file into a matrix
def loadCSVcontent(path) -> List[str]:
    content = []
    try:
        # open first file
        with open(path, newline="", encoding="UTF-8") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=";")
            for row in csvreader:
                content.append(row)
        return content
    except FileNotFoundError:
        print(f"<<<<<<! the file {path} could not be found !>>>>>>")
        sys.exit(1)
    except Exception as e:
        print(f"<<<<<<! An error occured: {e} !>>>>>>")
        
file1Content = loadCSVcontent(args.file1)
file2Content = loadCSVcontent(args.file2)

print("################################################ FILE 1 CONTENT ####################################################")
print(file1Content)
print("\n####################################################################################################################")

# returns labelList and dic of label: index in fileContent
def getColNameForLabelsFromUser(fileNumber, content) -> Tuple[List[str], Dict[str, int]]:
    labelColFound = False
    while not labelColFound:
        userInput = input(f"how is the column of the {fileNumber} file called in which the labels are stored?\n")
        try:
            labelColIndex = content[0].index(userInput)
            # A List of all labels WITHOUT the colName of the LabelCol
            labelSet = set([row[labelColIndex] for row in content[1:]])
            labelDic = {}
            for index, label in enumerate(labelSet):
                labelDic.update({label: index + 1}) # +1 because the colname is index 0 whch is missing in the label list
            
            return labelSet, labelDic
        except ValueError:
            print(f"<<<<<<! {userInput} is not contained in the provided file !>>>>>>")
            
            
####### Für die Implementation dass er zwei Files vergelichen kann WO NICHT ALLE LABELS in beiden vorkommen (es also nur eine Schnittmenge gibt)
### einfach die Schnittmenge der Labels bilden und als liste speichern -> nur diese Labels werden verglichen.

####### wenn 9999 und leere Zelle verglichen werden ist das KEIN FEHLER! (evtl ein parameter geben dem man übergeibt welche werte ignoriert werden sollen!)            


## check if labelListFile1 is subset of labelListFile2
is_LabelListFile1_SubSet = False
while not is_LabelListFile1_SubSet:
    labelSetFile1, labelDicFile1 = getColNameForLabelsFromUser(1, file1Content)
    labelSetFile2, labelDicFile2 = getColNameForLabelsFromUser(2, file2Content)
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

def printDic(dic):
    for key, value in labelDicFile1.items():
        print(key + ": " + str(value))

printDic(labelDicFile1)
printDic(labelDicFile2)

    
def getColNamePairsFromUser() -> tuple[List[List[str]], Dict[str, int], Dict[str, int]]:
    while True:
        colPairs = []
        userInput = input("provide all corresponding column name pairs in a way like: file1ColName1:::file2ColName1, file1ColName2:::file2ColName2, etc...\n")
        pairs = userInput.split(sep=", ")
        for string in pairs:
            pair = string.split(sep=":::")
            colPairs.append(pair)
            
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

colPairs, colNameDicFile1, colNameDicFile2 = getColNamePairsFromUser()

# This is the actual comparison of the corresponding values, it returns None if all vals are equal else it returns the position of the 
# mismatched value
def compareValues() -> Dict[str, List[List[str]]]:
    wrongValuesCoordinates = {}
    for label in labelIntersection:
        for pair in colPairs:
            file1Value = file1Content[labelDicFile1.get(label)][colNameDicFile1.get(pair[0])]
            file2Value = file2Content[labelDicFile2.get(label)][colNameDicFile2.get(pair[1])]
            
            if file1Value == file2Value:
                continue
            elif label in wrongValuesCoordinates: # if the values are not the same, they have to be diffrent which means we just check if label already has wrong Values
                wrongValuesCoordinates.get(label).append([pair[0], pair[1]])
            else:
                wrongValuesCoordinates.update({label: [[pair[0], pair[1]]]})
                
    return wrongValuesCoordinates
            
if not (wrongValues := compareValues()):
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