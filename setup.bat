@echo off
@break off
@title Setup Risk Environment
@color 0a
@cls

setlocal EnableDelayedExpansion

if not exist ".\TestAI_REC\" (
    mkdir ".\TestAI_REC\"
    if "!errorlevel!" EQU "0" (
        echo Folder created successfully
    ) else (
        echo Error while creating folder
    )
    ) else (
    echo Folder already exists
)
for /l %%A in (0,1,7) do (

    if not exist ".\Deceptive"%%A"AI_REC\" (
    mkdir ".\Deceptive"%%A"AI_REC\"
    if "!errorlevel!" EQU "0" (
        echo Folder created successfully
    ) else (
        echo Error while creating folder
    )
    ) else (
    echo Folder already exists
    )
)

pip install wheel
pip install curses
pip install networkx
pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
pip install --user scikit-learn

echo RISK Is Ready To Go!!!
pause