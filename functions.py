def changeI(d):
    return int(d.replace('-','').replace('T','').replace('+09:00','').replace(':','').replace('Z',''))