import sys
import os
import json

path = r'C:\Users\vkabadi\OneDrive - The University of Melbourne\Vinay\PHD\GIT\bug_classifier\Bugs_Discovery\logs'
#fileName  = 'code.json'
#fileName  = 'test.json'
fileName  = 'build.json'

full_path = path+"\\"+fileName

diff_urls = []

with open(full_path, encoding='utf-8') as fh:
    data = json.load(fh)

for item in data:
    diff_urls.append(item['diff_url'])

fullLinks = []
commitLinks = []

for line in diff_urls:
    line.strip()
    line = line.replace("\n", "")

    baseLine = line.split("/")
    commits = baseLine[-1].split("..")

    commit_link = line.split("compare")

    l1 = commit_link[0]+'commit/'+commits[0]
    l2 = commit_link[0]+'commit/'+commits[1]
    l3 = line

    l0 = l1 + ',' + l2 + ',' + l3 + '\n'
    fullLinks.append(l0)
    commitLinks.append(l1+"\n")

fileNameNoExt = fileName.split(".")[0]

fullLinks =  set(fullLinks) #remove duplicates
f = open(path+"/"+fileNameNoExt+"_full_links.txt", "w")
f.writelines(fullLinks)
f.close()

commitLinks =  set(commitLinks) #remove duplicates
f = open(path+"/"+fileNameNoExt+"_commit_links.txt", "w")
f.writelines(commitLinks)
f.close()