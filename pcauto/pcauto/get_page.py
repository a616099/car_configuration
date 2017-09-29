import re,requests

def get_pages(resonse_text):
	total = int(re.search('var\s+total\s*=\s*[\'\"]?(\d+)[\'\"]?;\s*',resonse_text).group(1)) 
	pageSize = int(re.search('var\s+pageSize\s*=\s*[\'\"]?(\d+)[\'\"]?;\s*',resonse_text).group(1)) 
	pageNoEnd = 10 
	i = 0 if total % pageSize ==0 else 1 
	pagenum = int(total/pageSize + i)
	return pagenum