rmdir build /s /q

set PATH=C:\Py3\Scripts;%PATH%

python setup.py bdist_wheel
python setup.py sdist --formats=gztar

pause