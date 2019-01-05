# Python 3.x

# Script for scraping the hypothes.is annotations



import requests
from pprint import pprint
import json
import xlwt
import inflect
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import Algorithmia

html_parser = HTMLParser()

inflect_object = inflect.engine()
workbook = xlwt.Workbook(encoding='ascii', style_compression=2)


worksheet = workbook.add_sheet("PubMedCommonsArchive")
worksheet._cell_overwrite_ok = True
headers_csv = ["Index", "Comment Type", "Research Paper DOI", "Source Url", "Source PMID", "Author", "Date of comment", "Comment"]
for column, heading in enumerate(headers_csv):
    worksheet.write(0, column, heading)

document_name = "PubMedCommonsArchiveWithSentiments.xlsx"


# def fetch_doi(source_url):
# 	doi = ""
# 	try:
# 		req = requests.get(source_url)
# 		soup = BeautifulSoup(req.text, 'lxml')
# 		doi = soup.find_all('div', {'class': 'metaData'})[0].find_all('a')[0].text
# 	except Exception:
# 		pass
# 	return doi


def fetch_doi(pmid):	
	doi = ""
	try:
		response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + pmid)
		for i in json.loads(response.text)['result'][str(pmid)]['articleids']:
			if i['idtype'] == "doi":
				doi = i['value']
				break
	except Exception as e:
		print(e)
		pass
	print(doi, "DOI, ", pmid, "PMID")
	return doi

def process_comment(text):
	processed_comment = {}
	text = text[:text.find('<hr>')].replace('</p>', '').replace('<p>', '').strip().replace('\n', '')
	date_author_details = text[6:text.find('commented:')].strip().split(',')
	date = date_author_details[0]
	author = date_author_details[1]
	comment = html_parser.unescape(text)
	comment = comment[comment.find("</i>")+4:]
	processed_comment['date'] = date
	processed_comment['author'] = author.strip()
	processed_comment['comment'] = comment
	# print(text)
	# print(processed_comment)
	return processed_comment


def get_annotations(params):

	response = requests.get('https://hypothes.is/api/search?', params=params)
	rows = json.loads(response.text)['rows']
	return rows

def store_annotations(annotations, document_name, row):

	# preprocessing the comments
	annotations_details = process_comment(annotations["text"])
	pmid = annotations["tags"][1].split(':')[1].strip()
	doi = fetch_doi(pmid)
	if len(annotations_details['comment']) > 20 and len(doi) > 0:
		try:
			# input = {
			#   "document": annotations_details['comment']
			# }
			# client = Algorithmia.client('simmyzx/Iyeus1pL8pkwIeaVZCw1')
			# algo = client.algo('nlp/SentimentAnalysis/1.0.5')
			source_url = "https://europepmc.org/abstract/MED/"+ pmid
			worksheet.write(row, 0, row)  # index
			# sentiment_score = algo.pipe(input).result[0]['sentiment']
			# print(sentiment_score)
			# worksheet.write(row, 1, sentiment_score) # sentiment
			worksheet.write(row, 2, doi)  # DOI
			# worksheet.write(row, 1, row) # Comment Type
			worksheet.write(row, 3, source_url)  # source url
			worksheet.write(row, 4, annotations["tags"][1])  # source pmid
			worksheet.write(row, 5, annotations_details['author'])
			worksheet.write(row, 6, annotations_details['date'])
			worksheet.write(row, 7, annotations_details['comment'])
			return 1
		except Exception as e:
			print(e)
			return 0
	else:
		return 0
row = 1
params = {'limit': 40,
          'tag': 'PubMedCommonsArchive',
          'sort': 'updated'}
rows = get_annotations(params)

while len(rows) > 0:
	for each_annotations in rows:
		# pprint(each_annotations['updated'])
		success = store_annotations(each_annotations, document_name, row)
		print(row, " Processed")
		if success == 1:
			row += 1
	search_after = rows[-1]['updated']
	params['search_after'] = search_after
	rows = get_annotations(params)
	break
workbook.save(document_name)