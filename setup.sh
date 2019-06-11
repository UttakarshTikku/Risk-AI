@ECHO off

# Create directories for use

dirs="TestAI_REC Deceptive0AI_REC Deceptive1AI_REC Deceptive2AI_REC Deceptive3AI_REC Deceptive4AI_REC Deceptive5AI_REC Deceptive6AI_REC Deceptive7AI_REC "
mkdir -p $dirs

# Install Dependencies

pip3 install wheel
pip3 install curses
pip3 install networkx
pip3 install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
pip3 install --user scikit-learn

# All Done!

echo RISK Is Ready To Go!!!
