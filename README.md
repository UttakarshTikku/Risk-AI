________________________________________________________________________
DECEPTIVE AI IN RISK
________________________________________________________________________

INTRODUCTION
________________________________________________________________________
This project uses a RISK implementation in Python to study the possibility
of deceptive artificial intelligence in Stochastic, Turn-Based games.

The AI agents implemented for this purpose are:
Intent Recognition Based, Non-Deceptive Agent: ai/test.py
Intent Recognition Based, Deceptive Agent: ai/deceptive.py

The supporting files like

    configuration.py
    intent_engine.py
    previous_turn_checker.py
    decision_engine.py

are also used as helpers of the deceptive agents.


TO RUN THE GAME (Windows)
________________________________________________________________________
The prerequisite is Python version >= 3.5
First, run setup.bat
setup.bat will install the dependencies and setup the requisite folder structure. 
Then the game is runnable.

Note: If running on a non-windows machine, check running on docker.

COMMAND LINE ARGS
________________________________________________________________________
--nocurses, default=True, description=Disable the ncurses map display

--nocolor, default=True, description=Display the map without colors

-l, default=False, description=Write game events to a logfile

-d, default=0.1, description=Delay in seconds after each action is displayed

-s, default=None, description=Random number generator seed

-g, default=1, description=Number of rounds to play

-w, default=False, description=Pause and wait for a keypress after each action

players, description=Names of the AI classes to use. May use 'ExampleAI*3' syntax

--deal", default=False, description="Deal territories rather than letting players choose

-gs, default=False, description=Grid Search For Intent Classifier

-rec, default=False, description=Turn Recording CSV Data On Or Off


TESTING AND TRAINING FILES
________________________________________________________________________
The training and testing files are:

    training_AI_agents.bat

    round_robin_tournament.bat

RUNNING ON DOCKER
________________________________________________________________________
`docker run -ti -v /path/to/code/:/RISK/ --entrypoint /bin/sh ubuntu:18.04`

Then follow the below steps:

INSTALL PYTHON


1. apt-get update
2. apt-get install libssl-dev openssl
3. wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
4. tar xzvf Python-3.5.0.tgz
5. cd Python-3.5.0
6. ./configure
7. make
8. make install

NOTE: 
* All tests were run on a Windows machine
* If wget is not available, install using `apt install wget`
* If make is not found on docker, run the command `apt-get install --reinstall make`
* If while running `./configure`, no acceptable C compiler is found in ${path}, run `apt-get install build-essentials` 


INSTALL RISK

Run setup.sh