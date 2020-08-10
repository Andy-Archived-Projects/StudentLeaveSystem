# -*- coding: utf-8 -*-
import os
bat_content = '''@echo off
echo =======启动中请稍后 Starting up Please wait=======
client.exe
echo Press Enter to exit
set /p a=
'''
folder_name = 'LeaveSystemClient'

os.system('@echo off')
os.system(f'rd /s /q {folder_name}')
os.system('pyinstaller -F client.py')
os.system('xcopy /e /y /q /i lang dist\lang')
os.system('rd /s /q build')
os.system('rd /s /q __pycache__')
os.system('del client.spec')
os.rename('dist', folder_name)
with open(f'{folder_name}\\Start.bat', 'w') as f:
    f.write(bat_content)
