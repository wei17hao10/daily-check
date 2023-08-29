import os
import json

dirs = os.listdir('./Checks')
for folder in ['Powershell', 'Python']:
	if folder in dirs:
		files = os.listdir(f'Checks/{folder}')
		for file in files:
			filepath = f'./Checks/{folder}/{file}'
			print(filepath)
			if os.path.exists(filepath) and filepath[-5:] == '.json':
				with open(filepath, encoding='utf8') as f:
					checkitem = json.load(f)
					
				check = checkitem["CheckContent"]
				print(len(check))
				check.append('0')
				checkitem["CheckContent"] = check
				print(f'check1={checkitem["CheckContent"][1]}, check2={checkitem["CheckContent"][2]}')
				
				with open(filepath, 'w+', encoding='utf8') as f:
					json.dump(checkitem, f, indent=4)

for folder in ['SQL']:
	if folder in dirs:
		files = os.listdir(f'Checks/{folder}')
		for file in files:
			filepath = f'./Checks/{folder}/{file}'
			print(filepath)
			if os.path.exists(filepath) and filepath[-5:] == '.json':
				with open(filepath, encoding='utf8') as f:
					checkitem = json.load(f)
					
				check = checkitem["CheckContent"]
				print(len(check))
				check.append('0')
				check[2] = check[1]
				check[1] = '0'
				checkitem["CheckContent"] = check
				print(f'check1={checkitem["CheckContent"][1]}, check2={checkitem["CheckContent"][2]}')
				
				with open(filepath, 'w+', encoding='utf8') as f:
					json.dump(checkitem, f, indent=4)