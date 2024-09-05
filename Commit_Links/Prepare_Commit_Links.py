import json



# Opening JSON file
with open(r'C:\PHD\Classifier\Bugswarm_Git_Commit_Links\build_test.json', encoding='utf-8') as fh:
    data = json.load(fh)

commit_urls = []

index = 0
for item in data:
    index = index + 1
    diff_url = item['diff_url']
    repo, commits = diff_url.split("compare")
    base_commit = commits.split("..")[0]
    tgt_commit = commits.split("..")[1]    
    base_url = repo+"commit"+base_commit
    tgt_url = repo+"commit"+tgt_commit   

    #commit_url = base_url + ',' + tgt_url + ',' + diff_url
    commit_urls.append(base_url)


commit_urls = list(set(commit_urls))
f = open(r"C:\PHD\Classifier\Bugswarm_Git_Commit_Links\build_test.txt", "w+")   
for url in commit_urls:
    f.writelines(url+'\n') 
f.close()