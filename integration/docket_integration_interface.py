#!/usr/bin/env python
import os
import sys
import json
import subprocess
Curr_dir = os.getcwd()
Script_dir = Curr_dir+"/notebooks/" 
User_output = sys.argv[1]

if os.path.isdir(User_output) == False:
	os.mkdir(User_output)

def excute_jupyterNotebook(default_filename) :
	#subprocess.call(['cp', Script_dir+'Docket_integration.py', User_output+'Docket_integration.py'])
	jupyter_filename = default_filename
	subprocess.call([
		        'jupyter',
		        'nbconvert',
				'--ExecutePreprocessor.timeout=600',
		        '--inplace',
		        '--to',
		        'html',
		        '--execute',
		        jupyter_filename])
	#subprocess.call(['jupyter',
	#				'notebook',
	#				'--no-browser',
	#				jupyter_filename
	#				])

def Print_Warning():
	print("Argument: docket_integration_interface.py.py integration_GDSC_mut_drugResponse Para1.json Para2.json")
	

def load_json(Para_file):
	import json
	with open(Para_file) as f:
		data = json.load(f)
		#print(data)
	return(data)

def reformat_json(json):
	new_content  = []
	for i in json:
		if isinstance(json[i], str):
			new_content.append('"'+i + '"' + ':' + '"'+ json[i]+ '",' + '\n')
		if isinstance(json[i], list):
			temp = '"'+i + '"' + ': [' 
			for item in json[i]:
				temp = temp + '"' +item + '"' +','
			temp = temp + '],\n'
			new_content.append(temp)

	return(new_content)

def main():
	print(sys.argv)
	if len(sys.argv) < 3:
		Print_Warning()
	
	else:
		if sys.argv[2] == 'integration':
			para1 = load_json(sys.argv[3])
			para2 = load_json(sys.argv[4])

			if len(sys.argv) == 5:
				with open(Script_dir + "Integration_template.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_template.ipynb"

				new_content = []
				new_content.append('input_data1 = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][3]['source'] = new_content

				new_content = []
				new_content.append('input_data2 = {')
				for item in reformat_json(para2):
					new_content.append(item)
				new_content.append('}')

				content['cells'][4]['source'] = new_content
				

				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)


				excute_jupyterNotebook(default_filename)

				print("Finished! Please check the output file in " + default_filename)
			else:
				Print_Warning()

		elif sys.argv[2] == 'mut_drugResponse':
			para1 = load_json(sys.argv[3])
			para2 = load_json(sys.argv[4])
			print(para2)
			if len(sys.argv) == 5:
				with open(Script_dir + "Integration_temp_GDSC_mut_drug_response.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_GDSC_mut_drug_response.ipynb"
				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][1]['source'] = new_content

				new_content = []
				new_content.append('input_data2 = {')
				for item in reformat_json(para2):
					new_content.append(item)
				new_content.append('}')

				content['cells'][2]['source'] = new_content

				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

				print("Finished! Please check the output file in " + default_filename)
		elif sys.argv[2] == 'mut_expr':
			para1 = load_json(sys.argv[3])
			para2 = load_json(sys.argv[4])
			print(para2)
			if len(sys.argv) == 5:
				with open(Script_dir + "Integration_temp_GDSC_mut_expression.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_GDSC_mut_expression.ipynb"
				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][1]['source'] = new_content

				new_content = []
				new_content.append('input_data2 = {')
				for item in reformat_json(para2):
					new_content.append(item)
				new_content.append('}')

				content['cells'][2]['source'] = new_content

				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

				print("Finished! Please check the output file in " + default_filename)
				
		elif sys.argv[2] == 'annotation':
			para1 = load_json(sys.argv[3])
			para2 = load_json(sys.argv[4])
			print(para1)
			print(para2)
			if len(sys.argv) == 5:
				with open(Script_dir + "Integration_temp_GDSC_annotation_associations.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_GDSC_annotation_associations.ipynb"
				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][1]['source'] = new_content

				new_content = []
				new_content.append('input_data2 = {')
				for item in reformat_json(para2):
					new_content.append(item)
				new_content.append('}')

				content['cells'][2]['source'] = new_content

				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

				print("Finished! Please check the output file in " + default_filename)

		elif sys.argv[2] == 'visualization':
			para1 = load_json(sys.argv[3])
			print(para1)
			if len(sys.argv) == 4:
				with open(Script_dir + "Integration_temp_Visualization.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_Visualization.ipynb"
				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][1]['source'] = new_content


				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

		elif sys.argv[2] == 'comp':
			para1 = load_json(sys.argv[3])
			print(para1)
			if len(sys.argv) == 4:
				with open(Script_dir + "Integration_temp_similarity_compare.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_similarity_compare.ipynb"
				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][3]['source'] = new_content


				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)
		else:
			Print_Warning()

		

if __name__ == "__main__":
	main()


