@echo off
set count=10

echo %count%

for /l %%i in (1,1,%count%) do (
    echo Running iteration %%i of %count%
    call python main.py
)