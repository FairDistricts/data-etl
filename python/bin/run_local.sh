#!/bin/bash
#------------------------------------------------------------------------
#  run_local.sh - locally starts a classifier instance
#------------------------------------------------------------------------

# infer the project location
MODEL_DIR=$(dirname $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) )
echo "Local run directory '$MODEL_DIR'..., function '$1'"
if [ $# -eq 0 ]; then
    echo "Invalid arugments, please provide a function (parse, server)"
    echo "  ex. ./bin/run_local.sh parse -i data/2017-06-02-tx-csv "
    echo "  ex. ./bin/run_local.sh server "
fi

# inject into python path and run with existing args (for unix-like environments)
SCRIPT=$1
shift 1
PYTHONPATH="$MODEL_DIR:$PYTHONPATH" python $MODEL_DIR/bin/run_fair_data_$SCRIPT.py $*
