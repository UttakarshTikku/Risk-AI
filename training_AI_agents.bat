@echo off

REM PREPARING NON DECEPTIVE AGENT FOR INTENT CLASSIFICATION GRID SEARCH

start "" /MIN python pyrisk.py TestAI:ALPHA BetterAI:BRAVO -g 200 -rec=True

REM TRAINING STRATEGY : RANDOM

start "" /MIN python pyrisk.py Deceptive0AI:ALPHA BetterAI:BRAVO -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive1AI:ALPHA BetterAI:BRAVO -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive2AI:ALPHA BetterAI:BRAVO -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive3AI:ALPHA BetterAI:BRAVO -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive4AI:ALPHA BetterAI:BRAVO -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive5AI:ALPHA BetterAI:BRAVO -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive6AI:ALPHA BetterAI:BRAVO -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive7AI:ALPHA BetterAI:BRAVO -g 200 -rec=True

REM TRAINING STRATEGY : RANDOM

start "" /MIN python pyrisk.py Deceptive0AI:BRAVO BetterAI:ALPHA -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive1AI:BRAVO BetterAI:ALPHA -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive2AI:BRAVO BetterAI:ALPHA -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive3AI:BRAVO BetterAI:ALPHA -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive4AI:BRAVO BetterAI:ALPHA -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive5AI:BRAVO BetterAI:ALPHA -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive6AI:BRAVO BetterAI:ALPHA -g 200 -rec=True
start "" /MIN python pyrisk.py Deceptive7AI:BRAVO BetterAI:ALPHA -g 200 -rec=True