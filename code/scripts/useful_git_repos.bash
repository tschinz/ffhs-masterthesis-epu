#!/bin/bash
#================================================================================
# git_clone.bash - Clone repositories
#
base_directory="$(dirname "$(readlink -f "$0")")"
pushd $base_directory
#base_directory="$base_directory/.."

SEPARATOR='--------------------------------------------------------------------------------'
INDENT='  '

echo "$SEPARATOR"
echo "-- ${0##*/} Started!"
echo ""


#--------------------------------------------------------------------------------
# Parse command line options
#
git_cmd="git clone"
git_opt="--recursive"

#-------------------------------------------------------------------------------
# Clone Private Repos
#
echo "$SEPARATOR\n * Git clone important repositories\n"

echo "  * PYNQ Workshop\n"
$git_cmd $git_opt "https://github.com/Xilinx/PYNQ_Workshop.git"
echo "  * Neural Net Tutorials\n"
$git_cmd $git_opt "https://github.com/stephencwelch/Neural-Networks-Demystified.git"
echo "  * QNN Tutorials\n"
$git_cmd $git_opt "https://github.com/maltanar/qnn-inference-examples.git"


#-------------------------------------------------------------------------------
# Exit
#
echo ""
echo "-- ${0##*/} Finished!"
echo "$SEPARATOR"
popd
