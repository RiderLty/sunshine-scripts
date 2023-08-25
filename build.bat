pyinstaller main.py -F -p ./ --name setDisplay -i ./screen-code-line.png --add-data "./static;static"
rd build /s /q
del setDisplay.spec