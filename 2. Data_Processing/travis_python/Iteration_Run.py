from Build import *
from Classifier import *

REPOLIST_FILEPATH = 'repo_list.txt'
GIT_REPO_DIR = 'GitRepos'
BUILD_DIR = 'Builds'
TOKEN = "opQw994o9xzRg7qWxDQdZA"
FETCH_COUNT = 10000
HTTP_PROXIES = None

BASE_URL = "https://travis-ci.org/github/"
JSON_DIR = 'Builds'
RESULT_DIR = 'Results'

if __name__=="__main__":
	buildObj = Build(REPOLIST_FILEPATH, GIT_REPO_DIR, BUILD_DIR, TOKEN, FETCH_COUNT, HTTP_PROXIES)
	git_repos, travis_repos = buildObj.fetchRepoList()
	buildObj.createDir(GIT_REPO_DIR)
	buildObj.downloadRepos(git_repos)
	buildObj.createDir(BUILD_DIR)
	buildObj.fetchBuilds(travis_repos)
	
	buildObj.createDir(RESULT_DIR)
	classifierObj = Classifier(HTTP_PROXIES, BASE_URL, JSON_DIR, RESULT_DIR)
	classifierObj.filterResults()
	
