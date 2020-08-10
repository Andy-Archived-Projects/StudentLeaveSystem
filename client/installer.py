# -*- coding: utf-8 -*-
import os

os.system('@echo off')
os.system('rd /s /q client')
os.system('pyinstaller -F client.py')
os.system('xcopy /e /y /q /i lang dist\lang')
os.system('rd /s /q build')
os.system('rd /s /q __pycache__')
os.system('del client.spec')
os.rename('dist', 'client')
with open('client\\Start.bat', 'w') as f:
    f.write('@echo off\necho ====启动中 请稍后====\nclient.exe\npause')
