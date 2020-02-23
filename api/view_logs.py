# A stupid log visualizer.
# Created to be used with the watch command.

try:
	with open('api.log') as f:
		log = f.readlines()
except:
	log = []


for line in log[-20:]:
	if line[20] == 'D':
		print(line[:-1])
	elif line[20] == 'I':
		print('\033[34m' + line[:-1] + '\033[0m')
	elif line[20] == 'W':
		print('\033[32m' + line[:-1] + '\033[0m')
	elif line[20] == 'E':
		print('\033[33m' + line[:-1] + '\033[0m')
