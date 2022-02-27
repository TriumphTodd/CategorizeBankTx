@echo off
SET outfile="pylint_output.txt"
IF EXIST %outfile% DEL %outfile%
touch %outfile%
for %%i in (*.py) do pylint %%i >> %outfile%
