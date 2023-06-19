isPass = True
for i in output.split('\n'):
    if "NOK" in i:
        isPass = False