@echo off
call :lastarg %*

IF exist "%LAST_ARG%" (
	docker run -it --rm -v "%LAST_ARG%":"/workspace" ifrim/insurance-db:0.1.1 insurance-db %ALL_BUT_LAST% /workspace
) ELSE (
	docker run -it --rm ifrim/insurance-db:0.1.1 insurance-db "%*"
)

:lastarg
  set "LAST_ARG=%~1"
  shift
  if not "%~1"=="" set "ALL_BUT_LAST=%ALL_BUT_LAST% %LAST_ARG%"
  if not "%~1"=="" goto lastarg
goto :eof

