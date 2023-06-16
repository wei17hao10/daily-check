import runpy

input_param = {}
output = """
Output:
OK baidu.com
OK taobao.com
NOK jd.com

Errors:
None
"""
input_param['output'] = output
result = runpy.run_path(path_name='hello.py', init_globals=input_param)
print(result['isPass'])


import os
source_dir = 'C:\\Users\\WEIHAO\\PycharmProjects\\daily-check\\UI'
filter_str = '.ui'
output = ''
files = os.listdir(source_dir)
files = [f for f in files if filter_str in f]
for f in files:
    size = os.path.getsize(os.path.join(source_dir, f))
    if size < 5 * 1024:
        output = output + '\n' + f'small file: {f}'

print(output)
