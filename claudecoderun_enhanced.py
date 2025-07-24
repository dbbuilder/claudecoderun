#!/usr/bin/env python3
"""
Claude Code Runner - Enhanced Version with pexpect
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
from typing import List, Optional, Dict, Any
import json
import threading
import queue

# Platform-specific imports
try:
    if platform.system().lower() != "windows":
        import pexpect
    else:
        pexpect = None
except ImportError:
    pexpect = None
    logging.warning("pexpect not available - using fallback method")

# Add colorama for cross-platform colored output
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        GREEN = RED = YELLOW = BLUE = CYAN = MAGENTA = RESET = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''

# Configure logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler('claudecoderun_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TerminalLauncher:
    """Platform-specific terminal launcher"""
    
    def __init__(self, platform_name: str, wsl_distro: str = "Ubuntu"):
        self.platform = platform_name
        self.wsl_distro = wsl_distro
        self.terminal_cmds = self._get_terminal_commands()
        self._check_required_tools()
    
    def _get_terminal_commands(self) -> Dict[str, Any]:
        """Get terminal commands for each platform"""
        commands = {
            "wsl": {
                "wt": ["wt.exe", "-d", "{path}", "wsl", "-d", self.wsl_distro, "--cd", "{wsl_path}", "--", "bash", "-c", "{script}"],
                "cmd": ["cmd.exe", "/c", "start", "cmd.exe", "/k", "wsl", "-d", self.wsl_distro, "--cd", "{wsl_path}", "--", "bash", "{script}"]
            },
            "macos": {
                "terminal": {
                    "type": "applescript",
                    "script": '''
                    tell application "Terminal"
                        do script "cd '{path}' && bash '{script}'"
                        activate
                    end tell
                    '''
                },
                "iterm": {
                    "type": "applescript",
                    "script": '''
                    tell application "iTerm"
                        create window with default profile
                        tell current session of current window
                            write text "cd '{path}' && bash '{script}'"
                        end tell
                    end tell
                    '''
                }
            },
            "linux": {
                "gnome-terminal": ["gnome-terminal", "--working-directory={path}", "--", "bash", "{script}"],
                "konsole": ["konsole", "--workdir", "{path}", "-e", "bash", "{script}"],
                "xterm": ["xterm", "-e", "cd '{path}' && bash '{script}'"],
                "terminator": ["terminator", "--working-directory={path}", "-e", "bash '{script}'"]
            }
        }
        return commands.get(self.platform, {})
    
    def launch(self, directory: Path, script_path: Path) -> bool:
        """Launch terminal with script"""
        try:
            if self.platform == "wsl":
                return self._launch_wsl(directory, script_path)
            elif self.platform == "macos":
                return self._launch_macos(directory, script_path)
            elif self.platform == "linux":
                return self._launch_linux(directory, script_path)
            else:
                logger.error(f"Unsupported platform: {self.platform}")
                return False
        except Exception as e:
            logger.error(f"Error launching terminal: {e}")
            return False
    
    def _launch_wsl(self, directory: Path, script_path: Path) -> bool:
        """Launch terminal on WSL"""
        try:
            # Convert paths
            win_path = subprocess.check_output(
                ["wslpath", "-w", str(directory)], text=True
            ).strip()
            wsl_path = str(directory)
            
            # Try Windows Terminal first
            if self._check_command_exists("wt.exe"):
                cmd = self.terminal_cmds["wt"]
                cmd = [c.format(path=win_path, wsl_path=wsl_path, script=script_path) for c in cmd]
                subprocess.Popen(cmd)
                return True
            else:
                # Fallback to cmd
                cmd = self.terminal_cmds["cmd"]
                cmd = [c.format(path=win_path, wsl_path=wsl_path, script=script_path) for c in cmd]
                subprocess.Popen(cmd)
                return True
                
        except Exception as e:
            logger.error(f"WSL launch error: {e}")
            return False    
    def _launch_macos(self, directory: Path, script_path: Path) -> bool:
        """Launch terminal on macOS"""
        try:
            # Try iTerm first if available
            if self._check_command_exists("osascript"):
                if subprocess.run(["osascript", "-e", 'tell application "System Events" to get name of every process'], 
                                capture_output=True, text=True).stdout.find("iTerm") != -1:
                    terminal_type = "iterm"
                else:
                    terminal_type = "terminal"
                
                script_template = self.terminal_cmds[terminal_type]["script"]
                script = script_template.format(path=directory, script=script_path)
                
                subprocess.run(["osascript", "-e", script])
                return True
                
        except Exception as e:
            logger.error(f"macOS launch error: {e}")
            return False
    
    def _launch_linux(self, directory: Path, script_path: Path) -> bool:
        """Launch terminal on Linux"""
        terminals = ["gnome-terminal", "konsole", "xterm", "terminator"]
        
        for term in terminals:
            if self._check_command_exists(term):
                cmd = self.terminal_cmds[term]
                cmd = [c.format(path=directory, script=script_path) for c in cmd]
                subprocess.Popen(cmd)
                return True
        
        logger.error("No supported terminal found on Linux")
        return False
    
    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _check_required_tools(self):
        """Check for platform-specific required tools and warn if missing"""
        warnings = []
        
        if self.platform == "linux":
            # Check for clipboard tools
            if not self._check_command_exists("xclip") and not self._check_command_exists("xsel"):
                warnings.append("No clipboard tool found. Install xclip or xsel for clipboard support:")
                warnings.append("  Ubuntu/Debian: sudo apt-get install xclip")
                warnings.append("  Fedora: sudo dnf install xclip")
                warnings.append("  Arch: sudo pacman -S xclip")
            
            # Check for automation tools (only for basic script)
            if not self._check_command_exists("xdotool"):
                warnings.append("xdotool not found. Install for window automation support:")
                warnings.append("  Ubuntu/Debian: sudo apt-get install xdotool")
                warnings.append("  Fedora: sudo dnf install xdotool")
                warnings.append("  Arch: sudo pacman -S xdotool")
                warnings.append("  Note: Enhanced mode with pexpect provides better automation")
        
        elif self.platform == "macos":
            # macOS uses built-in tools (pbcopy, osascript) so no warnings needed
            pass
        
        elif self.platform == "wsl":
            # WSL-specific checks
            if not self._check_command_exists("wslpath"):
                warnings.append("wslpath not found. Make sure you're running in WSL")
        
        if warnings:
            print(f"\n{Fore.YELLOW}Platform compatibility warnings:{Style.RESET_ALL}")
            for warning in warnings:
                print(f"  {warning}")
            print()


class ClaudeAutomation:
    """Handle Claude Code automation using pexpect or subprocess"""
    
    def __init__(self, directory: Path, coderun_content: str, init_content: str):
        self.directory = directory
        self.coderun_content = coderun_content
        self.init_content = init_content
        self.use_pexpect = pexpect is not None and platform.system().lower() != "windows"
    
    def create_script(self) -> Path:
        """Create automation script"""
        script_name = f"claude_auto_{self.directory.name}.sh"
        script_path = self.directory / script_name
        
        if self.use_pexpect:
            script_content = self._create_pexpect_script()
        else:
            script_content = self._create_basic_script()
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        logger.info(f"Created automation script: {script_path}")
        return script_path
    
    def _create_pexpect_script(self) -> str:
        """Create script using pexpect for better automation"""
        return f'''#!/usr/bin/env python3
import pexpect
import sys
import time
import os

os.chdir("{self.directory}")
print(f"Working in: {self.directory}")

# Try to resume session
print("Attempting to resume Claude Code session...")
child = pexpect.spawn("claude --resume --dangerously-skip-permissions", timeout=30)
child.logfile_read = sys.stdout.buffer

try:
    index = child.expect(["Select a session", "No sessions found", pexpect.EOF], timeout=5)
    
    if index == 0:  # Session found
        print("\\nSession found, selecting most recent...")
        child.sendline("")  # Select first/most recent
        child.expect([".*>", ".*$"], timeout=10)
        
        # Send coderun content
        print("\\nSending main instructions...")
        child.sendline("""{self.coderun_content}""")
        
    else:  # No session, start new
        print("\\nNo session to resume, starting new...")
        child = pexpect.spawn("claude --dangerously-skip-permissions", timeout=30)
        child.logfile_read = sys.stdout.buffer
        
        # Wait for main prompt
        child.expect([".*>", ".*$"], timeout=10)
        
        # Send /init
        print("\\nSending /init command...")
        child.sendline("/init")
        child.expect([".*>", ".*$"], timeout=10)
        
        # Send init content
        print("\\nSending initialization instructions...")
        child.sendline("""{self.init_content}""")
        child.expect([".*>", ".*$"], timeout=10)
        
        # Send main content
        print("\\nSending main instructions...")
        child.sendline("""{self.coderun_content}""")
    
    # Keep interactive
    print("\\nClaude Code is ready. Switching to interactive mode...")
    child.interact()
    
except Exception as e:
    print(f"\\nError: {{e}}")
    child.close()
    sys.exit(1)
'''    
    def _create_basic_script(self) -> str:
        """Create basic script for platforms without pexpect"""
        return f'''#!/bin/bash
# Claude Code Automation Script
# Directory: {self.directory.name}

set -e
cd "{self.directory}"
echo "Working in: $(pwd)"

# Create temporary files for instructions
CODERUN_FILE=$(mktemp)
INIT_FILE=$(mktemp)

cat > "$CODERUN_FILE" << 'EOF'
{self.coderun_content}
EOF

cat > "$INIT_FILE" << 'EOF'
{self.init_content}
EOF

# Function to cleanup
cleanup() {{
    rm -f "$CODERUN_FILE" "$INIT_FILE"
}}
trap cleanup EXIT

echo "Starting Claude Code automation..."

# Try to resume session
if claude --resume --dangerously-skip-permissions 2>&1 | grep -q "Select a session"; then
    echo "Resuming session..."
    # Use expect if available, otherwise manual steps
    if command -v expect >/dev/null 2>&1; then
        expect -c "
            spawn claude --resume --dangerously-skip-permissions
            expect \\"Select a session\\"
            send \\"\\r\\"
            expect -re \\".*[>$]\\"
            send_user \\"\\nSending main instructions...\\n\\"
            send \\"$(cat $CODERUN_FILE)\\r\\"
            interact
        "
    else
        echo "Note: Install 'expect' for better automation"
        echo "Please manually:"
        echo "1. Press Enter to select the most recent session"
        echo "2. Paste the contents of: $CODERUN_FILE"
        claude --resume --dangerously-skip-permissions
    fi
else
    echo "Starting new session..."
    if command -v expect >/dev/null 2>&1; then
        expect -c "
            spawn claude --dangerously-skip-permissions
            expect -re \\".*[>$]\\"
            send \\"/init\\r\\"
            expect -re \\".*[>$]\\"
            send_user \\"\\nSending initialization instructions...\\n\\"
            send \\"$(cat $INIT_FILE)\\r\\"
            expect -re \\".*[>$]\\"
            send_user \\"\\nSending main instructions...\\n\\"
            send \\"$(cat $CODERUN_FILE)\\r\\"
            interact
        "
    else
        echo "Note: Install 'expect' for better automation"
        echo "Please manually:"
        echo "1. Type: /init"
        echo "2. Paste the contents of: $INIT_FILE"
        echo "3. Paste the contents of: $CODERUN_FILE"
        claude --dangerously-skip-permissions
    fi
fi
'''


class ClaudeCodeRunnerEnhanced:
    """Enhanced Claude Code Runner with better automation"""
    
    def __init__(self, base_dir: str, coderun_file: str = "coderun.md",
                 init_file: str = "coderun_init.md", delay: int = 2,
                 wsl_distro: str = "Ubuntu"):
        self.base_dir = Path(base_dir).resolve()
        self.coderun_file = coderun_file
        self.init_file = init_file
        self.delay = delay
        self.wsl_distro = wsl_distro
        self.platform = self._detect_platform()
        self.launcher = TerminalLauncher(self.platform, wsl_distro)
        
        # Read instruction files once
        self.coderun_content = self._read_instruction_file(self.coderun_file)
        self.init_content = self._read_instruction_file(self.init_file)
        
        logger.info(f"Enhanced ClaudeCodeRunner initialized")
        logger.info(f"Platform: {self.platform}")
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
    
    def _read_instruction_file(self, filename: str) -> str:
        """Read instruction file content"""
        search_paths = [
            self.base_dir / filename,
            self.base_dir.parent / filename,
            Path.cwd() / filename,
            Path(__file__).parent / filename
        ]
        
        for path in search_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        logger.info(f"Loaded instruction file: {path}")
                        return content
                except Exception as e:
                    logger.error(f"Error reading {path}: {e}")
        
        logger.warning(f"Instruction file not found: {filename}")
        return f"# {filename} not found\\n# Please create this file with your instructions"    
    def get_subdirectories(self, exclude: Optional[List[str]] = None) -> List[Path]:
        """Get all subdirectories"""
        exclude = exclude or []
        exclude_set = set(exclude)
        exclude_set.add('.git')  # Always exclude .git
        
        subdirs = []
        try:
            for item in self.base_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    if item.name not in exclude_set:
                        subdirs.append(item)
        except Exception as e:
            logger.error(f"Error scanning directories: {e}")
            raise
        
        return sorted(subdirs)
    
    def process_directory(self, directory: Path) -> bool:
        """Process a single directory"""
        try:
            # Create automation handler
            automation = ClaudeAutomation(
                directory, 
                self.coderun_content, 
                self.init_content
            )
            
            # Create script
            script_path = automation.create_script()
            
            # Launch terminal
            success = self.launcher.launch(directory, script_path)
            
            if success:
                logger.info(f"Successfully launched terminal for {directory.name}")
            else:
                logger.error(f"Failed to launch terminal for {directory.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing {directory.name}: {e}")
            return False
    
    def run(self, exclude: Optional[List[str]] = None, dry_run: bool = False,
            parallel: bool = False, max_parallel: int = 3):
        """
        Run the automation
        
        Args:
            exclude: Directories to exclude
            dry_run: Show what would be done without executing
            parallel: Launch terminals in parallel
            max_parallel: Maximum parallel launches
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Claude Code Runner Enhanced{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"Base directory: {Fore.GREEN}{self.base_dir}{Style.RESET_ALL}")
        print(f"Platform: {Fore.GREEN}{self.platform}{Style.RESET_ALL}")
        print(f"Using pexpect: {Fore.GREEN}{pexpect is not None}{Style.RESET_ALL}")
        
        # Get subdirectories
        subdirs = self.get_subdirectories(exclude)
        
        if not subdirs:
            print(f"\n{Fore.YELLOW}No subdirectories found{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.BLUE}Found {len(subdirs)} directories:{Style.RESET_ALL}")
        for subdir in subdirs:
            print(f"  {Fore.BLUE}→{Style.RESET_ALL} {subdir.name}")
        
        if dry_run:
            print(f"\n{Fore.YELLOW}Dry run - no actions will be taken{Style.RESET_ALL}")
            return
        
        # Process directories
        print(f"\n{Fore.GREEN}Starting processing...{Style.RESET_ALL}")
        results = {"success": 0, "failed": 0}
        
        if parallel and len(subdirs) > 1:
            self._process_parallel(subdirs, results, max_parallel)
        else:
            self._process_sequential(subdirs, results)
        
        # Summary
        self._print_summary(results, len(subdirs))
    
    def _process_sequential(self, subdirs: List[Path], results: Dict[str, int]):
        """Process directories sequentially"""
        for i, subdir in enumerate(subdirs, 1):
            print(f"\n{Fore.CYAN}[{i}/{len(subdirs)}] Processing: {subdir.name}{Style.RESET_ALL}")
            
            if self.process_directory(subdir):
                results["success"] += 1
                print(f"{Fore.GREEN}✓ Success: {subdir.name}{Style.RESET_ALL}")
            else:
                results["failed"] += 1
                print(f"{Fore.RED}✗ Failed: {subdir.name}{Style.RESET_ALL}")
            
            if i < len(subdirs):
                print(f"{Fore.YELLOW}Waiting {self.delay}s...{Style.RESET_ALL}")
                time.sleep(self.delay)
    
    def _process_parallel(self, subdirs: List[Path], results: Dict[str, int], 
                         max_parallel: int):
        """Process directories in parallel"""
        print(f"{Fore.MAGENTA}Using parallel processing (max {max_parallel}){Style.RESET_ALL}")
        
        work_queue = queue.Queue()
        for subdir in subdirs:
            work_queue.put(subdir)
        
        threads = []
        lock = threading.Lock()
        
        def worker():
            while True:
                try:
                    subdir = work_queue.get(timeout=1)
                    success = self.process_directory(subdir)
                    
                    with lock:
                        if success:
                            results["success"] += 1
                            print(f"{Fore.GREEN}✓ {subdir.name}{Style.RESET_ALL}")
                        else:
                            results["failed"] += 1
                            print(f"{Fore.RED}✗ {subdir.name}{Style.RESET_ALL}")
                    
                    work_queue.task_done()
                    time.sleep(self.delay)
                    
                except queue.Empty:
                    break
        
        # Start workers
        for _ in range(min(max_parallel, len(subdirs))):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Wait for completion
        work_queue.join()
        for t in threads:
            t.join()
    
    def _print_summary(self, results: Dict[str, int], total: int):
        """Print execution summary"""
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}Summary:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Successful:{Style.RESET_ALL} {results['success']}")
        print(f"  {Fore.RED}Failed:{Style.RESET_ALL} {results['failed']}")
        print(f"  {Fore.BLUE}Total:{Style.RESET_ALL} {total}")
        
        success_rate = (results['success'] / total * 100) if total > 0 else 0
        color = Fore.GREEN if success_rate >= 80 else Fore.YELLOW if success_rate >= 50 else Fore.RED
        print(f"  {color}Success Rate:{Style.RESET_ALL} {success_rate:.1f}%")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Claude Code Runner - Automate Claude Code sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/projects
  %(prog)s /path/to/projects --exclude node_modules,dist,build
  %(prog)s /path/to/projects --parallel --max-parallel 5
  %(prog)s /path/to/projects --coderun instructions.md --init setup.md
  %(prog)s /path/to/projects --dry-run --verbose
        """
    )    
    parser.add_argument("base_dir", help="Base directory to scan")
    parser.add_argument("--coderun", default="coderun.md", 
                       help="Main instruction file")
    parser.add_argument("--init", default="coderun_init.md",
                       help="Initialization instruction file")
    parser.add_argument("--delay", type=int, default=2,
                       help="Delay between launches (seconds)")
    parser.add_argument("--wsl-distro", default="Ubuntu",
                       help="WSL distribution name (default: Ubuntu)")
    parser.add_argument("--exclude", help="Comma-separated directories to exclude")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done")
    parser.add_argument("--parallel", action="store_true",
                       help="Launch terminals in parallel")
    parser.add_argument("--max-parallel", type=int, default=3,
                       help="Maximum parallel launches")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate directory
    base_dir = Path(args.base_dir)
    if not base_dir.exists():
        print(f"{Fore.RED}Error: Directory not found: {base_dir}{Style.RESET_ALL}")
        sys.exit(1)
    
    if not base_dir.is_dir():
        print(f"{Fore.RED}Error: Not a directory: {base_dir}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Parse excludes
    exclude = args.exclude.split(',') if args.exclude else []
    
    try:
        # Create runner
        runner = ClaudeCodeRunnerEnhanced(
            base_dir=str(base_dir),
            coderun_file=args.coderun,
            init_file=args.init,
            delay=args.delay,
            wsl_distro=args.wsl_distro
        )
        
        # Run
        runner.run(
            exclude=exclude,
            dry_run=args.dry_run,
            parallel=args.parallel,
            max_parallel=args.max_parallel
        )
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()