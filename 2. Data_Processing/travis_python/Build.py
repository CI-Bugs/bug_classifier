import os
import sys
import requests
import json
import subprocess
import git
from git import Repo
import shutil

class Build:
	def __init__(self, repolist_filepath, git_repo_dir, build_dir, token, fetch_count, http_proxies):
		self.repolist_filepath = repolist_filepath
		self.git_repo_dir = git_repo_dir
		self.build_dir = build_dir
		self.token = token
		self.fetch_count = fetch_count
		self.http_proxies = http_proxies

	def checkIfRepoNameExist(self, repo_name):
		if os.path.isdir(repo_name):
			return True
		return False

	def fetchRepoList(self):
		with open(self.repolist_filepath) as f:
			content = f.readlines()
		git_repos = [x.strip() for x in content] 
		travis_repos = ['/'.join(x.strip().split("/")[-2:]) for x in content]

		return git_repos, travis_repos

	def createDir(self, directory):
		if os.path.isdir(directory):
			shutil.rmtree(directory)
			print('STATUS:', directory, 'removed')
	
		os.makedirs(directory)
		print('STATUS:', directory, 'created')
		
	def cloneGitRepo(self, repo_url, repo_name):
		repo_name_path = os.path.join(self.git_repo_dir, repo_name)
		print('STATUS:','cloning...', repo_url, 'inside', self.git_repo_dir, 'as', repo_name)
		git.Git(self.git_repo_dir).clone(repo_url)

	def downloadRepos(self, repos_url):
		for repo_url in repos_url:
			repo_name = repo_url.split("/")[-1]
			self.cloneGitRepo(repo_url, repo_name)
	

	def fetchBuilds(self, repos):
		for repo in repos:
			b = []
			off = 0
			remain = self.fetch_count
			while remain > 0:
				headers = { 'Travis-API-Version': '3', 'Authorization' : 'token ' + self.token }
				c = min(remain, 100)
				res = requests.get('https://api.travis-ci.org/repo/{}/builds?offset={}&limit={}'.format(repo.replace('/', '%2F'), off, c), headers=headers, proxies=self.http_proxies)
				content = res.content
				try:
					builds = json.loads(content)['builds']
				except:
					print('STATUS: Some error, skipping', repo)
					break
				b.extend(builds)
				off += c
				print('STATUS:', off, 'builds retrieved from', repo)
				remain -= c
		
			repo_name = repo.rsplit("/")[1].split(".")[0]
			cloned_repo_path = os.path.join(self.git_repo_dir, repo_name)
			json_str = json.dumps({'builds': b, 'local_path': cloned_repo_path})
			json_filename = repo.replace('/', '_') + '.json'
			json_filepath = os.path.join(self.build_dir, json_filename)
			print('STATUS:', 'Saving', json_filepath)
			f = open(json_filepath,  'w')
			f.write(json_str)
			f.close()

