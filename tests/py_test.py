import runpy
result = runpy.run_path(path_name='hello.py', init_globals={'output': 'resutl'})
print(type(result))

print(result['val'])

# file = open('hello.py', 'r')
# script = file.read()
# file.close()
# print(script)
# print(type(script))
#
# file = open('hello2.py', 'w')
# file.write(script)
# file.close()

