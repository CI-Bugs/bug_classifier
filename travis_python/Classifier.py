import os
import requests
import bs4
from bs4 import BeautifulSoup
import json
import re
from git import Repo

class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   NEWLINE = '\n'


class Classifier:
	def __init__(self, http_proxies, base_url, json_dir, result_dir):
		self.http_proxies = http_proxies
		self.base_url = base_url
		self.json_dir = json_dir
		self.travis_jsons = list(filter(lambda x: x.endswith('.json'), os.listdir(self.json_dir)))
		self.result_dir = result_dir
		
	def printResults(self, count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits, filteredBy):
		to_print = ""
		to_print += Color.GREEN
		to_print += Color.BOLD
		to_print += str(count)+"."	
		to_print += Color.END
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tDate:\t\t\t" 		
		to_print += Color.END

		to_print += str(build['commit']['committed_at']) + Color.NEWLINE

		to_print += Color.BOLD + Color.BLUE
		to_print +=	"\tCurrent_State:\t\t"
		to_print += Color.END

		to_print +=	build['state'] + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tCurr_Message:\t\t"
		to_print += Color.END

		to_print += message + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tCurr_git_commit:\t" 
		to_print += Color.END

		to_print += curr_sha + Color.NEWLINE

		to_print += Color.BOLD + Color.BLUE
		to_print += "\tCurr_git_url:\t\t"
		to_print += Color.END

		to_print += curr_git_url + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tCurr_travis_url:\t"
		to_print += Color.END

		to_print += curr_travis_url + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tPrevious_State:\t\t"
		to_print += Color.END

		to_print += build['previous_state'] + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tPrev_Message:\t\t"
		to_print += Color.END

		to_print += prev_message + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tPrev_git_commit:\t"
		to_print += Color.END

		to_print += prev_sha + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tPrev_git_url:\t\t"
		to_print += Color.END
	
		to_print += prev_git_url + Color.NEWLINE
	
		to_print += Color.BOLD + Color.BLUE
		to_print += "\tPrev_travis_url: "
		to_print += Color.END
	
		to_print += "" + Color.NEWLINE

		to_print += Color.BOLD + Color.BLUE
		to_print += "\tCompare_url:\t\t"
		to_print += Color.END

		to_print += compare_url + Color.NEWLINE

		to_print += Color.BOLD + Color.BLUE
		if betweenCommits:
			to_print += "\tChanged Files b/w commits:\t\t"
		else:
			to_print += "\tChanged Files since last commit:\t\t"
		to_print += Color.END
		
		to_print += str(changedFiles) + Color.NEWLINE

		to_print += Color.BOLD + Color.BLUE
		to_print += "\tFiltered_by:\t\t"
		to_print += Color.END

		to_print += filteredBy
	
		print(to_print)
		print("\n")

		return

	def containsTestFolder(self, filename):
		filenameSplit = (filename.lower()).split('/')
		if 'test' in filenameSplit:
			return True
		return False

	def containsSrcFile(self, filename):
		extensionName = (filename.lower()).split('.')[-1]
		if 'java' in extensionName:
			return True
		return False

	def containsConfigFile(self, filename):
		extensionName = (filename.lower()).split('.')[-1]
		if 'xml' in extensionName or 'yml' in extensionName:
			return True
		return False

	def formJson(self, count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits):
		to_ret = {}
		metadata = {}
		metadata['Date']			=	build['commit']['committed_at']
		metadata['Current_State'] 	= 	build['state']
		metadata['Curr_Message']	=	message
		metadata['Curr_git_commit']	=	curr_sha
		metadata['Curr_git_url']	=	curr_git_url
		metadata['Curr_travis_url']	=	curr_travis_url
		metadata['Previous_State']	=	build['previous_state']
		metadata['Prev_Message']	=	prev_message
		metadata['prev_message']	=	prev_sha
		metadata['Prev_git_url']	=	prev_git_url
		metadata['Prev_travis_url']	=	''
		metadata['Compare_url']		=	compare_url
		if betweenCommits:
			metadata['Changed_Files_b/w_commits']	=	changedFiles
		else:
			metadata['Changed_Files_since_last_commit']	=	changedFiles

		to_ret[count]	=	metadata
	
		return to_ret
	
	def createFinalJson(self, summary_json, results_json):
		final_json = {'Summary': summary_json, 'Categories': results_json}	
		return final_json	

	def createJsonFilename(self, build):
		json_filename = ((build['repository']['slug']).replace('/', '_'))+'_results.json'
		json_filepath = os.path.join(self.result_dir, json_filename)
		return json_filepath

	def createSummaryJson(self, test_count, src_count, config_count, mixed_count, summary_json):
		total_count = test_count + src_count + config_count + mixed_count
		if total_count == 0:
			total_count = 1
		summary_json['test only']['count'] = test_count
		summary_json['test only']['percent'] = test_count/total_count*100

		summary_json['src only']['count'] = src_count
		summary_json['src only']['percent'] = round(src_count/total_count*100, 2)

		summary_json['config only']['count'] = config_count
		summary_json['config only']['percent'] = round(config_count/total_count*100, 2)

		summary_json['mixed']['count'] = mixed_count
		summary_json['mixed']['percent'] = round(mixed_count/total_count*100, 0)

		return summary_json

	def dumpResults(self, json_filepath, final_json):
		if not os.path.isdir(self.result_dir):
			os.makedirs(self.result_dir)

		with open(json_filepath, 'w') as outfile:
			json.dump(final_json, outfile)

	def modifiedFiles(self, a, b):
		changed_files = []
		for x in a.diff(b):
			if x.a_blob is not None and x.a_blob.path not in changed_files:
				changed_files.append(x.a_blob.path)
				
			if x.b_blob is not None and x.b_blob.path not in changed_files:
				changed_files.append(x.b_blob.path)
		
		return changed_files



	def filterResults(self):
		for json_file in self.travis_jsons:
			betweenCommits = False
			v = []
			f = open(self.json_dir + os.sep + json_file, 'r')
			content = f.read()
			res = json.loads(content)
			count = 0;
			cloned_repo_path = res['local_path']
			results_json = {'test only': {}, 'src only': {}, 'config only': {}, 'mixed': {}}
			summary_json = {'test only': {}, 'src only': {}, 'config only': {}, 'mixed': {}}
			test_count = 0
			src_count = 0
			config_count = 0
			mixed_count = 0
			build = []
			for i, build in enumerate(res['builds']):
				message = build['commit']['message']
				if build['state'] == 'passed' and build['previous_state'] == 'failed':
					curr_sha = build['commit']['sha']
					compare_url = build['commit']['compare_url']
					prev_sha = 'not found'
					if '...' in compare_url:
						prev_sha = (compare_url.split('...')[0]).split('/')[-1]

					to_cont = True
					a = None
					repo = Repo(cloned_repo_path)
					try:
						a = repo.commit(curr_sha)
					except:
						to_cont = False

					to_cont_prev = True
					b = None
					prev_repo = Repo(cloned_repo_path)
					try:
						b = prev_repo.commit(prev_sha)
					except:
						to_cont_prev = False
					
					prev_message = 'not found'						
					if to_cont_prev == True:
						prev_message = b.message			
					
					
					curr_travis_url = self.base_url+build['repository']['slug']+build['@href']
					curr_travis_url = curr_travis_url.replace('build', 'builds')

					prev_travis_build = 'not found'
					prev_travis_url = 'not found'
					
					if curr_sha == 'not found':
						curr_git_url = 'not found'
					else:
						curr_git_url =  repo.remotes[0].config_reader.get("url") + '/commits/' + curr_sha
					
					if prev_sha == 'not found':
						prev_git_url = 'not found'
					else:
						prev_git_url =  repo.remotes[0].config_reader.get("url") + '/commits/' + prev_sha
					
					if to_cont == False:
						continue
					
					if(prev_git_url == 'not found'):
						filelist = a.stats.files.keys()
					else:
						betweenCommits = True
						filelist = self.modifiedFiles(a, b)
					changedFiles = []
					testFilesCount = 0
					srcFilesCount = 0
					configFilesCount = 0
					totalFilesCount = len(filelist)
					for filename in filelist:
						changedFiles.append(filename)
						if self.containsTestFolder(filename):
							testFilesCount += 1
						elif self.containsSrcFile(filename):
							srcFilesCount += 1
						elif self.containsConfigFile(filename):
							configFilesCount += 1
					
					if testFilesCount == totalFilesCount:
						count += 1
						test_count += 1
						self.printResults(count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits, 'test only')
						test_json = self.formJson(test_count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits)
						results_json['test only'].update(test_json)
					elif srcFilesCount == totalFilesCount:
						count += 1
						src_count += 1
						self.printResults(count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits, 'src only')
						src_json = self.formJson(src_count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits)
						results_json['src only'].update(src_json)
					elif configFilesCount == totalFilesCount:
						count += 1
						config_count += 1
						self.printResults(count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits, 'config only')
						config_json = self.formJson(config_count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits)
						results_json['config only'].update(config_json)
					else:
						count += 1
						mixed_count += 1
						self.printResults(count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits, 'mixed')
						mixed_json = self.formJson(mixed_count, build, curr_git_url, prev_git_url, curr_travis_url, compare_url, message, prev_message, curr_sha, prev_sha, changedFiles, betweenCommits)
						results_json['mixed'].update(mixed_json)

			if not build:
				continue
			summary_json = self.createSummaryJson(test_count, src_count, config_count, mixed_count, summary_json)
			final_json = self.createFinalJson(summary_json, results_json)
			json_filepath = self.createJsonFilename(build)

			self.dumpResults(json_filepath, final_json)
			print('Output written to:', json_filepath)
			print('\n\n/***************************************************************************************************/\n\n')
