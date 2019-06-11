@echo off
@break off
@title Running Round Robin Tournament of All Deceptive Agents 
@color 0a
@cls


setlocal enabledelayedexpansion 
set ai_agent[0]=Deceptive0AI
set ai_agent[1]=Deceptive1AI
set ai_agent[2]=Deceptive2AI
set ai_agent[3]=Deceptive3AI
set ai_agent[4]=Deceptive4AI
set ai_agent[5]=Deceptive5AI
set ai_agent[6]=Deceptive6AI
set ai_agent[7]=Deceptive7AI

for /l %%a in (0,1,6) do ( 
    for /l %%b in (%%a,1,7) do (
        if NOT %%a == %%b start "" /MIN python pyrisk.py !ai_agent[%%a]!:ALPHA !ai_agent[%%b]!:BRAVO -g 200 --nocurses
    )
)

REM UNWRAPPED LOOP FOR PARALLEL EXECUTION

REM start "" /MIN python pyrisk.py !ai_agent[0]!:ALPHA !ai_agent[1]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[0]!:ALPHA !ai_agent[2]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[0]!:ALPHA !ai_agent[3]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[0]!:ALPHA !ai_agent[4]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[0]!:ALPHA !ai_agent[5]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[0]!:ALPHA !ai_agent[6]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[0]!:ALPHA !ai_agent[7]!:BRAVO -g 200 --nocurses

REM start "" /MIN python pyrisk.py !ai_agent[1]!:ALPHA !ai_agent[2]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[1]!:ALPHA !ai_agent[3]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[1]!:ALPHA !ai_agent[4]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[1]!:ALPHA !ai_agent[5]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[1]!:ALPHA !ai_agent[6]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[1]!:ALPHA !ai_agent[7]!:BRAVO -g 200 --nocurses

REM start "" /MIN python pyrisk.py !ai_agent[2]!:ALPHA !ai_agent[3]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[2]!:ALPHA !ai_agent[4]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[2]!:ALPHA !ai_agent[5]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[2]!:ALPHA !ai_agent[6]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[2]!:ALPHA !ai_agent[7]!:BRAVO -g 200 --nocurses

REM start "" /MIN python pyrisk.py !ai_agent[3]!:ALPHA !ai_agent[4]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[3]!:ALPHA !ai_agent[5]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[3]!:ALPHA !ai_agent[6]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[3]!:ALPHA !ai_agent[7]!:BRAVO -g 200 --nocurses

REM start "" /MIN python pyrisk.py !ai_agent[4]!:ALPHA !ai_agent[5]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[4]!:ALPHA !ai_agent[6]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[4]!:ALPHA !ai_agent[7]!:BRAVO -g 200 --nocurses

REM start "" /MIN python pyrisk.py !ai_agent[5]!:ALPHA !ai_agent[6]!:BRAVO -g 200 --nocurses
REM start "" /MIN python pyrisk.py !ai_agent[5]!:ALPHA !ai_agent[7]!:BRAVO -g 200 --nocurses

REM start "" /MIN python pyrisk.py !ai_agent[6]!:ALPHA !ai_agent[7]!:BRAVO -g 200 --nocurses