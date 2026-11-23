@echo off
set ROOT=%~dp0..

echo ^> run.bat examples\spec_tests.yaml result.bin --test
call "%ROOT%\run.bat" "%ROOT%\examples\spec_tests.yaml" result.bin --test
echo код завершения: %ERRORLEVEL%
echo.

echo ^> run.bat examples\commented.yaml result.bin --test
call "%ROOT%\run.bat" "%ROOT%\examples\commented.yaml" result.bin --test
echo код завершения: %ERRORLEVEL%
echo.

echo ^> run.bat examples\invalid_range.yaml result.bin --test
call "%ROOT%\run.bat" "%ROOT%\examples\invalid_range.yaml" result.bin --test
echo код завершения: %ERRORLEVEL%
