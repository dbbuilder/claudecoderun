#!/bin/bash
# Claude Code Runner with Stage Support - Bash wrapper

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if we're in WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "Detected WSL environment"
fi

# Check for --list-stages flag
if [[ "$*" == *"--list-stages"* ]]; then
    python3 "$SCRIPT_DIR/claudecoderun_stage.py" --list-stages
    exit 0
fi

# Use the stage-aware version if --stage is provided
if [[ "$*" == *"--stage"* ]]; then
    echo "Using stage-aware version"
    SCRIPT="claudecoderun_stage.py"
elif python3 -c "import pexpect" 2>/dev/null; then
    echo "Using enhanced version with pexpect support"
    SCRIPT="claudecoderun_enhanced.py"
else
    echo "Using basic version (install pexpect for better automation)"
    SCRIPT="claudecoderun.py"
fi

# Pass all arguments to the Python script
python3 "$SCRIPT_DIR/$SCRIPT" "$@"