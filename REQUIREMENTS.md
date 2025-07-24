# Claude Code Runner Requirements

## Overview
Automate the process of opening Claude Code in new terminals for each subfolder in a given directory, using specific instruction files.

## Functional Requirements

### Core Features
1. **Directory Scanning**
   - Scan a given base directory for all subdirectories
   - Process each subdirectory independently
   - Skip hidden directories (starting with .)

2. **Terminal Management**
   - Open a new terminal window/tab for each subdirectory
   - Support both Linux (WSL) and macOS terminals
   - Change to the target directory before running Claude Code

3. **Claude Code Automation**
   - Detect if Claude Code can resume a session
   - Handle both resume and new session scenarios
   - Programmatically interact with Claude Code prompts

4. **File Integration**
   - Use coderun.md for main instructions
   - Use coderun_init.md for initialization instructions
   - Insert file contents at appropriate prompts

### Technical Requirements

1. **Platform Support**
   - Linux (WSL) support using Windows Terminal or default terminal
   - macOS support using Terminal.app or iTerm2
   - Platform detection and appropriate terminal selection

2. **Error Handling**
   - Handle missing directories gracefully
   - Handle missing instruction files
   - Log errors for debugging
   - Continue processing other folders on failure

3. **Configuration**
   - Configurable base directory
   - Configurable terminal preferences
   - Configurable Claude Code command options

## Non-Functional Requirements

1. **Performance**
   - Minimal delay between terminal launches
   - Efficient directory scanning

2. **Usability**
   - Clear console output showing progress
   - Simple command-line interface
   - Helpful error messages

3. **Reliability**
   - Robust error handling
   - Graceful degradation on partial failures
   - Logging for troubleshooting

## Implementation Details

1. **Languages**
   - Python for main script (cross-platform compatibility)
   - Shell scripts for terminal automation

2. **Dependencies**
   - Python 3.8+
   - Platform-specific terminal emulators
   - Claude Code CLI tool

3. **File Structure**
   - Main Python script for orchestration
   - Platform-specific shell scripts
   - Configuration files
   - Instruction template files