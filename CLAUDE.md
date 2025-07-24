# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Claude Code Runner - a CLI automation tool designed to automate opening Claude Code CLI in multiple terminal windows for subdirectories. The tool supports session management, stage-based development workflows, and cross-platform execution.

## Key Commands

### Running the Application

```bash
# Basic usage - open Claude Code for each subdirectory
./run.sh /path/to/directory

# Stage-based execution
./run_stage.sh /path/to/directory --stage scaffolding_mvp

# List available stages
./run_stage.sh --list-stages

# Dry run to preview actions
./run.sh /path/to/directory --dry-run

# Direct Python execution (if wrapper scripts fail)
python3 claudecoderun.py /path/to/directory
python3 claudecoderun_enhanced.py /path/to/directory  # Enhanced version
python3 claudecoderun_stage.py /path/to/directory --stage planning_design_gitsetup
```

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Required packages: pexpect>=4.8.0, pyautogui>=0.9.54, psutil>=5.9.0, colorama>=0.4.6, tqdm>=4.65.0
```

## High-Level Architecture

### Core Components

1. **Three Progressive Versions**:
   - `claudecoderun.py` - Basic terminal automation
   - `claudecoderun_enhanced.py` - Enhanced with pexpect support (preferred)
   - `claudecoderun_stage.py` - Stage-aware with development workflow support

2. **Platform Abstraction Layer**:
   - `TerminalLauncher` class handles platform-specific terminal commands
   - Automatic detection of WSL, macOS, and Linux environments
   - Graceful fallback when enhanced features unavailable

3. **Instruction File System**:
   - `coderun.md` - Main instructions sent after session start/resume
   - `coderun_init.md` - Initialization instructions for new sessions
   - Stage-specific files: `coderun_init_<stage>.md`, `coderun_continue_<stage>.md`

### Key Design Patterns

- **Strategy Pattern**: Platform-specific terminal launching strategies
- **Template Method**: Automation script generation with customizable steps
- **Factory Pattern**: ClaudeAutomation class creates platform-appropriate scripts
- **Progressive Enhancement**: Basic functionality with optional advanced features

### Development Stages

The tool supports 14 distinct development stages:
- **Required**: planning_design_gitsetup, scaffolding_mvp, database_design, code_debug, addchange_check, deploy_test, document, upgrade
- **Optional**: opt_api_design, opt_integration_test, opt_performance_baseline, opt_security_audit, opt_monitoring_observability, opt_release_management

### Critical Implementation Details

1. **Session Management**:
   - Attempts to resume existing Claude Code sessions before creating new ones
   - Uses pexpect for reliable automation when available
   - Falls back to basic terminal interaction if needed

2. **Instruction File Search Path**:
   - Current project directory
   - Parent directory
   - Base directory
   - Script directory
   - Hardcoded stage directories

3. **Parallel Processing**:
   - Thread-based execution with configurable workers
   - Work queue pattern for task distribution
   - `--max-parallel` option to control concurrency

### Important Notes

- No test suite exists - consider adding tests when making significant changes
- The tool uses `--dangerously-skip-permissions` flag with Claude Code CLI
- Logs are created in the current working directory
- The enhanced version requires pexpect which may not work on all platforms
- Stage progression requires review documents as quality gates