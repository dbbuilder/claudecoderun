# TODO List for Claude Code Runner

## Stage 1: Core Implementation (Priority: High)

### Section 1.1: Project Setup
- [x] Create project directory structure
- [x] Create REQUIREMENTS.md
- [x] Create README.md
- [ ] Create requirements.txt for Python dependencies
- [ ] Create sample instruction files (coderun.md, coderun_init.md)

### Section 1.2: Platform Detection
- [ ] Implement OS detection (Linux/WSL vs macOS)
- [ ] Detect available terminal emulators
- [ ] Create terminal launcher abstraction

### Section 1.3: Directory Processing
- [ ] Implement directory scanning function
- [ ] Add directory filtering (exclude hidden, etc.)
- [ ] Create directory queue for processing

## Stage 2: Claude Code Integration (Priority: High)

### Section 2.1: Session Management
- [ ] Implement session detection logic
- [ ] Create resume session handler
- [ ] Create new session handler
- [ ] Implement prompt detection and response

### Section 2.2: File Insertion
- [ ] Read instruction files
- [ ] Implement keyboard input simulation
- [ ] Handle file insertion timing

## Stage 3: Terminal Automation (Priority: Medium)

### Section 3.1: Linux/WSL Support
- [ ] Create Windows Terminal launcher
- [ ] Create fallback cmd.exe launcher
- [ ] Implement WSL path conversion

### Section 3.2: macOS Support
- [ ] Create Terminal.app launcher
- [ ] Create iTerm2 launcher (optional)
- [ ] Implement AppleScript automation

## Stage 4: Error Handling & Logging (Priority: Medium)

### Section 4.1: Error Handling
- [ ] Add try-catch blocks for all operations
- [ ] Implement graceful failure modes
- [ ] Create error recovery mechanisms

### Section 4.2: Logging
- [ ] Set up Python logging framework
- [ ] Add debug logging throughout
- [ ] Create log file rotation

## Stage 5: User Interface (Priority: Low)

### Section 5.1: CLI Arguments
- [ ] Implement argparse for command-line options
- [ ] Add configuration file support
- [ ] Create help documentation

### Section 5.2: Progress Feedback
- [ ] Add progress bar for directory processing
- [ ] Show current directory being processed
- [ ] Display summary statistics

## Stage 6: Testing & Documentation (Priority: Low)

### Section 6.1: Testing
- [ ] Create unit tests for core functions
- [ ] Add integration tests
- [ ] Test on both platforms

### Section 6.2: Documentation
- [ ] Update README with examples
- [ ] Create troubleshooting guide
- [ ] Add configuration examples

## Current Focus
Start with Stage 1 to establish the foundation, then move to Stage 2 for core Claude Code integration.

## Notes
- Prioritize cross-platform compatibility
- Ensure robust error handling from the start
- Keep terminal automation modular for easy extension