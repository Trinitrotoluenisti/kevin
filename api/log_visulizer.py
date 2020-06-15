from configs import configs
from time import sleep


while True:
    # Load configs
    try:
        with open(configs['LOG']['filename']) as f:
            log = f.readlines()
    except FileNotFoundError:
        log = []

    # Color lines!
    for line in log[-20:]:
        # White Debugs
        if line[20] == 'D':
            print(line[:-1])

        # Blue Infos
        elif line[20] == 'I':
            print('\033[34m' + line[:-1] + '\033[0m')

        # Green Warnings
        elif line[20] == 'W':
            print('\033[32m' + line[:-1] + '\033[0m')

        # Yellow Errors
        elif line[20] == 'E':
            print('\033[33m' + line[:-1] + '\033[0m')

    # Sleep 0.2 seconds
    sleep(0.2)
