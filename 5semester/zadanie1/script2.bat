@echo off
for /L %%i in (1,1,10) do (
    start cmd /k python main.py
)