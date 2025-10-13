#!/bin/bash
# Helper script to activate the Python 3.12 environment for layout automation

echo "Activating Python 3.12 environment (layout_py312)..."
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate layout_py312

echo ""
echo "✓ Environment activated!"
echo ""
echo "Python version: $(python --version)"
echo "Environment: $CONDA_DEFAULT_ENV"
echo ""
echo "You can now run your layout automation scripts:"
echo "  python your_script.py"
echo ""
echo "To deactivate, run: conda deactivate"
