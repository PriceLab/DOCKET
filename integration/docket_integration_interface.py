#!/usr/bin/env python
import os
import sys
import json
import subprocess
Curr_dir = os.getcwd()
Script_dir = Curr_dir+"/notebooks/" 


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
	print("Argument: docket_integration_interface.py.py input_dir output_dir label parameter_file")
	

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
	if len(sys.argv) < 5:
		Print_Warning()
	
	else:
		if sys.argv[1] == 'mut_drugResponse':
			directories = {"input_dir": sys.argv[2],"output_dir":sys.argv[3]}
			User_output = sys.argv[3]

			if os.path.isdir(User_output) == False:
				os.mkdir(User_output)

			para1 = load_json(sys.argv[4])
			para2 = load_json(sys.argv[5])
			print(para2)
			if len(sys.argv) == 6:
				with open(Script_dir + "Integration_temp_GDSC_mut_drug_response.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_GDSC_mut_drug_response.ipynb"
				
				directory_content = []
				directory_content.append('directories = {')
				for item in reformat_json(directories):
					directory_content.append(item)
				directory_content.append('}')
				content['cells'][3]['source'] = directory_content

				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][5]['source'] = new_content

				new_content = []
				new_content.append('input_data2 = {')
				for item in reformat_json(para2):
					new_content.append(item)
				new_content.append('}')

				content['cells'][6]['source'] = new_content

				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

				print("Finished! Please check the output file in " + default_filename)
		elif sys.argv[1] == 'mut_expr':
			directories = {"input_dir": sys.argv[2], "output_dir":sys.argv[3]}
			User_output = sys.argv[3]

			if os.path.isdir(User_output) == False:
				os.mkdir(User_output)

			para1 = load_json(sys.argv[4])
			para2 = load_json(sys.argv[5])
			print(para2)
			if len(sys.argv) == 6:
				with open(Script_dir + "Integration_temp_GDSC_mut_expression.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_GDSC_mut_expression.ipynb"
				
				directory_content = []
				directory_content.append('directories = {')
				for item in reformat_json(directories):
					directory_content.append(item)
				directory_content.append('}')
				content['cells'][3]['source'] = directory_content


				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][5]['source'] = new_content

				new_content = []
				new_content.append('input_data2 = {')
				for item in reformat_json(para2):
					new_content.append(item)
				new_content.append('}')

				content['cells'][6]['source'] = new_content

				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

				print("Finished! Please check the output file in " + default_filename)
				
		elif sys.argv[1] == 'annotation':
			directories = {"input_dir": sys.argv[2],"output_dir":sys.argv[3]}
			User_output = sys.argv[3]

			if os.path.isdir(User_output) == False:
				os.mkdir(User_output)

			para1 = load_json(sys.argv[4])
			para2 = load_json(sys.argv[5])
			print(para1)
			print(para2)
			if len(sys.argv) == 6:
				with open(Script_dir + "Integration_temp_GDSC_annotation_associations.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_GDSC_annotation_associations.ipynb"

				directory_content = []
				directory_content.append('directories = {')
				for item in reformat_json(directories):
					directory_content.append(item)
				directory_content.append('}')
				content['cells'][3]['source'] = directory_content

				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][5]['source'] = new_content

				new_content = []
				new_content.append('input_data2 = {')
				for item in reformat_json(para2):
					new_content.append(item)
				new_content.append('}')

				content['cells'][6]['source'] = new_content

				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

				print("Finished! Please check the output file in " + default_filename)

		elif sys.argv[1] == 'visualization':
			directories = {"input_dir": sys.argv[2], "output_dir":sys.argv[3]}
			User_output = sys.argv[3]

			if os.path.isdir(User_output) == False:
				os.mkdir(User_output)

			para1 = load_json(sys.argv[4])
			print(para1)
			if len(sys.argv) == 5:
				with open(Script_dir + "Integration_temp_Visualization.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_Visualization.ipynb"
				directory_content = []
				directory_content.append('directories = {')
				for item in reformat_json(directories):
					directory_content.append(item)
				directory_content.append('}')
				content['cells'][3]['source'] = directory_content

				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')

				content['cells'][5]['source'] = new_content


				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)

		elif sys.argv[1] == 'comp':
			print(len(sys.argv))
			
			directories = {"input_dir": sys.argv[2],"output_dir":sys.argv[3]}
			User_output = sys.argv[3]

			if os.path.isdir(User_output) == False:
				os.mkdir(User_output)


			para1 = load_json(sys.argv[4])

			#print(directories)
			#print(para1)
			if len(sys.argv) == 5:
				with open(Script_dir + "Integration_temp_similarity_compare.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"Integration_temp_similarity_compare.ipynb"

				directory_content = []
				directory_content.append('directories = {')
				for item in reformat_json(directories):
					directory_content.append(item)
				directory_content.append('}')
				content['cells'][3]['source'] = directory_content

				new_content = []
				new_content.append('input_data = {')
				for item in reformat_json(para1):
					new_content.append(item)
				new_content.append('}')


				content['cells'][5]['source'] = new_content



				jupyter_content = content
				with open(default_filename, 'w') as fp:
					json.dump(content, fp, indent=2)
				excute_jupyterNotebook(default_filename)
		else:
			Print_Warning()

		

if __name__ == "__main__":
	main()


