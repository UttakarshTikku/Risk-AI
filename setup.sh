# Create directories for use

dirs="TestAI_REC Deceptive0AI_REC Deceptive1AI_REC Deceptive2AI_REC Deceptive3AI_REC Deceptive4AI_REC Deceptive5AI_REC Deceptive6AI_REC Deceptive7AI_REC "
mkdir -p $dirs

# Install Dependencies

pip install wheel
pip install curses
pip install networkx
pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
pip install --user scikit-learn

# All Done!

echo RISK Is Ready To Go!!!
