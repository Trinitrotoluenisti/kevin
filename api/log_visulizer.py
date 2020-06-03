from configs import configs

try:
    with open(configs['LOG']['filename']) as f:
        log = f.readlines()
except FileNotFoundError:
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
