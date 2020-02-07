#!/usr/bin/env python

import sys
import json
import subprocess


Script_dir = "./" 
subprocess.call(['mkdir', 'Output'])
User_output = "./Output/"

def excute_jupyterNotebook(default_filename) :
	subprocess.call(['cp', Script_dir+'Docket_OverView.py', User_output+'Docket_OverView.py'])
	jupyter_filename = default_filename
	subprocess.call([
		        'jupyter',
		        'nbconvert',
		        '--to',
		        'notebook',
		        '--execute',
		        jupyter_filename])
	subprocess.call(['jupyter',
					'notebook',
					jupyter_filename
					])

def Print_Warning_PCA():
	print("Argument: Generate_jupyterNotebook.py PCA_Visual PCA_File PC_sele_1 PC_sele_2")
	print("PCA_Visual: Label for PCA visualization jupyter notebook"  )
	print("PCA_File: The PCA data file"  )
	print("PC_sele_1: The first Principle component you choose to plot"  )
	print("PC_sele_2: The first Principle component you choose to plot"  )

def main():
	if len(sys.argv) == 1:
		Print_Warning_PCA()
		
	if len(sys.argv) > 1:
		if sys.argv[1] == 'PCA_Visual':
			if len(sys.argv) == 5:
				with open(Script_dir + "PCA_plot_template.ipynb") as fp:
			   		content = json.load(fp)

				default_filename = User_output+"PCA_plot.ipynb"

				content['cells'][3]['source']
				new_content = []
				new_content.append("PCA_File = " + '"'+ str(sys.argv[2])+ '"' + "\n")
				new_content.append("PC_sele_1 = " + '"' + str(sys.argv[3]) + '"' + "\n")
				new_content.append("PC_sele_2 = " + '"' + str(sys.argv[4]) + '"' + "\n")

				content['cells'][3]['source'] = new_content



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


