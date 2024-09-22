@echo off
set count=30

echo %count%

for /l %%i in (1,1,%count%) do (
    echo Running iteration %%i of %count%
    call main.exe
)