import os
treeErrorUrls = []
urlList = []
accessibleFileName = 'Accessible_Code.txt'
inAccessibleFileName = 'Inaccessible_Code.txt'
urlFileName = 'Code_commit_links.txt'
nohupFileName = 'code_nohup.out'
firsttime = True

os.system('rm -rf ' + accessibleFileName)
os.system('rm -rf ' + inAccessibleFileName)

with open(urlFileName, 'r') as fileObj:
    for line in fileObj.readlines():
        urlList.append(line.strip())

with open(nohupFileName, 'r') as fileObj:
    for line in fileObj.readlines():
        line = line.strip()
        if 'not a tree' in line:
            commitId = line.split()[-1]
            for url in urlList:
                if commitId in url:
                    inAccessibleCommand = 'echo ' + url + ' >> ' + inAccessibleFileName
                    os.system(inAccessibleCommand)
                else:
                    accessibleCommand = 'echo ' + url + ' >> ' + accessibleFileName
                    os.system(accessibleCommand)


