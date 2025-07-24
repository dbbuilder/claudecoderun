# Claude Code Runner

Automates opening Claude Code in new terminals for each subdirectory in a given directory.

## Overview

This tool scans a base directory and opens Claude Code in a new terminal for each subdirectory found. It handles both resuming existing sessions and creating new ones, automatically inserting instruction files at the appropriate prompts.

## Prerequisites

- Python 3.8 or higher
- Claude Code CLI installed and accessible in PATH
- Linux (WSL) or macOS
- Terminal emulator (Windows Terminal for WSL, Terminal.app or iTerm2 for macOS)

### Platform-Specific Requirements

#### Linux
- **Clipboard support**: Install `xclip` or `xsel`
  ```bash
  # Ubuntu/Debian
  sudo apt-get install xclip
  
  # Fedora
  sudo dnf install xclip
  
  # Arch
  sudo pacman -S xclip
  ```
- **Window automation** (optional for basic script): Install `xdotool`
  ```bash
  # Ubuntu/Debian
  sudo apt-get install xdotool
  
  # Fedora
  sudo dnf install xdotool
  
  # Arch
  sudo pacman -S xdotool
  ```
  Note: The enhanced version with pexpect provides better automation without xdotool

#### macOS
- No additional tools required (uses built-in `pbcopy` and `osascript`)

#### Windows (WSL)
- Windows Subsystem for Linux (WSL) with a Linux distribution installed
- Windows Terminal recommended (fallback to CMD if not available)
- Ensure `wslpath` is available (included by default in WSL)

## Installation

1. Clone or download this project to `D:\dev2\claudecoderun\` (or your preferred location)

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create your instruction files:
   - `coderun.md` - Main instructions for Claude Code
   - `coderun_init.md` - Initialization instructions for new sessions

## Usage

### Basic Usage

```bash
python claudecoderun.py /path/to/base/directory
```

### With Custom Instruction Files

```bash
python claudecoderun.py /path/to/base/directory --coderun custom_instructions.md --init custom_init.md
```

### Configuration Options

- `--terminal` - Specify terminal emulator (auto-detected by default)
- `--delay` - Delay between launching terminals (default: 2 seconds)
- `--exclude` - Comma-separated list of directories to exclude
- `--dry-run` - Show what would be executed without running
- `--wsl-distro` - WSL distribution name (default: Ubuntu)
- `--verbose` - Enable verbose logging

### Enhanced Version Options

The enhanced version (`claudecoderun_enhanced.py`) provides additional features:
- `--parallel` - Launch terminals in parallel
- `--max-parallel` - Maximum number of parallel launches (default: 3)

### Stage Version Options

The stage version (`claudecoderun_stage.py`) adds development workflow support:
- `--stage` - Specify development stage (e.g., planning_design_gitsetup, scaffolding_mvp)
- `--stage-dirs` - Custom directories to search for stage files (comma-separated)
- `--list-stages` - List all available development stages

## How It Works

1. **Directory Scanning**: The script scans the specified base directory for all subdirectories
2. **Terminal Launch**: For each subdirectory, a new terminal window is opened
3. **Session Detection**: The script attempts to resume an existing Claude Code session
4. **Instruction Insertion**: Depending on whether it's a new or resumed session, the appropriate instruction files are inserted

### Session Resume Logic

If `claude --resume` has available sessions:
- Selects the most recent session (top one)
- Inserts contents of `coderun.md`

If no sessions are available:
- Runs `claude --dangerously-skip-permissions`
- Accepts prompts until main prompt
- Enters `/init` command
- Inserts contents of `coderun_init.md`
- Inserts contents of `coderun.md`

## Platform-Specific Notes

### Windows (WSL)
- Uses Windows Terminal by default
- Falls back to cmd.exe with WSL if Windows Terminal not available

### macOS
- Uses Terminal.app by default
- Can be configured to use iTerm2

## Troubleshooting

1. **Claude Code not found**: Ensure Claude Code is installed and in your PATH
2. **Terminal not opening**: Check terminal emulator is installed and accessible
3. **Instructions not inserting**: Verify instruction files exist and are readable
4. **Sessions not resuming**: Check Claude Code permissions and session state

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is provided as-is for personal and educational use.