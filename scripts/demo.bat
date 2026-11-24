@echo off
set ROOT=%~dp0..
set OUT=%TEMP%\uvm_result.bin

call :show spec_tests.yaml
call :show commented.yaml
call :show invalid_range.yaml
if exist "%OUT%" del "%OUT%"
goto :eof

:show
echo ^> run.bat examples\%1 result.bin --test
call "%ROOT%\run.bat" "%ROOT%\examples\%1" "%OUT%" --test
echo код завершения: %ERRORLEVEL%
echo.
goto :eof
