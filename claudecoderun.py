#!/usr/bin/env python3
"""
Claude Code Runner - Main Script
Automates opening Claude Code in new terminals for each subdirectory
"""

import os
import sys
import time
import platform
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Tuple
import json
import signal

# Add colorama for cross-platform colored output
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        GREEN = RED = YELLOW = BLUE = RESET = ''
    class Style:
        BRIGHT = RESET_ALL = ''

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claudecoderun.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClaudeCodeRunner:
    """Main class for automating Claude Code terminals"""
    
    def __init__(self, base_dir: str, coderun_file: str = "coderun.md", 
                 init_file: str = "coderun_init.md", delay: int = 2,
                 wsl_distro: str = "Ubuntu"):
        """
        Initialize the ClaudeCodeRunner
        
        Args:
            base_dir: Base directory to scan for subdirectories
            coderun_file: Main instruction file
            init_file: Initialization instruction file
            delay: Delay between launching terminals
            wsl_distro: WSL distribution name (default: Ubuntu)
        """
        self.base_dir = Path(base_dir).resolve()
        self.coderun_file = coderun_file
        self.init_file = init_file
        self.delay = delay
        self.wsl_distro = wsl_distro
        self.platform = self._detect_platform()
        self.terminal_cmd = self._get_terminal_command()
        
        logger.info(f"Initialized ClaudeCodeRunner for {self.platform} platform")
        logger.info(f"Base directory: {self.base_dir}")
    
    def _detect_platform(self) -> str:
        """Detect the current platform"""
        system = platform.system().lower()
        if system == "linux" and "microsoft" in platform.uname().release.lower():
            return "wsl"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            return "linux"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
    
    def _get_terminal_command(self) -> List[str]:
        """Get the appropriate terminal command for the platform"""
        if self.platform == "wsl":
            # Check for Windows Terminal first
            try:
                subprocess.run(["wt.exe", "--version"], capture_output=True, check=True)
                return ["wt.exe", "-d"]
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to cmd.exe
                return ["cmd.exe", "/c", "start", "cmd.exe", "/k", "wsl", "-d", self.wsl_distro, "--cd"]
        
        elif self.platform == "macos":
            # Use osascript to open Terminal.app
            return ["osascript", "-e"]
        
        elif self.platform == "linux":
            # Try common terminal emulators
            terminals = ["gnome-terminal", "konsole", "xterm", "terminator"]
            for term in terminals:
                try:
                    subprocess.run([term, "--version"], capture_output=True, check=True)
                    if term == "gnome-terminal":
                        return [term, "--working-directory"]
                    else:
                        return [term, "--workdir"]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            raise RuntimeError("No supported terminal emulator found")
    
    def get_subdirectories(self, exclude: Optional[List[str]] = None) -> List[Path]:
        """
        Get all subdirectories in the base directory
        
        Args:
            exclude: List of directory names to exclude
            
        Returns:
            List of subdirectory paths
        """
        exclude = exclude or []
        subdirs = []
        
        try:
            for item in self.base_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    if item.name not in exclude:
                        subdirs.append(item)
                        logger.info(f"Found directory: {item.name}")
        except Exception as e:
            logger.error(f"Error scanning directories: {e}")
            raise
        
        return sorted(subdirs)
    
    def create_automation_script(self, directory: Path) -> Path:
        """
        Create a temporary automation script for the directory
        
        Args:
            directory: Target directory
            
        Returns:
            Path to the created script
        """
        script_name = f"claude_automation_{directory.name}.sh"
        script_path = directory / script_name        
        # Read instruction files
        coderun_content = self._read_instruction_file(self.coderun_file)
        init_content = self._read_instruction_file(self.init_file)
        
        # Create the automation script
        script_content = f"""#!/bin/bash
# Claude Code Automation Script for {directory.name}
# Generated by ClaudeCodeRunner

set -e  # Exit on error

echo "Starting Claude Code automation for {directory.name}"
cd "{directory}"

# Detect platform
PLATFORM=$(uname -s)

# Function to set clipboard content
set_clipboard() {{
    if [[ "$PLATFORM" == "Darwin" ]]; then
        echo "$1" | pbcopy
    else
        # Try xclip first, then xsel
        if command -v xclip >/dev/null 2>&1; then
            echo "$1" | xclip -selection clipboard
        elif command -v xsel >/dev/null 2>&1; then
            echo "$1" | xsel --clipboard --input
        else
            echo "Warning: No clipboard tool found. Please install xclip or xsel on Linux."
        fi
    fi
}}

# Function to send keystrokes (platform-specific)
send_keystrokes() {{
    if [[ "$PLATFORM" == "Darwin" ]]; then
        # macOS: Use osascript for automation
        osascript -e 'tell application "System Events" to keystroke "v" using command down'
        sleep 0.5
        osascript -e 'tell application "System Events" to key code 36' # Return key
    else
        # Linux: Check if xdotool is available
        if command -v xdotool >/dev/null 2>&1; then
            xdotool key --window $(xdotool search --pid $1 | head -1) ctrl+v 2>/dev/null || true
            sleep 0.5
            xdotool key --window $(xdotool search --pid $1 | head -1) Return 2>/dev/null || true
        else
            echo "Warning: xdotool not found. Automation features limited on Linux."
            echo "Please install xdotool for full automation support."
        fi
    fi
}}

# Function to type text (platform-specific)
type_text() {{
    if [[ "$PLATFORM" == "Darwin" ]]; then
        osascript -e "tell application \\"System Events\\" to keystroke \\"$1\\""
    else
        if command -v xdotool >/dev/null 2>&1; then
            xdotool type --window $(xdotool search --pid $2 | head -1) "$1" 2>/dev/null || true
        fi
    fi
}}

# Try to resume session
echo "Attempting to resume Claude Code session..."
if claude --resume --dangerously-skip-permissions 2>&1 | grep -q "Select a session"; then
    echo "Session found, resuming..."
    # Send Enter to select the most recent session
    echo "" | claude --resume --dangerously-skip-permissions &
    CLAUDE_PID=$!
    sleep 2
    
    # Insert coderun.md content
    set_clipboard '{coderun_content}'
    send_keystrokes $CLAUDE_PID
else
    echo "No session to resume, starting new session..."
    # Start new session
    claude --dangerously-skip-permissions &
    CLAUDE_PID=$!
    sleep 3
    
    # Wait for main prompt and send /init
    echo "Sending /init command..."
    type_text "/init" $CLAUDE_PID
    sleep 0.5
    if [[ "$PLATFORM" == "Darwin" ]]; then
        osascript -e 'tell application "System Events" to key code 36' # Return key
    else
        xdotool key --window $(xdotool search --pid $CLAUDE_PID | head -1) Return 2>/dev/null || true
    fi
    sleep 2
    
    # Insert coderun_init.md content
    set_clipboard '{init_content}'
    send_keystrokes $CLAUDE_PID
    sleep 2
    
    # Insert coderun.md content
    set_clipboard '{coderun_content}'
    send_keystrokes $CLAUDE_PID
fi

echo "Claude Code automation completed for {directory.name}"
echo ""
echo "Note: If automation didn't work properly, you can manually:"
echo "1. Run 'claude --resume --dangerously-skip-permissions' or 'claude --dangerously-skip-permissions'"
echo "2. For new sessions, type '/init' and paste the instruction files"
echo ""

# Keep terminal open
exec bash
"""
        
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            logger.info(f"Created automation script: {script_path}")
            
        except Exception as e:
            logger.error(f"Error creating automation script: {e}")
            raise
        
        return script_path
    
    def _read_instruction_file(self, filename: str) -> str:
        """Read and return the content of an instruction file"""
        try:
            file_path = self.base_dir.parent / filename
            if not file_path.exists():
                # Try current directory
                file_path = Path(filename)
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read().replace('\n', '\\n').replace('"', '\\"')
                    return content
            else:
                logger.warning(f"Instruction file not found: {filename}")
                return f"# {filename} not found"
                
        except Exception as e:
            logger.error(f"Error reading instruction file {filename}: {e}")
            return f"# Error reading {filename}"
    
    def launch_terminal(self, directory: Path) -> bool:
        """
        Launch a terminal for the given directory
        
        Args:
            directory: Target directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.platform == "wsl":
                # Convert WSL path to Windows path
                win_path = subprocess.check_output(
                    ["wslpath", "-w", str(directory)], 
                    text=True
                ).strip()
                
                if self.terminal_cmd[0] == "wt.exe":
                    # Windows Terminal
                    cmd = [self.terminal_cmd[0], "-d", win_path, "wsl", "-d", self.wsl_distro, 
                           f"cd '{directory}' && bash"]
                else:
                    # CMD fallback
                    cmd = self.terminal_cmd + [str(directory)]                
            elif self.platform == "macos":
                # macOS Terminal.app via AppleScript
                script = f'''tell app "Terminal" to do script "cd '{directory}' && bash"'''
                cmd = self.terminal_cmd + [script]
                
            else:  # linux
                cmd = self.terminal_cmd + [str(directory)]
            
            logger.info(f"Launching terminal with command: {' '.join(map(str, cmd))}")
            subprocess.Popen(cmd)
            return True
            
        except Exception as e:
            logger.error(f"Error launching terminal for {directory}: {e}")
            return False
    
    def run(self, exclude: Optional[List[str]] = None, dry_run: bool = False):
        """
        Main execution method
        
        Args:
            exclude: List of directory names to exclude
            dry_run: If True, only show what would be done
        """
        print(f"{Fore.GREEN}Claude Code Runner Starting...{Style.RESET_ALL}")
        print(f"Base directory: {self.base_dir}")
        print(f"Platform: {self.platform}")
        
        # Get subdirectories
        subdirs = self.get_subdirectories(exclude)
        
        if not subdirs:
            print(f"{Fore.YELLOW}No subdirectories found in {self.base_dir}{Style.RESET_ALL}")
            return
        
        print(f"\nFound {len(subdirs)} directories to process:")
        for subdir in subdirs:
            print(f"  - {subdir.name}")
        
        if dry_run:
            print(f"\n{Fore.YELLOW}Dry run mode - no terminals will be launched{Style.RESET_ALL}")
            return
        
        # Process each directory
        successful = 0
        failed = 0
        
        for i, subdir in enumerate(subdirs, 1):
            print(f"\n{Fore.BLUE}[{i}/{len(subdirs)}] Processing: {subdir.name}{Style.RESET_ALL}")
            
            try:
                # Create automation script
                script_path = self.create_automation_script(subdir)
                
                # Launch terminal
                if self.launch_terminal(subdir):
                    successful += 1
                    print(f"{Fore.GREEN}✓ Terminal launched for {subdir.name}{Style.RESET_ALL}")
                else:
                    failed += 1
                    print(f"{Fore.RED}✗ Failed to launch terminal for {subdir.name}{Style.RESET_ALL}")
                
                # Delay between launches
                if i < len(subdirs):
                    print(f"Waiting {self.delay} seconds before next launch...")
                    time.sleep(self.delay)
                    
            except Exception as e:
                failed += 1
                logger.error(f"Error processing {subdir.name}: {e}")
                print(f"{Fore.RED}✗ Error processing {subdir.name}: {e}{Style.RESET_ALL}")
        
        # Summary
        print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Completed!{Style.RESET_ALL}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(subdirs)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automate opening Claude Code in terminals for each subdirectory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/projects
  %(prog)s /path/to/projects --exclude node_modules,build
  %(prog)s /path/to/projects --coderun custom.md --init custom_init.md
  %(prog)s /path/to/projects --dry-run
        """
    )
    
    parser.add_argument(
        "base_dir",
        help="Base directory containing subdirectories to process"
    )
    
    parser.add_argument(
        "--coderun",
        default="coderun.md",
        help="Main instruction file (default: coderun.md)"
    )
    
    parser.add_argument(
        "--init",
        default="coderun_init.md",
        help="Initialization instruction file (default: coderun_init.md)"
    )
    
    parser.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Delay in seconds between launching terminals (default: 2)"
    )
    
    parser.add_argument(
        "--wsl-distro",
        default="Ubuntu",
        help="WSL distribution name (default: Ubuntu)"
    )
    
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directories to exclude"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually launching terminals"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse exclude list
    exclude = args.exclude.split(',') if args.exclude else []
    
    # Validate base directory
    base_dir = Path(args.base_dir)
    if not base_dir.exists():
        print(f"{Fore.RED}Error: Base directory does not exist: {base_dir}{Style.RESET_ALL}")
        sys.exit(1)
    
    if not base_dir.is_dir():
        print(f"{Fore.RED}Error: Path is not a directory: {base_dir}{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        # Create and run the automation
        runner = ClaudeCodeRunner(
            base_dir=str(base_dir),
            coderun_file=args.coderun,
            init_file=args.init,
            delay=args.delay,
            wsl_distro=args.wsl_distro
        )
        
        runner.run(exclude=exclude, dry_run=args.dry_run)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()