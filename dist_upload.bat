set PATH=C:\Py3\Scripts;%PATH%

twine upload --skip-existing dist\*.whl dist\*.tar.gz
pause