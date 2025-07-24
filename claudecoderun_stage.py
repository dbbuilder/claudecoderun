#!/usr/bin/env python3
"""
Claude Code Runner - Enhanced Version with Stage Support
Automates opening Claude Code in new terminals with stage-specific instructions
"""

import os
import sys
import time
import platform
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import json
import threading
import queue
import glob

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
        logging.FileHandler('claudecoderun_stage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StageAwareClaudeRunner:
    """Enhanced Claude Code Runner with development stage support"""
    
    def __init__(self, base_dir: str, stage_pattern: Optional[str] = None,
                 delay: int = 2):
        self.base_dir = Path(base_dir).resolve()
        self.stage_pattern = stage_pattern
        self.delay = delay
        self.platform = self._detect_platform()
        self.launcher = TerminalLauncher(self.platform)
        
        logger.info(f"Stage-aware ClaudeCodeRunner initialized")
        logger.info(f"Platform: {self.platform}")
        logger.info(f"Base directory: {self.base_dir}")
        logger.info(f"Stage pattern: {self.stage_pattern}")
    
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
    
    def find_instruction_files(self, directory: Path) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Find instruction files for a directory, supporting wildcards
        
        Returns:
            Tuple of (init_file, continue_file)
        """
        init_file = None
        continue_file = None
        
        # If stage pattern provided, look for stage-specific files
        if self.stage_pattern:
            # Look for stage-specific files
            init_pattern = f"coderun_init_{self.stage_pattern}.md"
            continue_pattern = f"coderun_continue_{self.stage_pattern}.md"
            
            # Search in multiple locations
            search_paths = [
                directory,
                directory.parent,
                self.base_dir,
                self.base_dir.parent,
                Path.cwd(),
                Path(__file__).parent,
                Path("D:/dev3/stages"),  # Stage directory
                Path("/mnt/d/dev3/stages")  # WSL path
            ]
            
            for search_path in search_paths:
                if not search_path.exists():
                    continue
                    
                # Look for exact matches first
                init_candidate = search_path / init_pattern
                continue_candidate = search_path / continue_pattern
                
                if init_candidate.exists():
                    init_file = init_candidate
                    logger.info(f"Found init file: {init_file}")
                
                if continue_candidate.exists():
                    continue_file = continue_candidate
                    logger.info(f"Found continue file: {continue_file}")
                
                # If not found, try glob patterns
                if not init_file:
                    init_matches = list(search_path.glob(init_pattern))
                    if init_matches:
                        init_file = init_matches[0]
                        logger.info(f"Found init file via glob: {init_file}")
                
                if not continue_file:
                    continue_matches = list(search_path.glob(continue_pattern))
                    if continue_matches:
                        continue_file = continue_matches[0]
                        logger.info(f"Found continue file via glob: {continue_file}")
                
                if init_file or continue_file:
                    break
        
        # Fallback to generic files if no stage-specific found
        if not init_file and not continue_file:
            for filename in ["coderun_init.md", "coderun.md"]:
                for search_path in [directory, directory.parent, self.base_dir, Path.cwd()]:
                    candidate = search_path / filename
                    if candidate.exists():
                        init_file = candidate
                        logger.info(f"Using generic file: {init_file}")
                        break
                if init_file:
                    break
        
        return init_file, continue_file
    
    def read_instruction_file(self, file_path: Path) -> str:
        """Read and return instruction file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Successfully read {file_path}")
                return content
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return f"# Error reading {file_path}\n{str(e)}"
    
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
        """Process a single directory with stage awareness"""
        try:
            # Find appropriate instruction files
            init_file, continue_file = self.find_instruction_files(directory)
            
            if not init_file and not continue_file:
                logger.warning(f"No instruction files found for {directory}")
                return False
            
            # Read instruction content
            init_content = self.read_instruction_file(init_file) if init_file else ""
            continue_content = self.read_instruction_file(continue_file) if continue_file else ""
            
            # Determine which content to use
            # If we have a continue file, check if we should use it
            # For now, we'll use init for first run, continue for subsequent
            # This could be enhanced to detect actual session state
            primary_content = init_content if init_content else continue_content
            
            # Create automation handler
            automation = ClaudeAutomation(
                directory, 
                primary_content,
                continue_content if continue_content else init_content
            )
            
            # Create script
            script_path = automation.create_script()
            
            # Launch terminal
            success = self.launcher.launch(directory, script_path)
            
            if success:
                logger.info(f"Successfully launched terminal for {directory.name}")
                if self.stage_pattern:
                    print(f"{Fore.GREEN}✓ Launched with stage: {self.stage_pattern}{Style.RESET_ALL}")
            else:
                logger.error(f"Failed to launch terminal for {directory.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing {directory.name}: {e}")
            return False    
    def run(self, exclude: Optional[List[str]] = None, dry_run: bool = False,
            parallel: bool = False, max_parallel: int = 3):
        """Run the automation with stage support"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Claude Code Runner - Stage Aware{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"Base directory: {Fore.GREEN}{self.base_dir}{Style.RESET_ALL}")
        print(f"Platform: {Fore.GREEN}{self.platform}{Style.RESET_ALL}")
        
        if self.stage_pattern:
            print(f"Stage: {Fore.MAGENTA}{self.stage_pattern}{Style.RESET_ALL}")
        
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
            
            # Show what files would be used
            for subdir in subdirs:
                init_file, continue_file = self.find_instruction_files(subdir)
                print(f"\n{subdir.name}:")
                if init_file:
                    print(f"  Init: {init_file}")
                if continue_file:
                    print(f"  Continue: {continue_file}")
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


# Include the TerminalLauncher and ClaudeAutomation classes from the enhanced version
class TerminalLauncher:
    """Platform-specific terminal launcher"""
    
    def __init__(self, platform_name: str):
        self.platform = platform_name
        self.terminal_cmds = self._get_terminal_commands()
    
    def _get_terminal_commands(self) -> Dict[str, Any]:
        """Get terminal commands for each platform"""
        commands = {
            "wsl": {
                "wt": ["wt.exe", "-d", "{path}", "wsl", "-d", "Ubuntu", "--cd", "{wsl_path}", "--", "bash", "-c", "{script}"],
                "cmd": ["cmd.exe", "/c", "start", "cmd.exe", "/k", "wsl", "-d", "Ubuntu", "--cd", "{wsl_path}", "--", "bash", "{script}"]
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

class ClaudeAutomation:
    """Handle Claude Code automation using pexpect or subprocess"""
    
    def __init__(self, directory: Path, init_content: str, continue_content: str):
        self.directory = directory
        self.init_content = init_content
        self.continue_content = continue_content
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
        
        # Send continue content if available, otherwise init
        content = """{self.continue_content if self.continue_content else self.init_content}"""
        print("\\nSending instructions...")
        child.sendline(content)
        
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
        
        # If we have different continue content, send it too
        if self.continue_content and self.continue_content != self.init_content:
            print("\\nSending main instructions...")
            child.sendline("""{self.continue_content}""")
    
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
INIT_FILE=$(mktemp)
CONTINUE_FILE=$(mktemp)

cat > "$INIT_FILE" << 'EOF'
{self.init_content}
EOF

cat > "$CONTINUE_FILE" << 'EOF'
{self.continue_content}
EOF

# Function to cleanup
cleanup() {{
    rm -f "$INIT_FILE" "$CONTINUE_FILE"
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
            send_user \\"\\nSending instructions...\\n\\"
            send \\"$(cat $CONTINUE_FILE)\\r\\"
            interact
        "
    else
        echo "Note: Install 'expect' for better automation"
        echo "Please manually:"
        echo "1. Press Enter to select the most recent session"
        echo "2. Paste the contents of: $CONTINUE_FILE"
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
            if [ "$INIT_FILE" != "$CONTINUE_FILE" ]; then
                send_user \\"\\nSending main instructions...\\n\\"
                send \\"$(cat $CONTINUE_FILE)\\r\\"
            fi
            interact
        "
    else
        echo "Note: Install 'expect' for better automation"
        echo "Please manually:"
        echo "1. Type: /init"
        echo "2. Paste the contents of: $INIT_FILE"
        if [ "$INIT_FILE" != "$CONTINUE_FILE" ]; then
            echo "3. Paste the contents of: $CONTINUE_FILE"
        fi
        claude --dangerously-skip-permissions
    fi
fi
'''


def main():
    """Main entry point with stage support"""
    parser = argparse.ArgumentParser(
        description="Claude Code Runner with Development Stage Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with specific stage
  %(prog)s /path/to/projects --stage planning_design_gitsetup
  %(prog)s /path/to/projects --stage scaffolding_mvp
  %(prog)s /path/to/projects --stage database_design
  
  # Run with wildcard stage pattern
  %(prog)s /path/to/projects --stage "planning*"
  %(prog)s /path/to/projects --stage "*mvp"
  
  # Traditional usage (backward compatible)
  %(prog)s /path/to/projects
  %(prog)s /path/to/projects --exclude node_modules,dist
  
  # Advanced options
  %(prog)s /path/to/projects --stage deploy_test --parallel --max-parallel 5
  %(prog)s /path/to/projects --stage upgrade --dry-run --verbose
        """
    )
    
    parser.add_argument("base_dir", help="Base directory to scan")
    
    parser.add_argument("--stage", 
                       help="Development stage (e.g., planning_design_gitsetup, scaffolding_mvp)")
    
    parser.add_argument("--coderun", 
                       help="Override default instruction file pattern")
    
    parser.add_argument("--init",
                       help="Override default init file pattern")
    
    parser.add_argument("--delay", type=int, default=2,
                       help="Delay between launches (seconds)")
    
    parser.add_argument("--exclude", 
                       help="Comma-separated directories to exclude")
    
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done")
    
    parser.add_argument("--parallel", action="store_true",
                       help="Launch terminals in parallel")
    
    parser.add_argument("--max-parallel", type=int, default=3,
                       help="Maximum parallel launches")
    
    parser.add_argument("--list-stages", action="store_true",
                       help="List available stages and exit")
    
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # List stages if requested
    if args.list_stages:
        print(f"\n{Fore.CYAN}Available Development Stages:{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}Required Stages:{Style.RESET_ALL}")
        required_stages = [
            ("planning_design_gitsetup", "Initial planning, design, and Git setup"),
            ("scaffolding_mvp", "Build MVP structure with TDD"),
            ("database_design", "Design and implement database layer"),
            ("code_debug", "Debug, optimize, and improve code quality"),
            ("addchange_check", "Pull request workflow and change management"),
            ("deploy_test", "Set up deployment and production testing"),
            ("document", "Create comprehensive documentation"),
            ("upgrade", "Upgrade dependencies and add enhancements")
        ]
        for stage, desc in required_stages:
            print(f"  {Fore.GREEN}{stage:<30}{Style.RESET_ALL} - {desc}")
        
        print(f"\n{Fore.YELLOW}Optional Stages:{Style.RESET_ALL}")
        optional_stages = [
            ("opt_api_design", "API-first design and contract definition"),
            ("opt_integration_test", "End-to-end and integration testing"),
            ("opt_performance_baseline", "Establish performance metrics and optimize"),
            ("opt_security_audit", "Security assessment and remediation"),
            ("opt_monitoring_observability", "Implement monitoring and observability"),
            ("opt_release_management", "Version control and release automation")
        ]
        for stage, desc in optional_stages:
            print(f"  {Fore.YELLOW}{stage:<30}{Style.RESET_ALL} - {desc} {Fore.DIM}(optional){Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Usage Examples:{Style.RESET_ALL}")
        print(f"  {Fore.BLUE}Required stage:{Style.RESET_ALL} %(prog)s /path/to/projects --stage scaffolding_mvp")
        print(f"  {Fore.BLUE}Optional stage:{Style.RESET_ALL} %(prog)s /path/to/projects --stage opt_api_design")
        print(f"\n{Fore.YELLOW}Use --stage <name> to run with a specific stage{Style.RESET_ALL}")
        sys.exit(0)
    
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
        # Create runner with stage support
        runner = StageAwareClaudeRunner(
            base_dir=str(base_dir),
            stage_pattern=args.stage,
            delay=args.delay
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