@echo off
set ROOT=%~dp0..
set BIN=%TEMP%\uvm_program.bin
set DUMP=%TEMP%\uvm_dump.xml

echo ^> run.bat examples\copy_array.yaml program.bin
call "%ROOT%\run.bat" "%ROOT%\examples\copy_array.yaml" "%BIN%"
echo.
echo ^> run_interpreter.bat program.bin dump.xml --range 10 24
call "%ROOT%\run_interpreter.bat" "%BIN%" "%DUMP%" --range 10 24
echo.
echo ^> type dump.xml
type "%DUMP%"
if exist "%BIN%" del "%BIN%"
if exist "%DUMP%" del "%DUMP%"
