from argparse import FileType
import os
import sys
import subprocess
import json
from copy import deepcopy
from collections import OrderedDict

WHITESPACE  =   " "
TAB         =   "\t"
RUN         =   "./"
REDIRECTION =   ">"

GUMTREE_EXECUTABLE  =   "/home/ubuntu/Projects/downloads/gumtree-3.0.0/bin/gumtree"
GUMTREE_TEXTDIFF    =   "textdiff"
GUMTREE_PARSE       =   "parse"

TEXTDIFF_DUMP       =   "textdiff.dmp"
SOURCE_PARSE_DUMP   =   "source.dmp"
TARGET_PARSE_DUMP   =   "target.dmp"

IMPORT_DECLARATION  =   "ImportDeclaration"
TYPE_DECLARATION    =   "TypeDeclaration"

data = {}

filenameMapping = {}

def textdiff(left, right):
    command = GUMTREE_EXECUTABLE + WHITESPACE + GUMTREE_TEXTDIFF + WHITESPACE + left + WHITESPACE + right
    command += WHITESPACE + REDIRECTION + WHITESPACE + TEXTDIFF_DUMP
    #os.system(command)
    print("...")
    subprocess.check_call(command, shell=True);

def parse(file, dumpfile):
    command = GUMTREE_EXECUTABLE + WHITESPACE + GUMTREE_PARSE + WHITESPACE + file
    command += WHITESPACE + REDIRECTION + WHITESPACE + dumpfile
    #print("Command:", command)
    subprocess.check_call(command, shell=True);

def isDifference(element, file):
    with open(file, "r") as fileObj:
        elementFound = False
        for line in fileObj:
            if element in line:
                return True
    
    return False

def extractKeyword(element):
    splitted = element.split()
    if len(splitted) > 1:
        return splitted[1]
    print("Second element not found")
    return ""

def findDetails1(searchString):
    if not searchString:
        return []
    
    targetTD = []
    sourceTD = []
    TD = False
    ID = False
    MD = False
    found = False

    importUpdated = []
    importCounter = 0
    with open(TARGET_PARSE_DUMP, "r") as fileObj:
        tmp = []
        mtmp = []
        for line in fileObj:
            line = line.strip()
            if "TypeDeclaration" in line and not tmp:
                TD = True

            if "TypeDeclaration" in line and tmp:
                tmp = []
                TD = True
            
            if "MethodDeclaration" in line and not tmp and not mtmp:
                MD = True
            
            if "MethodDeclaration" in line and tmp and mtmp:
                mtmp = []
                MD = True
            
            if searchString[-2].strip() in line:
                found = True
                tmp.append(line)
                return tmp, mtmp
            
            #if "MethodDeclaration" in line and found:
            #    print "bbbbbbbbb", tmp
            #    return tmp
            
            if TD:
                tmp.append(line)
            if MD:
                mtmp.append(line)
    
    return tmp, mtmp

def findDetails(searchString):

    if not searchString:
        return []
    
    targetTD = []
    sourceTD = []
    TD = False
    ID = False
    found = False

    importUpdated = []
    importCounter = 0
    with open(SOURCE_PARSE_DUMP, "r") as fileObj:
        tmp = []
        for line in fileObj:
            line = line.strip()
            if "TypeDeclaration" in line and not tmp:
                TD = True
            if "ImportDeclaration" in line and not tmp:
                ID = True
            
            if ID:
                importCounter += 1
            

            if ID and line in searchString:
                return "import", line
                ID = False
            
            if importCounter == 2:
                importCounter = 0
                ID = False

            if "TypeDeclaration" in line and tmp:
                tmp = []
                TD = True
            
            if searchString[-1] in line:
                found = True
            
            if "MethodDeclaration" in line and found:
                return "", tmp
            
            if TD:
                line = line.strip()
                tmp.append(line)
    
    return "",""
                
    
    


def extractUpdationNode():
    results = []
    tmp = []
    lastline = ""
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        lastline = fileObj.readlines()[-1]
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        updateStart = False
        prevLine = ""
        for line in fileObj:
            if "update-node" in line:
                updateStart = True
            elif ("===" in line and updateStart) or (line in lastline and updateStart):
                updateStart = False
                action, details = findDetails(tmp)
                if action == "import":
                    createDataImports(details, "updated")

                results.append(tmp)
                results.append(details)
                
                tmp = []
            
            if updateStart:
                line = line.strip("\n")
                tmp.append(line)
            prevLine = line
    
    return results

def extractUpdationNodeMethod(): #for method
    results = []
    tmp = []
    lastline = ""
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        lastline = fileObj.readlines()[-1]
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        updateStart = False
        prevLine = ""
        for line in fileObj:
            if "insert-node" in line:
                updateStart = True
            elif "===" in line and updateStart or line in lastline:
                updateStart = False
                results.append(tmp)
                tmp = []
            
            if updateStart:
                line = line.strip("\n")
                tmp.append(line)
            prevLine = line
    
    return results
            

def extractInsertClassOrImportTrees():
    results = []
    tmp = []
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        insertStart = False
        prevLine = ""
        for line in fileObj:
            if "insert-tree" in line:
                insertStart = True
            elif ("CompilationUnit" in line or "TypeDeclaration" in line and "to" in prevLine) or ("Block" in line and "to" in prevLine):
                insertStart = False
                results.append(tmp)
                tmp = []
            
            if insertStart:
                line = line.strip("\n")
                tmp.append(line)
            prevLine = line
    #print(results)
    
    return results

def extractDeleteClassOrImportTrees():
    results = []
    tmp = []
    lastline = ""
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        lastline = fileObj.readlines()[-1]
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        deleteStart = False
        prevLine = ""
        for line in fileObj:
            if "delete-tree" in line:
                deleteStart = True
            elif ("===" in line and deleteStart) or (line in lastline and deleteStart):
                tmp.append(line)
                deleteStart = False
                results.append(tmp)
                tmp = []
            
            if deleteStart:
                line = line.strip("\n")
                tmp.append(line)
            prevLine = line
    
    return results


def lookForInsertTree():
    simpleName = ""
    with open(TEXTDIFF_DUMP, "r") as fileObj:
        insertFound = False
        isImportDeclaration =   False
        isTypeDeclaration   =   False
        isModifier          =   False
        isTypeDeclarationKind   =   False
        for line in fileObj:
            if not insertFound:
                if "insert-tree" in line :
                    insertFound = True
            else:
                if IMPORT_DECLARATION in line:  #for import insertion
                   isImportDeclaration = True 
                elif TYPE_DECLARATION in line:  #for type declaration
                    isTypeDeclaration = True
                elif isImportDeclaration and "SimpleName: " in line:    #simplename for import declaration
                    simpleName = line
                elif isTypeDeclaration:
                    if "Modifier:" in line:
                        #print("1:", extractKeyword(line))
                        isModifier = True
                    elif isModifier:
                        if "TYPE_DECLARATION_KIND:" in line:
                            print("2:", extractKeyword(line))
                            isTypeDeclarationKind = True
                    

    
    if isDifference(simpleName, TARGET_PARSE_DUMP):
        addedKeyword = extractKeyword(simpleName)
        #print(addedKeyword, " imported")

def lookForDeleteTree():
    simpleName = ""

    with open(TEXTDIFF_DUMP, "r") as fileObj:
        deleteFound = False
        for line in fileObj:
            if not deleteFound:
                if "delete-tree" in line :
                    deleteFound = True
            else:
                if TYPE_IMPORT in line: #for import deletion
                   pass 
                if "SimpleName: " in line:
                    simpleName = line
    
    if isDifference(simpleName, SOURCE_PARSE_DUMP):
        addedKeyword = extractKeyword(simpleName)
        #print(addedKeyword, " deleted")
#used
def createDataImports(tion, action):
    splitted = tion.split()
    form_key = "import " + splitted[1]
    data[form_key] = action     
#used
def createDataClass(tion, action):
    splitted = tion.split()
    #print(len(splitted))
    form_key = ""
    if "SimpleType" in tion:#for extends addition case
        form_key = splitted[1] + " " + splitted[4] + " " + splitted[7] + " extends " + splitted[12]
    elif len(splitted) == 14:#for extends deletion case
        form_key = splitted[1] + " " + splitted[4] + " " + splitted[7] + " extends " + splitted[12]
    else:
        form_key = splitted[1] + " " + splitted[4] + " " + splitted[7]
    



    data[form_key] = action
#used
def checkIfDelta(addition, deletion, updation, updation1):
    additionCounter = 0
    for element in addition:
        importFound = False
        classFound  = False
        classFormString = ""
        for element1 in element:
            additionCounter += 1
            if "ImportDeclaration" in element1:
                importFound = True
            elif importFound:
                createDataImports(element1, "added")
                importFound = False
            
            if "TypeDeclaration" in element1:
                classFound = True
            elif classFound:
                classFormString += " " + element1
                if "to" == element1:
                    createDataClass(classFormString, "added")
                    classFound = False
    
    deletionCounter = 0
    for element in deletion:
        importFound = False
        classFound  = False
        classFormString = ""
        for element1 in element:
            deletionCounter += 1
            if "ImportDeclaration" in element1:
                importFound = True
            elif importFound:
                createDataImports(element1, "deleted")
                importFound = False
            
            if "TypeDeclaration" in element1:
                classFound = True
            elif classFound:
                classFormString += " " + element1
                if "\n" in element1:
                    createDataClass(classFormString, "deleted")
                    classFound = False
    
    updationCounter = 0
    for element in updation:
        classFound = False
        classFormString = ""
        extendsPresent = False
        if type(element) == type([]):
            element.append("to")
        #print(element)
        for element1 in element:
            updationCounter += 1
            if "TypeDeclaration" in element1:
                classFound = True
            elif classFound:
                classFormString += " " + element1
                if "to" == element1:
                    createDataClass(classFormString, "updated")
                    classFound = False
    
    updation1Counter = 0
    for element in updation1:
        for element1 in element:
            updation1Counter += 1
    
    return (additionCounter, deletionCounter, updationCounter, updation1Counter)



def checkIfAddedInsideClass(addition):
    toReturn = []
    defineMethod = False
    for element in addition:
        if element and len(element) > 5:
            details = findDetails1(element)
            pos = 0
            for tyo in details[0]:
                pos += 1
                if "MethodDeclaration" in tyo:
                    defineMethod = True
                    break
            parentClassName = details[0][1].split()[1] + " " + details[0][2].split()[1] + " " + details[0][3].split()[1] 
            parentFunctionName = ""
            if defineMethod:
                parentFunctionName = details[0][pos].split()[1] + " " + details[0][pos+2].split()[1] + " " + details[0][pos+3].split()[1] 
                defineMethod = False
            try:
                if not data.has_key(parentClassName):
                    data[parentClassName] = {parentFunctionName:{"added":[element[2:-1]]}}
                elif not data[parentClassName].has_key(parentFunctionName):
                    data[parentClassName][parentFunctionName] = {"added" : element[2:-1]}
                else:
                    data[parentClassName][parentFunctionName]["added"].append(element[2:-1])
            except:
                continue
    

def analyze():
    #lookForInsertTree() #type 1
    #lookForDeleteTree() #type 2
    addition = extractInsertClassOrImportTrees()
    deletion = extractDeleteClassOrImportTrees()
    updation = extractUpdationNode()
    updation1 = extractUpdationNodeMethod()

    return addition, deletion, updation
    a,d,u,u1 = checkIfDelta(addition, deletion, updation, updation1)

    checkIfAddedInsideClass(addition)

    #data[parentClassName] = {parentFunctionName: "dfd"}


    #if not a and not d and not u and not u1:
    #    print("No Changes found")
    #    return

    #print(a,d,u,u1)
    '''print("ADDITION:", addition)
    print("DELETION:", deletion)
    print("UPDATION:", updation)
    print("UPDATION1:", updation1)
    '''
    #print data
    
    
    #checkImports(addition, deletion)
    
    

    
    '''if len(addition) and len(addition[0]):
        print("Import/Class added")
    if len(deletion) and len(deletion[0]):
        print("Import/Class deleted")
    if len(updation) and len(updation[0]):
        print("Name updated")
    if len(updation1) and len(updation1[0]):
        print("Function added")
    '''
def main(sourceFile, targetFile):
    textdiff(sourceFile, targetFile)
    parse(sourceFile, SOURCE_PARSE_DUMP)
    parse(targetFile, TARGET_PARSE_DUMP)

    analyze()

#################################################################################################

class Node:
    def __init__(self, indented_line):
        self.children = []
        self.level = len(indented_line) - len(indented_line.lstrip())
        self.text = indented_line.strip()
        #self.text = indented_line.strip().split()[0]

    def add_children(self, nodes):
        childlevel = nodes[0].level
        while nodes:
            node = nodes.pop(0)
            if node.level == childlevel: # add node as a child
                self.children.append(node)
            elif node.level > childlevel: # add nodes as grandchildren of the last child
                nodes.insert(0,node)
                self.children[-1].add_children(nodes)
            elif node.level <= self.level: # this node is a sibling, no more children
                nodes.insert(0,node)
                return

    def as_dict(self):
        if len(self.children) > 1:
            return {self.text: [node.as_dict() for node in self.children]}
        elif len(self.children) == 1:
            return {self.text: self.children[0].as_dict()}
        else:
            return self.text



SEPARATOR = '    '



def translateToDict(filename, cond=None):
    if cond == None:
        fileObj = open(filename, 'r')
        indented_text = fileObj.read()
        root = Node('root')
        root.add_children([Node(line) for line in indented_text.splitlines() if line.strip()])
        d = root.as_dict()['root']
        return d
    else:
        indented_text = filename
        root = Node('root')
        root.add_children([Node(line) for line in indented_text.splitlines() if line.strip()])
        d = root.as_dict()['root']
        return d

def fetchDifferenceAsString(filename):
    diffString = ""
    collect = False
    with open(filename, 'r') as fileObj:
        for line in fileObj:
            if 'insert-tree' in line or 'insert-node' in line or 'update-node' in line or 'delete-tree' in line or 'delete-node' in line or 'move-tree' in line:
                collect = True
            if collect:
                #diffString += line.strip() + " "
                diffString += line

    return diffString

def fetchDifferenceAsList(filename):
    diffList = []
    collect = False
    with open(filename, 'r') as fileObj:
        tmp = []
        for line in fileObj:
            if 'insert-tree' in line or 'insert-node' in line or 'update-node' in line or 'delete-tree' in line or 'delete-node' in line or 'move-tree' in line:
                if collect:
                    diffList.append(tmp)
                    tmp = []
                collect = True
                
            if collect and "===" not in line:
                tmp.append(line.strip())
        
        diffList.append(tmp)

    return diffList

def extractDifferenceFromDelete(deleteList, isNode=False):
    mapping = {}
    if isNode:
        for element in deleteList:
            parent = element[0]
            if parent in mapping:
                mapping[parent].append('NA')
            else:
                mapping[parent] = ['NA']   

    else:
        for element in deleteList:
            parent = element[0]
            if parent in mapping:
                mapping[parent].append(element[1])
            else:
                mapping[parent] = [element[1]]   
    
    return mapping

def extractDifferenceFromMove(moveList):
    mapping = {}
    for element in moveList:
        index = element.index('to')
        parent = element[index+1]
        if parent in mapping:
            mapping[parent].append(element[:index])
        else:
            mapping[parent] = [element[:index]]

    return mapping
    
def extractDifferenceFromInsert(insertList, isNode=False):
    mapping = {}
    if isNode:
        for element in insertList:
            parent = element[0]
            if parent in mapping:
                mapping[parent].append(element[1])
            else:
                mapping[parent] = [element[1]]    
    else:
        for element in insertList:
            index = element.index('to')
            parent = element[index+1]
            if parent in mapping:
                mapping[parent].append(element[:index])
            else:
                mapping[parent] = [element[:index]]    
    return mapping 

def extractDifferenceFrom(insertTreeList):
    mapping = {}
    for element in insertTreeList:
        index = element.index('to')
        parent = element[index+1]
        if parent in mapping:
            mapping[parent].append(element[:index])
        else:
            mapping[parent] = [element[:index]]    
    return mapping 


def extractDifferenceFromInsertTreeBlockList(insertTreeList):
    mapping = {}
    for element in insertTreeList:
        #print element
        continue
        index = element.index('to')
        parent = element[index+1]
        if parent in mapping:
            mapping[parent].append(element[:index])
        else:
            mapping[parent] = [element[:index]]    
    return mapping 

def getParentKeysByValue(json_dict_or_list, value):
  if json_dict_or_list == value:
    return [json_dict_or_list]
  elif isinstance(json_dict_or_list, dict):
    for k, v in json_dict_or_list.items():
      p = getParentKeysByValue(v, value)
      if p:
        return [k] + p
  elif isinstance(json_dict_or_list, list):
    lst = json_dict_or_list
    for i in range(len(lst)):
      p = getParentKeysByValue(lst[i], value)
      if p:
        return [str(i)] + p 

def getParentKeysByValueSubstring(json_dict_or_list, value):
  if json_dict_or_list == value:
    return [json_dict_or_list]
  elif isinstance(json_dict_or_list, dict):
    for k, v in json_dict_or_list.items():
      p = getParentKeysByValue(v, value)
      if p:
        return [k] + p
  elif isinstance(json_dict_or_list, list):
    lst = json_dict_or_list
    for i in range(len(lst)):
      p = getParentKeysByValue(lst[i], value)
      if p:
        return [str(i)] + p

                      

def findValue(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x 

def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x

def getImportName(value):
    return value.split()[1]

def getMethodInformation(methodValue):
    toReturn = {'modifier': None, 'return type': None, 'name': None, 'parameters':[]}
    for element in methodValue:
        for element1 in element:
            #print 'hello', element1
            if 'Block ' in str(element1):
                continue
            elif 'Modifier:' in str(element1) and toReturn['modifier'] == None:
                toReturn['modifier'] = element1.split()[1]
            elif 'SimpleType' in str(element1) and 'SimpleName: ' in str(element1) and toReturn['return type'] == None:
                toReturn['return type'] = element1.values()[0].split()[1]
            elif str(element1).count('SimpleName') == 1 and toReturn['name'] == None:
                toReturn['name'] = element1.split()[1]
            elif 'SingleVariableDeclaration ' in str(element1):
                for key, value in element1.items():
                    type = None
                    variable = None
                    for e in value:
                        if 'PrimitiveType: ' in e:
                            type = e.split()[1]
                        elif 'SimpleName: ' in e:
                            variable = e.split()[1]
                    
                    toInsert = (type, variable)
                    toReturn['parameters'].append(toInsert)
    
    return toReturn

def getClassInformation(classValue):
    toReturn = {'modifier': None, 'name': None}
    for element in classValue:
        for element1 in element:
            if not type({}) == type(element1):
                if 'Modifier: ' in element1:
                    toReturn['modifier'] = element1.split()[1]
                elif 'SimpleName: ' in element1:
                    toReturn['name'] = element1.split()[1]
    
    return toReturn
            

def fetchMethodInfo(value, targetDict):
    methodDeclarationElement = ''
    #print 'crashing', value
    for element in value:
        if 'MethodDeclaration' in element:
            methodDeclarationElement = element
            break
    
    methodValue = list(findkeys(targetDict, methodDeclarationElement))
    toReturn = getMethodInformation(methodValue)

    return toReturn
    
        
def fetchClassInfo(value, targetDict):
    info = []
    typeDeclarationElement = ''
    for element in value:
        if 'TypeDeclaration' in element:
            typeDeclarationElement = element
            break
    
    classValue = list(findkeys(targetDict, typeDeclarationElement))
    toReturn = getClassInformation(classValue)
    return toReturn

def createNestedDictionary(data):
  if len(data) == 0:
      return data 
  else: 
      first_value = data[0] 
      data = {first_value : createNestedDictionary(data[1:])}
      return data

def getParentInfoForDelete(sourceDict, targetDict, mappingDeleteTreeListDiff, isNode=False):
    toReturn = {}
    if isNode:
        for key, value in mappingDeleteTreeListDiff.items():
                parentKeysList = getParentKeysByValue(sourceDict, key)
                if not parentKeysList:
                    parentKeysList = getParentKeysByKey(sourceDict, targetDict, key)
                for element in parentKeysList:
                    if element.isdigit():
                        parentKeysList.remove(element)
                tuplatedKey = tuple(parentKeysList)
                if tuplatedKey not in toReturn:
                    toReturn[tuplatedKey] = value
                else:
                    toReturn[tuplatedKey].append(value)    
    else: #this one
        for key, value in mappingDeleteTreeListDiff.items():
                parentKeysList = getParentKeysByKey(sourceDict, targetDict, key)
                for element in parentKeysList:
                    if element.isdigit():
                        parentKeysList.remove(element)
                tuplatedKey = tuple(parentKeysList)
                if tuplatedKey not in toReturn:
                    toReturn[tuplatedKey] = value
                else:
                    toReturn[tuplatedKey].append(value)    
    return toReturn

def getParentInfoForUpdate(sourceDict, mappingInsertTree):
    toReturn = {}
    for key, value in mappingInsertTree.items():
            parentKeysList = getParentKeysByValue(sourceDict, key)
            for element in parentKeysList:
                if element.isdigit():
                    parentKeysList.remove(element)
            tuplatedKey = tuple(parentKeysList)
            if tuplatedKey not in toReturn:
                toReturn[tuplatedKey] = value
            else:
                toReturn[tuplatedKey].append(value)    
    return toReturn

def getParentInfoForMove(sourceDict, targetDict, mappingMoveTreeListDiff):
    toReturn = {}
    for key, value in mappingMoveTreeListDiff.items():
            parentKeysList = getParentKeysByKey(sourceDict, targetDict, key)
            for element in parentKeysList:
                if element.isdigit():
                    parentKeysList.remove(element)
            tuplatedKey = tuple(parentKeysList)
            if tuplatedKey not in toReturn:
                toReturn[tuplatedKey] = value
            else:
                toReturn[tuplatedKey].append(value)    
    return toReturn

def replaceByFunctionName(d,sourceDict, targetDict):
    tempd = deepcopy(d)
    for key, value in tempd.items():
        for element in key:
            if "MethodDeclaration [" in element:
                values = None
                try:
                    values = list(findValue(sourceDict, element))[0]
                except IndexError:
                    values = list(findValue(targetDict, element))[0]
            
                prevType = None
                for element1 in values:
                    if isinstance(element1, str) and 'SimpleName' in element1:
                        className = 'function=' + element1.split()[1]
                        listed = list(key)
                        element1Index = listed.index(element)
                        listed[element1Index] = className
                        tuplated = tuple(listed)
                        if key in d:
                            d[tuplated] = d.pop(key)

    return d

def replaceByClassName(d, sourceDict, targetDict):
    tempd = deepcopy(d)
    for key, value in tempd.items():
        for element in key:
            if "TypeDeclaration [" in element:
                values = None
                try:
                    values = list(findValue(sourceDict, element))[0]
                except IndexError:
                    values = list(findValue(targetDict, element))[0]
            
                prevType = None
                for element1 in values:
                    if isinstance(element1, str) and 'SimpleName' in element1:
                        className = 'class=' + element1.split()[1]
                        listed = list(key)
                        element1Index = listed.index(element)
                        listed[element1Index] = className
                        tuplated = tuple(listed)
                        if key in d:
                            d[tuplated] = d.pop(key)

    return d
                        
def replaceByFileName(d, sourceDict, targetDict):
    tempd = deepcopy(d)
    for key, value in tempd.items():
        for element in key:
            if "CompilationUnit [" in element:
                fileName = 'filename=' + filenameMapping[element]
                listed = list(key)
                element1Index = listed.index(element)
                listed[element1Index] = fileName
                tuplated = tuple(listed)
                if key in d:
                    d[tuplated] = d.pop(key)

    return d

def removeOtherKeys(copyFunctionInfo, keyToKeep):
    tempcfi = deepcopy(copyFunctionInfo)
    for k in tempcfi.keys():
        if keyToKeep == k:
            continue
        else:
            copyFunctionInfo.pop(k, None)




def getParentInfoForInsert(sourceDict, targetDict, mappingInsertTree):
    toReturn = {}
    for key, value in mappingInsertTree.items():
            parentKeysList = getParentKeysByKey(sourceDict, targetDict, key)
            for element in parentKeysList:
                if element.isdigit():
                    parentKeysList.remove(element)
            tuplatedKey = tuple(parentKeysList)
            if tuplatedKey not in toReturn:
                toReturn[tuplatedKey] = value
            else:
                toReturn[tuplatedKey].append(value)    
    return toReturn

    '''for element in mappingInsertTree:
        if len(element) > 2:
            valueToSearchFor = element[1:]
            value =  getParentKeysByValue(targetDict, valueToSearchFor)
            print 'INPUT', value
            if not value:
                continue
            methodInfo = fetchMethodInfo(value, targetDict)
            classInfo  = fetchClassInfo(value, targetDict)
            #print 'OUTPUT1', methodInfo
            #print 'OUTPUT2', classInfo
            parentInfoDict['class'].append([classInfo, methodInfo])

        else:
            valueToSearchFor = element[1]
            value =  getParentKeysByValue(targetDict, valueToSearchFor)
            if "ImportDeclaration" in str(value):
                importName = getImportName(value[-1])
                parentInfoDict['import'].append(importName)

    return parentInfoDict
    '''
    




result = []
path = []
from copy import copy
 
# i is the index of the list that dict_obj is part of
def find_path(dict_obj,key,i=None):
    for k,v in dict_obj.items():
        # add key to path
        path.append(k)
        if isinstance(v,dict):
            # continue searching
            find_path(v, key,i)
        if isinstance(v,list):
            # search through list of dictionaries
            for i,item in enumerate(v):
                # add the index of list that item dict is part of, to path
                path.append(i)
                if isinstance(item,dict):
                    # continue searching in item dict
                    find_path(item, key,i)
                # if reached here, the last added index was incorrect, so removed
                path.pop()
        if k == key:
            # add path to our result
            result.append(copy(path))
        # remove the key added in the first line
        if path != []:
            path.pop()

def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x

def getParentInfoInsertForBlock(sourceDict, insertTreeBlock):
    parentInfoInsertForBlock = {'class': []}
    insertTreeBlock = list(set(insertTreeBlock))
    for val in insertTreeBlock:
        value1 = list(findkeys(sourceDict, val))
        fff = getParentKeysByValue(sourceDict, value1[0])
        methodInfo = fetchMethodInfo(fff, sourceDict)
        classInfo  = fetchClassInfo(fff, sourceDict)
        parentInfoInsertForBlock['class'].append([classInfo, methodInfo])
    
    return parentInfoInsertForBlock

def getParentKey(d):
    if isinstance(d, dict):
        for k, v in d.items():
            getParentKey(v)
    elif hasattr(d, '__iter__') and not isinstance(d, str):
        for item in d:
            getParentKey(item)
    elif isinstance(d, str):
        print(d)

    else:
        print(d)

def getParentKeysByKey(sd, td, key):
    valueOfKey = None
    parentKeys = None
    try:
        valueOfKey = list(findValue(sd, key))[0]  
        parentKeys = getParentKeysByValue(sd, valueOfKey)
        #print 'Found from source'
    except IndexError:
        valueOfKey = list(findValue(td, key))[0]
        parentKeys = getParentKeysByValue(td, valueOfKey)
        #print 'Found from target'

    parentKeys.remove(valueOfKey)
    return parentKeys


def getParentInfoForUpdate1(updateNodeList, sourceDict):
    getParentKey(sourceDict)

def createNestedDictFromList(tree_list):
    tree_dict = {}
    for key in reversed(tree_list):
        tree_dict = {key: tree_dict}
    
    return tree_dict

def mergeDicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def getListOfKeys(listOfDict, key):
    return [d.get(key, None) for d in listOfDict]

def getPosFromListOfDict(listOfDict, searchFor, keyToFind="Name"):
    index = 0
    for element in listOfDict:
        for key, value in element.items():
            if key == keyToFind and value == searchFor:
                found = True
                return index
        
        index += 1

def combineDeleteTreeResults(   deleteTreeResults,
                                functionInfo,
                                classInfo,
                                fileInfo,
                                data):
    
    for key, value in  deleteTreeResults.items():
        copyFileInfo = deepcopy(fileInfo)
        copyClassInfo = deepcopy(classInfo)
        copyFunctionInfo = deepcopy(functionInfo)

        filename = ""
        importdeclarationname = ""
        classname = ""
        fielddeclarationname = ""
        functionname = ""
        blockname = ""
        modifiername = ""

        for element in key:
            if 'filename=' in element:
                filename = element.split('=')[1]
            elif 'class=' in element:
                classname = element.split('=')[1]
            elif 'function=' in element:
                functionname = element.split('=')[1]
            elif 'Block [' in element:
                blockname = element
            elif 'FieldDeclaration' in element:
                fielddeclarationname = element
            elif 'Modifier: ' in element:
                modifiername = element
            elif 'ImportDeclaration [' in element:
                importdeclarationname = element
        
        if functionname:
            copyFunctionInfo["Function"] = functionname
            removeOtherKeys(copyFunctionInfo, "Function")
            copyClassInfo["Function Deleted"].append(copyFunctionInfo)
            
        if fielddeclarationname:
            copyClassInfo["Field Declaration Deleted"] += 1
        if classname:             
            copyClassInfo["Class"] = classname
            if classname in key[-1]:
                for i in value:
                    if 'FieldDeclaration [' in i[0]:
                        copyClassInfo["Field Declaration Modified"] += 1
                        copyFileInfo["Class Modified"]["Class"].append(copyClassInfo)
                    elif 'MethodDeclaration [' in i[0]:
                        copyFunctionInfoTmp = deepcopy(functionInfo)
                        copyFunctionInfoTmp["Function"] = functionname
                        copyClassInfo["Function Modified"]["Function"].append(copyFunctionInfoTmp)
                        copyFileInfo["Class Modified"]["Class"].append(copyClassInfo)
            else:
                copyFileInfo["Class Modified"].append(copyClassInfo)
        importList = []
        if importdeclarationname:
            importList.append(value[0].split()[1])
            copyFileInfo["Import Deleted"].append(value[0].split()[1])
        
        if filename:
            copyFileInfo["File"] = filename

        if filename and filename in getListOfKeys(data["Files Modified"], "File"):
            filePos = getPosFromListOfDict(data["Files Modified"], filename, "File")
            if classname and classname in getListOfKeys(data["Files Modified"][filePos]["Class Modified"], "Class"):
                classPos = getPosFromListOfDict(data["Files Modified"][filePos]["Class Modified"], classname, "Class")
                if functionname and functionname in getListOfKeys(data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"], "Function"):
                    pass #need to do something here later
                elif classPos >= 0:
                    updateClass(data["Files Modified"][filePos]["Class Modified"][classPos], copyClassInfo)
                else:
                    data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"].append(copyFunctionInfo)
            elif importdeclarationname:
                for im in importList:
                    data["Files Modified"][filePos]["Import Deleted"].append(im)
                
            else:
                data["Files Modified"][filePos]["Class Deleted"].append(copyClassInfo)

        else:
            data["Files Modified"].append(copyFileInfo)
        
    
    return data

def updateClass(data, copyClassInfo):
    if not copyClassInfo['Field Declaration Added'] == 0:
        data['Field Declaration Added'] += 1
    elif not copyClassInfo['Field Declaration Deleted'] == 0:
        data['Field Declaration Deleted'] += 1
    elif not copyClassInfo['Field Declaration Modified'] == 0:
        data['Field Declaration Modified'] += 1




def combineUpdateNodeResults(   updateNodeResults,
                                functionInfo,
                                classInfo,
                                fileInfo,
                                data):
    
    for key, value in  updateNodeResults.items():
        copyFileInfo = deepcopy(fileInfo)
        copyClassInfo = deepcopy(classInfo)
        copyFunctionInfo = deepcopy(functionInfo)

        filename = ""
        importdeclarationname = ""
        classname = ""
        fielddeclarationname = ""
        functionname = ""
        blockname = ""
        modifiername = ""

        for element in key:
            if 'filename=' in element:
                filename = element.split('=')[1]
            elif 'class=' in element:
                classname = element.split('=')[1]
            elif 'function=' in element:
                functionname = element.split('=')[1]
            elif 'Block [' in element:
                blockname = element
            elif 'FieldDeclaration' in element:
                fielddeclarationname = element
            elif 'Modifier: ' in element:
                modifiername = element
            elif 'ImportDeclaration [' in element:
                importdeclarationname = element
                
        if modifiername:
            if functionname:
                copyFunctionInfo["Modifier Modified"] = "Yes"
            else:
                copyClassInfo["Modifier Modified"] = "Yes"

        if functionname:
            copyFunctionInfo["Function"] = functionname
            copyClassInfo["Function Modified"].append(copyFunctionInfo)
        if fielddeclarationname:
            copyClassInfo["Field Declaration Modified"] += 1
        if classname:             
            copyClassInfo["Class"] = classname
            if classname in key[-1]:
                for i in value:
                    if 'FieldDeclaration [' in i[0]:
                        copyClassInfo["Field Declaration Modified"] += 1
                        copyFileInfo["Class Modified"]["Class"].append(copyClassInfo)
                    elif 'MethodDeclaration [' in i[0]:
                        copyFunctionInfoTmp = deepcopy(functionInfo)
                        copyFunctionInfoTmp["Function"] = functionname
                        copyClassInfo["Function Modified"]["Function"].append(copyFunctionInfoTmp)
                        copyFileInfo["Class Modified"]["Class"].append(copyClassInfo)
            else:
                copyFileInfo["Class Modified"].append(copyClassInfo)
        importList = []
        if importdeclarationname:
            importList.append(value[0])
            copyFileInfo["Import Modified"].append(value[0])
        
        if filename:
            copyFileInfo["File"] = filename

        if filename and filename in getListOfKeys(data["Files Modified"], "File"):
            filePos = getPosFromListOfDict(data["Files Modified"], filename, "File")
            if classname and classname in getListOfKeys(data["Files Modified"][filePos]["Class Modified"], "Class"):
                classPos = getPosFromListOfDict(data["Files Modified"][filePos]["Class Modified"], classname, "Class")
                if functionname and functionname in getListOfKeys(data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"], "Function"):
                    '''functionPos = getPosFromListOfDict(data["Files Modified"]["Files"][filePos]["Class Modified"]["Class"][classPos]["Function Modified"]["Function"], functionname)
                    if blockname:
                        try:
                            data["Files Modified"]["Files"][filePos]["Class Modified"]["Class"][classPos]["Function Modified"]["Function"][functionPos].append(copyBlockInfo)
                        except AttributeError:
                            data["Files Modified"]["Files"][filePos]["Class Modified"]["Class"][classPos]["Function Modified"]["Function"][functionPos]["Block"] = copyBlockInfo
                        data["Files Modified"]["Files"][filePos]["Class Modified"]["Class"][classPos]["Function Modified"]["Count"] += 1
                    '''
                elif classPos >= 0:
                    updateClass(data["Files Modified"][filePos]["Class Modified"][classPos], copyClassInfo)
                else:
                    data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"].append(copyFunctionInfo)
            elif importdeclarationname:
                for im in importList:
                    data["Files Modified"][filePos]["Import Modified"].append(im)
                
            else:
                data["Files Modified"][filePos]["Class Modified"].append(copyClassInfo)

        else:
            data["Files Modified"].append(copyFileInfo)
        
    
    return data
        

def combineInsertTreeResults( insertTreeResults,
                                functionInfo,
                                classInfo,
                                fileInfo,
                                data):
    keyList = []
    count = 0
    for key, value in  insertTreeResults.items():
        copyFileInfo = deepcopy(fileInfo)
        copyClassInfo = deepcopy(classInfo)
        copyFunctionInfo = deepcopy(functionInfo)

        filename = ""
        importdeclaration = ""
        classname = ""
        classdeclaration = ""
        fielddeclarationname = ""
        functionname = ""
        blockname = ""

        for element in key:
            if 'filename=' in element:
                filename = element.split('=')[1]
            elif 'class=' in element:
                classname = element.split('=')[1]
            elif 'function=' in element:
                functionname = element.split('=')[1]
            elif 'Block [' in element:
                blockname = element
            elif 'FieldDeclaration' in element:
                fielddeclarationname = element

        if blockname:
            copyFunctionInfo["Block Added/Deleted"] = "Yes"
        if functionname:
            copyFunctionInfo["Function"] = functionname
            copyClassInfo["Function Modified"].append(copyFunctionInfo)
        if fielddeclarationname:
            copyClassInfo["Field Declaration Added"] += 1
        if classname:             
            copyClassInfo["Class"] = classname

        if classname in key[-1]:
            for i in value:
                if 'FieldDeclaration [' in i[0]:
                    copyClassInfo["Field Declaration Added"] += 1
                elif 'MethodDeclaration [' in i[0]:
                    functionname = [e for e in i if 'SimpleName: ' in e][0].split()[1]
                    copyFunctionInfoTmp = deepcopy(functionInfo)
                    copyFunctionInfoTmp["Function"] = functionname
                    copyClassInfo["Function Added"].append(copyFunctionInfoTmp)
                
                if copyClassInfo not in copyFileInfo["Class Modified"]:
                    copyFileInfo["Class Modified"].append(copyClassInfo)
        else:
            copyFileInfo["Class Modified"].append(copyClassInfo)
            

        importList = []
        classList = []
        if filename in key[-1]:
            for i in value:
                if 'ImportDeclaration [' in i[0]:
                    importdeclaration = i[0]
                    importList.append(i[1].split()[1])
                    copyFileInfo["Import Added"].append(i[1].split()[1])
                elif 'TypeDeclaration [' in i[0]:
                    classdeclaration = i[0]
                    classadded = [e for e in i if 'SimpleName: ' in e][0].split()[1]
                    classList.append(classadded)
                    copyFileInfo["Class Added"].append(classadded)

        if filename:
            copyFileInfo["File"] = filename
        
        if filename and filename in getListOfKeys(data["Files Modified"], "File"):
            filePos = getPosFromListOfDict(data["Files Modified"], filename, "File")
            if classname and classname in getListOfKeys(data["Files Modified"][filePos]["Class Modified"], "Class"):
                classPos = getPosFromListOfDict(data["Files Modified"][filePos]["Class Modified"], classname, "Class")
                if functionname and functionname in getListOfKeys(data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"], "Function"):
                    '''functionPos = getPosFromListOfDict(data["Files ModifiecombineAllResultsd"][filePos]["Class Modified"][classPos]["Function Modified"], functionname, "Function")
                    if blockname:
                        try:
                            data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"][functionPos].append(copyBlockInfo)
                        except AttributeError:
                            data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"][functionPos]["Block"] = copyBlockInfo
                    '''
                else:
                    data["Files Modified"][filePos]["Class Modified"][classPos]["Function Modified"].append(copyFunctionInfo)                    
            elif importdeclaration:
                for im in importList:
                    data["Files Modified"][filePos]["Import Added"].append(im)  
            elif classdeclaration:
                for c in classList:
                    data['Files Modified'][filePos]['Class Added'].append(c)         
            else:
                data["Files Modified"][filePos]["Class Modified"].append(copyClassInfo)
        else:
            data["Files Modified"].append(copyFileInfo)
        
    
    return data
    

def combineAllResults(insertTreeResults, insertNodeResults, updateNodeResults, deleteTreeResults, deleteNodeResults, moveTreeResults):
    functionInfo                =   {"Function": "",
                                                "Block Modified":"No",
                                                "Block Added/Deleted": "No",
                                                "Param Modified": 0,
                                                "Param Added/Deleted": 0,
                                                "Return Type Modified": "No",
                                                "Modifier Modified": "No"
                                                }
    classInfo                   =   {"Class": "", 
                                                "Function Modified":[], 
                                                "Function Added":[],
                                                "Function Deleted":[],  
                                                "Modifier Modified": "No",
                                                "Field Declaration Modified": 0, 
                                                "Field Declaration Added": 0, 
                                                "Field Declaration Deleted": 0
                                                }
    fileInfo                    =   {"File": "",
                                            "Import Modified":[],
                                            "Import Added":[],
                                            "Import Deleted":[],
                                            "Class Modified":[],
                                            "Class Added":[],
                                            "Class Deleted":[]}
    #data                        =   {"Files Modified": [], "Files Added": [], "Files Deleted": []}
    data                        =   {"Files Modified": []}

    data = combineInsertTreeResults( insertTreeResults,
                                functionInfo,
                                classInfo,
                                fileInfo,
                                data)
    
    data = combineUpdateNodeResults(   updateNodeResults,
                                functionInfo,
                                classInfo,
                                fileInfo,
                                data)
    
    
    for key, value in insertNodeResults.items():
        pass

    data = combineDeleteTreeResults(   deleteTreeResults,
                                functionInfo,
                                classInfo,
                                fileInfo,
                                data)

    for key, value in  deleteNodeResults.items():
        pass
    
    for key, value in moveTreeResults.items():
        pass

    return data


def start(srcFile, targetFile, actionType):
  try:
    filesDeleted = {'Files Deleted': []}
    filesAdded = {'Files Added': []}
    if actionType == 'deleted':
        for file in srcFile:
            filesDeleted['Files Deleted'].append({'File': file})
        return filesDeleted
    elif actionType == 'added':
        for file in srcFile:
            filesAdded['Files Added'].append({'File': file})
        return filesAdded
    main(srcFile, targetFile)
    sourceDict = translateToDict(SOURCE_PARSE_DUMP)
    filenameMapping[next(iter(sourceDict))] = srcFile
    targetDict = translateToDict(TARGET_PARSE_DUMP)
    filenameMapping[next(iter(targetDict))] = targetFile

    targetDictStr = str(targetDict)
    sourceDictStr = str(sourceDict)

    diffString = fetchDifferenceAsString(TEXTDIFF_DUMP)
    diffList = fetchDifferenceAsList(TEXTDIFF_DUMP)

    splitted = diffString.split("===")

    insertTreeList = []
    insertTreeBlockList = []
    insertNodeList = []
    updateNodeList = []
    deleteTreeList = []
    deleteNodeList = []
    moveTreeList = []

    count = 1
    for s in diffList:
        
        if s and 'insert-tree' in s[0]:
            if False:#'Block' in str(s):
                blockFound = False
                for i in s:
                    if 'to' == i:
                        blockFound = True
                    elif blockFound:
                        insertTreeBlockList.append(i)
                        blockFound=False
            
            else:
                insertTreeList.append(s[2:])
        elif s and 'insert-node' in s[0]:
            insertNodeList.append(s[2:])
        elif s and 'update-node' in s[0]:
            updateNodeList.append(s[2:])   
            #print updateNodeList         
        elif s and  'delete-tree' in s:
            deleteTreeList.append(s[2:])
        elif s and 'delete-node' in s:
            deleteNodeList.append(s[2:])
        elif s and 'move-tree' in s:
            moveTreeList.append(s[2:])

    mappingInsertTreeListDiff = extractDifferenceFromInsert(insertTreeList)
    mappingInsertNodeListDiff = extractDifferenceFromInsert(insertNodeList)
    mappingUpdateNodeListDiff = extractDifferenceFromInsert(updateNodeList, True)
    mappingDeleteTreeListDiff = extractDifferenceFromDelete(deleteTreeList)
    mappingDeleteNodeListDiff = extractDifferenceFromDelete(deleteNodeList, True)
    mappingMoveTreeListDiff = extractDifferenceFromMove(moveTreeList)

    insertTreeResults = getParentInfoForInsert(sourceDict, targetDict, mappingInsertTreeListDiff)
    #print insertTreeResults
    #print ""
    insertNodeResults = getParentInfoForInsert(sourceDict, targetDict, mappingInsertNodeListDiff)
    updateNodeResults = getParentInfoForUpdate(sourceDict, mappingUpdateNodeListDiff)
    deleteTreeResults = getParentInfoForDelete(sourceDict, targetDict, mappingDeleteTreeListDiff)
    deleteNodeResults = getParentInfoForDelete(sourceDict, targetDict, mappingDeleteNodeListDiff, True)
    moveTreeResults = getParentInfoForMove(sourceDict, targetDict, mappingMoveTreeListDiff)

    insertTreeResults = replaceByFileName(insertTreeResults, sourceDict, targetDict)
    #print insertTreeResults
    #print ""
    insertNodeResults = replaceByFileName(insertNodeResults, sourceDict, targetDict)
    updateNodeResults = replaceByFileName(updateNodeResults, sourceDict, targetDict)
    deleteTreeResults = replaceByFileName(deleteTreeResults, sourceDict, targetDict)
    deleteNodeResults = replaceByFileName(deleteNodeResults, sourceDict, targetDict)
    moveTreeResults = replaceByFileName(moveTreeResults, sourceDict, targetDict)

    insertTreeResults = replaceByClassName(insertTreeResults, sourceDict, targetDict)
    #print insertTreeResults
    #print ""
    insertNodeResults = replaceByClassName(insertNodeResults, sourceDict, targetDict)
    updateNodeResults = replaceByClassName(updateNodeResults, sourceDict, targetDict)
    deleteTreeResults = replaceByClassName(deleteTreeResults, sourceDict, targetDict)
    deleteNodeResults = replaceByClassName(deleteNodeResults, sourceDict, targetDict)
    moveTreeResults = replaceByClassName(moveTreeResults, sourceDict, targetDict)

    insertTreeResults = replaceByFunctionName(insertTreeResults, sourceDict, targetDict)
    #print insertTreeResults
    insertNodeResults = replaceByFunctionName(insertNodeResults, sourceDict, targetDict)
    updateNodeResults = replaceByFunctionName(updateNodeResults, sourceDict, targetDict)
    deleteTreeResults = replaceByFunctionName(deleteTreeResults, sourceDict, targetDict)
    deleteNodeResults = replaceByFunctionName(deleteNodeResults, sourceDict, targetDict)
    moveTreeResults = replaceByFunctionName(moveTreeResults, sourceDict, targetDict)

    combinedResults = combineAllResults(insertTreeResults, insertNodeResults, updateNodeResults, deleteTreeResults, deleteNodeResults, moveTreeResults)

    return combinedResults
  except Exception as ex:
    print('Exception caught here', ex)
    return {"Files Modified": []}

