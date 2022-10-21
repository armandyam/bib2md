from pybtex.database import parse_file
import jinja2
from jinja2 import meta
import collections

def setup_jinja(templatefile):
	templateLoader = jinja2.FileSystemLoader(searchpath="./")
	templateEnv = jinja2.Environment(loader=templateLoader)
	template = templateEnv.get_template(templatefile)
	template_source = templateEnv.loader.get_source(templateEnv, templatefile)
	parsed_content = templateEnv.parse(template_source)
	undelared_variables = meta.find_undeclared_variables(parsed_content)
	return template, undelared_variables

def parse_bib_file(bibdata):
	bibdata_parsed = collections.defaultdict(lambda: collections.defaultdict(dict))
	bib_data = parse_file(bibdata)
	for entry in bib_data.entries:
		for field in bib_data.entries[entry].fields:
			bibdata_parsed[entry][field.lower().replace('-', '_')] = bib_data.entries[entry].fields[field]
		author_list = []
		for person in bib_data.entries[entry].persons:
			authors = bib_data.entries[entry].persons[person]
			for author in authors:
				author_first_name = ' '.join(author.first_names)
				author_last_name = ' '.join(author.last_names)
				author_list.append(author_first_name + ' ' + author_last_name)
		bibdata_parsed[entry]['authors_list'] = ', '.join(author_list)
		bibdata_parsed[entry]['paper_file_name'] = bibdata_parsed[entry]['year']+'-'+bibdata_parsed[entry]['title'].replace(' ', '-')+'.md'
		bibdata_parsed[entry]['date'] = bibdata_parsed[entry]['year']

	return bibdata_parsed

def write_md(bibdata, template, undelared_variables):
	for entry in bibdata:
		template_data = {}
		temp_undeclared_variables = undelared_variables.copy()
		for value in undelared_variables:
			if value in bibdata[entry].keys():
				template_data[value] = bibdata[entry][value]
				temp_undeclared_variables.remove(value)
		if len(temp_undeclared_variables) > 0:
			print('The following variables are not defined in the bib file: ', temp_undeclared_variables)
		outputText = template.render(template_data)  # this is where to put args to the template renderer
		with open(bibdata[entry]['paper_file_name'], "w") as text_file:
			text_file.write(outputText)

def bib2md(bibfile, templatefile):
	bibdata = parse_bib_file(bibfile)
	template, undelared_variables = setup_jinja(templatefile)
	write_md(bibdata, template, undelared_variables)
def main():
	bib2md('aerospace-v08-i11_20221020.bib', 'md_template.jinja2')
#
if __name__ == '__main__':
    	main()
# to_declare = meta.find_undeclared_variables(parsed_content)
#
# bib_data = parse_file('aerospace-v08-i11_20221020.bib')
# for entry in bib_data.entries:
# 	title = bib_data.entries[entry].fields['title']
# 	# print(type(bib_data.entries[entry].fields.keys()))
# 	template_data = {}
# 	for value in to_declare:
# 		if value in bib_data.entries[entry].fields.keys():
# 			# print(value, bib_data.entries[entry].fields[value])
# 			template_data[value] = bib_data.entries[entry].fields[value]
# 			# print({value, bib_data.entries[entry].fields[value]})
# 	print(bib_data.entries[entry].persons)
# 	# template_data = {"title": title}
# 	# print(template_data)
# 	outputText = template.render(template_data)  # this is where to put args to the template renderer
# 	with open("trial.md", "w") as text_file:
# 		text_file.write(outputText)
# # print(bib_data.entries['Knuth:TB8-1-14'].fields['title'])
# # for author in bib_data.entries['Knuth:TB8-1-14'].persons['author']:
# 	# print(unicode(author))