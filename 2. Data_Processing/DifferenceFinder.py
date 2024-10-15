from distutils import filelist
from doctest import testfile
import posixpath
import sys
import os
import shutil
import subprocess
import json
import csv

import urllib3
import common
import Java_Source_Code_Diff

logFileName = "log.txt"
TESTING = False
DEBUG = True

def disablePrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

def cloneMaster(reponame):
    gitCloneCommand = "git clone " + reponame
    clonedFolderName = reponame.split('/')[-1]
    clonedFolderName = clonedFolderName.split('.git')[0]
    removeCommand = 'rm -rf ' + clonedFolderName + '*'
    os.system(removeCommand)
    os.system(gitCloneCommand)
    return clonedFolderName

def makeCopyByCommitId(clonedFolderName, targetCommitId):
    currentPath = os.getcwd()

    targetFolderPath = os.path.join(currentPath, clonedFolderName + "_" + targetCommitId)
    clonedFolderPath = os.path.join(currentPath, clonedFolderName)

    try:
        shutil.copytree(clonedFolderPath, targetFolderPath)
    except Exception as ex:
        print('Exception caught1', ex)
        shutil.rmtree(clonedFolderPath)
        shutil.rmtree(targetFolderPath)
        return (None, None)

    createTargetFolderCommand = "git checkout " + targetCommitId 

    os.chdir(targetFolderPath)
    os.system(createTargetFolderCommand)

    getPreviousLogsCommand =     "git log -n 2"
    out = subprocess.check_output(getPreviousLogsCommand.split()).decode("utf-8") 
    counter = 0
    srcCommitId = ''
    for line in out.split("\n"):
        if 'commit ' in line:
            counter += 1
            if counter == 2:
                srcCommitId = line.split()[1]
                

    srcFolderPath = os.path.join(currentPath, clonedFolderName + "_" + srcCommitId)

    try:
        shutil.copytree(clonedFolderPath, srcFolderPath)
    except Exception as ex:
        print('Exception caught2', ex)
        shutil.rmtree(clonedFolderPath)
        shutil.rmtree(srcFolderPath)
        return (None, None)
    
    createSrcFolderCommand = "git checkout " + srcCommitId

    os.chdir(srcFolderPath)
    os.system(createSrcFolderCommand)

    os.chdir(currentPath)

    return (targetFolderPath, srcFolderPath, srcCommitId)

def getModifiedFiles(targetFolderPath, srcFolderPath, fileType='java'):
    deletedFileList = []
    modifiedFileList = []
    diffCommand = ''
    diffFile = ''
    if fileType == 'java':
        diffCommand = "diff --brief -r " + targetFolderPath + " " + srcFolderPath + " | grep \'\.java\' > codediff.txt"
        diffFile = 'codediff.txt'
    else:
        diffCommand = "diff --brief -r " + targetFolderPath + " " + srcFolderPath + "  > ncfdiff.txt"
        diffFile = 'ncfdiff.txt'
    os.system(diffCommand)
    fileList = []
    with open(diffFile) as fileObj:
        for line in fileObj.readlines():
            if 'Only in ' in line:
                if srcFolderPath in line:
                    deletedParentPath = line.split()[2].strip(':')
                    filename = line.split()[-1]
                    deletedFileList.append(os.path.join(deletedParentPath, filename))
                continue
            else:
                targetFile = line.split()[1]
                srcFile = line.split()[3]
                modifiedFileList.append((targetFile, srcFile))
    
    return modifiedFileList, deletedFileList
    
testRepo = "https://github.com/testdouble/java-testing-example/commit/693ec1e7edd16c0915db07ef96b2593d68daadf4"

def fetchUrlInfo(currentCommitUrl):
    print(currentCommitUrl)
    splitted = currentCommitUrl.split("commit")
    reponame = splitted[0]
    targetCommitId = splitted[1]

    reponame = reponame.strip('/')
    targetCommitId = targetCommitId.strip('/')

    return reponame, targetCommitId

def dumpOutputToJson(output, path):
    filejson = open(os.path.join(path, 'result.json'), "w")
    json.dump(output, filejson)
    filejson.close()

def dumpOutputToCSV(machine, path):
    filecsv = open(os.path.join(path, 'machine.csv'), 'w')
    writer = csv.writer(filecsv)
    rows = []
    rows.append(machine.keys())
    rows.append(machine.values())
    print(machine.values())
    for row in rows: 
        writer.writerow(row)
    filecsv.close()

def parseArgs(args):
    categoryId = args[1]
    sourceUrlType = args[2]

    if sourceUrlType.lower().endswith('txt'):
        sourceUrlType = 'text'
        sourceUrl = args[2].split('/')[-1].split('.txt')[0]
    else:
        sourceUrlType = 'link'
        sourceUrl = 'Individual'
    
    return categoryId, sourceUrlType, sourceUrl, args[2]

def createOutputDirectory(sourceUrl, cwd=True):
    pwd = None
    
    if cwd:
        pwd = os.getcwd()
    else:
        pwd = sourceUrl
    dirpath = os.path.join(pwd, sourceUrl)

    if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)

    os.mkdir(dirpath)

    return dirpath

def getFileTypeList(modifiedFileList, isModified=False):
    srcFiles = []
    testFiles = []
    for entry in modifiedFileList:
        splitted = None
        if isModified:
            splitted = entry[1].split(os.sep)
        else:
            splitted = entry.split(os.sep)
        if 'src' in splitted and 'test' in splitted:
            testFiles.append(entry)
        else:
            srcFiles.append(entry)
    
    return srcFiles, testFiles

def formFinalResult(srcFiles, testFiles,
                    srcFilesAdded, testFilesAdded,
                    srcFilesDeleted, testFilesDeleted):

    result = {}
    srcDataMod = {'Files Modified':[]}
    testDataMod = {'Files Modified':[]}
    for entry in srcFiles:
        if not srcDataMod:
            try:
                srcDataMod = Java_Source_Code_Diff.start(entry[1], entry[0], 'modified')
            except Exception as ex:
                print('Exception caught here5', ex)
        else:
            tmp = Java_Source_Code_Diff.start(entry[1], entry[0], 'modified')
            srcDataMod['Files Modified'].extend(tmp['Files Modified'])

    srcDataDel = Java_Source_Code_Diff.start(srcFilesDeleted, None, 'deleted')
    srcDataAdd = Java_Source_Code_Diff.start(srcFilesAdded, None, 'added')
    
    srcDataMod.update(srcDataAdd)
    srcDataMod.update(srcDataDel)
    result['SRC_FILES'] = srcDataMod

    for entry in testFiles:            
        if not testDataMod:
            testDataMod = Java_Source_Code_Diff.start(entry[1], entry[0], 'modified')
        else:
            tmp = Java_Source_Code_Diff.start(entry[1], entry[0], 'modified')
            testDataMod['Files Modified'].extend(tmp['Files Modified'])
    
    testDataDel = Java_Source_Code_Diff.start(testFilesDeleted, None, 'deleted')
    testDataAdd = Java_Source_Code_Diff.start(testFilesAdded, None, 'added')
    
    testDataMod.update(testDataAdd)
    testDataMod.update(testDataDel)
    result['TEST_FILES'] = testDataMod

    result['BUILD_FILES'] = {}

    return result

def srcFilesMachine(result):
    countCFA = 0
    countCFD =0
    countCFM = 0
    countCFM_CD = 0
    countCFM_CD_FD = 0
    countCFM_CA = 0
    countCFM_CA_FA = 0
    countCFM_CM = 0
    countCFM_CA_FA = 0
    countCFM_CM = 0
    countCFM_CM_FD = 0
    countCFM_CM_FA = 0
    countCFM_CM_FM = 0

    for cfm in result['SRC_FILES'].get('Files Modified', []):
        countCFM += 1
        for cfm_cm in cfm['Class Modified']:
            countCFM_CM += 1
            for cfm_cm_fm in cfm_cm['Function Modified']:
                countCFM_CM_FM += 1
            for cfm_cm_fa in cfm_cm['Function Added']:
                countCFM_CM_FA += 1
            for cfm_cm_fd in cfm_cm['Function Deleted']:
                countCFM_CM_FD += 1
        for cfm_cd in cfm['Class Deleted']:
            countCFM_CD += 1
        for cfm_ca in cfm['Class Added']:
            countCFM_CA_+= 1
    for cfa in result['SRC_FILES']['Files Added']:
        countCFA += 1   
    for cfd in result['SRC_FILES']['Files Deleted']:
        countCFD += 1
    
    common.machine['CFM'] = countCFM
    common.machine['CFM_CM'] = countCFM_CM
    common.machine['CFM_CM_FM'] = countCFM_CM_FM
    common.machine['CFM_CM_FA'] = countCFM_CM_FA
    common.machine['CFM_CM_FD'] = countCFM_CM_FD
    common.machine['CFM_CD'] = countCFM_CD
    common.machine['CFM_CA'] = countCFM_CA
    common.machine['CFA'] = countCFA
    common.machine['CFD'] = countCFD

def testFilesMachine(result):
    countTFA = 0
    countTFD =0
    countTFM = 0
    countTFM_CD = 0
    countTFM_CD_FD = 0
    countTFM_CA = 0
    countTFM_CA_FA = 0
    countTFM_CM = 0
    countTFM_CA_FA = 0
    countTFM_CM = 0
    countTFM_CM_FD = 0
    countTFM_CM_FA = 0
    countTFM_CM_FM = 0

    for tfm in result['TEST_FILES'].get('Files Modified', []):
        countTFM += 1
        for tfm_cm in tfm['Class Modified']:
            countTFM_CM += 1
            for tfm_cm_fm in tfm_cm['Function Modified']:
                countTFM_CM_FM += 1
            for tfm_cm_fa in tfm_cm['Function Added']:
                countTFM_CM_FA += 1
            for tfm_cm_fd in tfm_cm['Function Deleted']:
                countTFM_CM_FD += 1
        for tfm_cd in tfm['Class Deleted']:
            countTFM_CD += 1
        for tfm_ca in tfm['Class Added']:
            countTFM_CA_+= 1
    for tfa in result['TEST_FILES']['Files Added']:
        countTFA += 1   
    for tfd in result['TEST_FILES']['Files Deleted']:
        countTFD += 1
    
    common.machine['TFM'] = countTFM
    common.machine['TFM_CM'] = countTFM_CM
    common.machine['TFM_CM_FM'] = countTFM_CM_FM
    common.machine['TFM_CM_FA'] = countTFM_CM_FA
    common.machine['TFM_CM_FD'] = countTFM_CM_FD
    common.machine['TFM_CD'] = countTFM_CD
    common.machine['TFM_CA'] = countTFM_CA
    common.machine['TFA'] = countTFA
    common.machine['TFD'] = countTFD

def formFinalMachine(result, NCF, categoryId, sourceCommitLinkFull):
    testFilesMachine(result)
    srcFilesMachine(result)
    
    common.machine['NCF'] = NCF
    common.machine['Category'] = int(categoryId)
    common.machine['Previous Commit Link'] = sourceCommitLinkFull
    
    return common.machine

def getUrlList(passedUrlArg):
    urlList = []
    with open(passedUrlArg, 'r') as fileObj:
        contents = fileObj.readlines()
        for line in contents:
            urlList.append(line.strip())

    return urlList

def getNCFCount(targetFolderPath):
    commandNCF = 'find' + ' ' + targetFolderPath + ' *.* | grep -v .java | wc -l > ncf.txt'
    os.system(commandNCF)
    with open('ncf.txt', 'r') as fileObj:
        for line in fileObj.readlines():
            return line.strip('\n')

if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Insufficient arguments passed")
        print("Usage: python3 DifferenceFinder.py <Category_ID> <Commit_Id/Commit file path>")
        exit(0)

    if not DEBUG:
        disablePrint()

    categoryId, sourceUrlType, sourceUrl, passedUrlArg = parseArgs(sys.argv)    
    outputDir = createOutputDirectory(sourceUrl)

    print(sourceUrl, sourceUrlType)

    clonedFolderName = None
    targetFolderPath = None
    srcFolderPath = None
    targetCommitId = None
    currentCommitUrl = None
    urlList = []

    if sourceUrlType == 'link':
        urlList.append(passedUrlArg)
    else:
        urlList = getUrlList(passedUrlArg)
    print(urlList)
    
    for currentCommitUrl in urlList:
      try:
        reponame, targetCommitId = fetchUrlInfo(currentCommitUrl)
        clonedFolderName = cloneMaster(reponame)
        targetFolderPath, srcFolderPath, srcCommitId = makeCopyByCommitId(clonedFolderName, targetCommitId)

        print('currentCommitUrl:', currentCommitUrl)
        sourceCommitLinkFull = ''
        splitted = currentCommitUrl.split('/')
        rejoined = '/'.join(splitted[:-1])
        print('rejoined:', rejoined)
        sourceCommitLinkFull = rejoined + '/' + srcCommitId
        print('sourceCommitLinkFull', sourceCommitLinkFull)

        modifiedFileList, deletedFileList = getModifiedFiles(targetFolderPath, srcFolderPath)
        print('Modified file list:', modifiedFileList)
        print('Modified file count:', len(modifiedFileList))
        print()

        print('Deleted file list:', deletedFileList)
        print('Deleted file count:', len(deletedFileList))
        print()

        modifiedFileListNCF, deletedFileListNCF = getModifiedFiles(targetFolderPath, srcFolderPath, 'NCF')

        print('Modified NCF list:', modifiedFileListNCF)
        print('Modified NCF count:', len(modifiedFileListNCF))
        print()

        print('Deleted NCF list:', deletedFileListNCF)
        print('Deleted NCF count:', len(deletedFileListNCF))
        print()

        addedFileList = None
        addedFileListNCF = None
        try:
          tmp, addedFileList = getModifiedFiles(srcFolderPath, targetFolderPath)
          tmpNCF, addedFileListNCF = getModifiedFiles(srcFolderPath, targetFolderPath, 'NCF')
        except Exception as ex:
            continue

        print('Added file list:', addedFileList)
        print('Added file list count', len(addedFileList))
        print()

        print('Added NCF list:', addedFileListNCF)
        print('Added NCF list count', len(addedFileListNCF))
        print()

        NCF = getNCFCount(targetFolderPath)
        
        print('Current commiturl:', currentCommitUrl)
        print('NCF=', NCF)
        print()
        
        srcFilesModified, testFilesModified = getFileTypeList(modifiedFileList, True)
        
        print('Src files modified:', srcFilesModified)
        print('Src files modified count:', len(srcFilesModified))
        print()

        print('Test files modified', testFilesModified)
        print('Test files modified count:', len(testFilesModified))
        print()
        
        srcFilesDeleted, testFilesDeleted = getFileTypeList(deletedFileList)
        srcFilesAdded, testFilesAdded = getFileTypeList(addedFileList)
        
        print('Src files added:', srcFilesAdded)
        print('Src files deleted:', srcFilesDeleted)
        print()

        print('Test files added:', testFilesAdded)
        print('Test files deleted:', testFilesDeleted)
        print()
        
        result = formFinalResult(srcFilesModified, testFilesModified,
                                srcFilesAdded, testFilesAdded,
                                srcFilesDeleted, testFilesDeleted)
        
        machine = formFinalMachine(result, NCF, categoryId, sourceCommitLinkFull)
        
        print(machine)
        print()

        repoCommitOutDir = os.path.join(outputDir, clonedFolderName + '_' + targetCommitId)
        createOutputDirectory(repoCommitOutDir, False)

        dumpOutputToJson(result, repoCommitOutDir) 
        dumpOutputToCSV(machine, repoCommitOutDir)

        print('Check output in path=', repoCommitOutDir)    
      except Exception as ex:
          print('Exception caught here3', ex)
          continue
    
    

