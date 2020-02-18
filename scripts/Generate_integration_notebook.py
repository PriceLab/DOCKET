#!/usr/bin/env python

import sys
import json
import subprocess

Script_dir = "/Users/gloria/Documents/ISB/Translator/project/Script/" 
User_output = "/Users/gloria/Documents/ISB/Translator/project/Output/"


def excute_jupyterNotebook(default_filename) :
	subprocess.call(['cp', Script_dir+'Docket_integration.py', User_output+'Docket_integration.py'])
	jupyter_filename = default_filename
	subprocess.call([
		        'jupyter',
		        'nbconvert',
		        '--inplace',
		        '--to',
		        'notebook',
		        '--execute',
		        jupyter_filename])
	subprocess.call(['jupyter',
					'notebook',
					jupyter_filename
					])

def Print_Warning():
	print("Argument: Generate_integration_notebook.py integration Para1.json Para2.json")
	

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
	if len(sys.argv) < 3:
		Print_Warning_PCA()
	
	else:
		if sys.argv[1] == 'integration':
			para1 = load_json(sys.argv[2])
			para2 = load_json(sys.argv[3])

			if len(sys.argv) == 4:
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
				Print_Warning_PCA()
		else:
			Print_Warning_PCA()

		

if __name__ == "__main__":
	main()


