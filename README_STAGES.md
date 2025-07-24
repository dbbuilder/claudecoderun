# Claude Code Runner - Stage-Aware Development

An enhanced version of Claude Code Runner that supports development stage-specific instructions, enabling automated workflows through different phases of software development.

## Development Stages

The tool supports the following development stages, each with specialized initialization and continuation instructions:

1. **planning_design_gitsetup** - Initial planning, design, and Git repository setup
2. **scaffolding_mvp** - Building MVP structure using Test-Driven Development
3. **database_design** - Database schema design and implementation
4. **code_debug** - Debugging, optimization, and code quality improvements
5. **addchange_check** - Pull request workflow and change management
6. **deploy_test** - Deployment setup and production testing
7. **document** - Comprehensive documentation creation
8. **upgrade** - Dependency updates and feature enhancements

## Stage Flow and Dependencies

```
planning_design_gitsetup
         ↓
   scaffolding_mvp
         ↓
   database_design
         ↓
     code_debug
         ↓
  addchange_check  ← NEW: Protects main branch
         ↓
    deploy_test
         ↓
     document
         ↓
     upgrade
```

## The Add/Change Check Stage

The `addchange_check` stage is a critical quality gate that:

### Purpose
- Enforces pull request workflows for all changes
- Protects the main branch from direct commits
- Enables safe rollbacks through Git history
- Ensures code review and CI/CD validation

### Key Features
1. **Branch Protection Setup**
   - Main branch requires PR reviews
   - Automated CI/CD checks must pass
   - No force pushes allowed
   - Dismiss stale reviews

2. **Standardized PR Process**
   - PR templates for consistency
   - Automated testing on all PRs
   - Required review approvals
   - Merge conflict prevention

3. **Rollback Capabilities**
   - Every change is revertible
   - Feature flags for instant rollback
   - Database migration rollbacks
   - Documented rollback procedures

4. **Change Documentation**
   - CHANGELOG.md maintenance
   - PR descriptions with impact analysis
   - Rollback plans for each PR
   - Risk assessment documentation

### Benefits
- **Safety**: No accidental commits to production
- **Quality**: Enforced code review process
- **Traceability**: Complete history of changes
- **Reversibility**: Easy rollback of problematic changes
- **Collaboration**: Team review and knowledge sharing

## Stage-Specific Instructions

Each stage has two instruction files:
- `coderun_init_<stage>.md` - Used when starting a new Claude Code session
- `coderun_continue_<stage>.md` - Used when resuming an existing session

These files follow the Autonomous Development Protocol, providing stage-specific guidance for Claude Code.

## Review Documents

Each stage creates timestamped review documents for human verification:
- Format: `<stage>_review_<YYYYMMDD_HHMMSS>.md`
- Contains stage-specific metrics and checklists
- Tracks progress and decisions made
- Provides quality gates before proceeding

## Usage

### Basic Stage Usage

```bash
# Run with a specific stage
./run_stage.sh /path/to/projects --stage planning_design_gitsetup

# Run the new add/change check stage
./run_stage.sh /path/to/projects --stage addchange_check

# Windows
run_stage.bat D:\projects --stage addchange_check
```

### List Available Stages

```bash
./run_stage.sh --list-stages
```

### Stage File Locations

The tool searches for stage instruction files in the following locations (in order):
1. Current project directory
2. Parent directory
3. Base directory specified
4. Current working directory
5. Script directory
6. `D:\dev3\stages` (or `/mnt/d/dev3/stages` on WSL)

### Examples

```bash
# Planning stage for multiple projects
./run_stage.sh ~/projects --stage planning_design_gitsetup

# MVP scaffolding with exclusions
./run_stage.sh ~/projects --stage scaffolding_mvp --exclude node_modules,build

# Database design with parallel processing
./run_stage.sh ~/projects --stage database_design --parallel --max-parallel 5

# Code debug stage
./run_stage.sh ~/projects --stage code_debug

# NEW: Add/change check stage for PR workflow
./run_stage.sh ~/projects --stage addchange_check

# Deployment stage with dry run
./run_stage.sh ~/projects --stage deploy_test --dry-run

# Documentation stage with custom delay
./run_stage.sh ~/projects --stage document --delay 5
```

## Autonomous Development Protocol

Each stage follows the Autonomous Development Protocol which includes:

1. **Test-Driven Development (TDD)**
   - Write failing tests first
   - Implement minimal code to pass
   - Refactor while keeping tests green

2. **Git Management**
   - Frequent commits (every 15-30 minutes)
   - Descriptive commit messages
   - Push every 3-4 commits

3. **Continuous Documentation**
   - Update TODO.md after each session
   - Maintain inline code comments
   - Keep README.md current

4. **Quality Assurance**
   - Run tests before each commit
   - Maintain code coverage >80%
   - Follow established patterns

5. **Change Management** (NEW in addchange_check)
   - All changes through pull requests
   - Automated CI/CD validation
   - Required code reviews
   - Documented rollback procedures

## Stage Workflows

### Planning & Design Stage
- Creates project structure
- Initializes Git repository
- Generates documentation templates
- Establishes coding standards

### Scaffolding & MVP Stage
- Sets up test framework
- Implements core features with TDD
- Creates basic API structure
- Establishes error handling

### Database Design Stage
- Designs schema with tests
- Implements migrations
- Creates repository pattern
- Optimizes queries

### Code & Debug Stage
- Identifies and fixes bugs
- Optimizes performance
- Refactors code
- Improves test coverage

### Add/Change Check Stage (NEW)
- Implements branch protection
- Creates PR workflows
- Sets up CI/CD checks
- Documents rollback procedures
- Organizes changes into reviewable PRs

### Deploy & Test Stage
- Sets up CI/CD pipelines
- Configures environments
- Implements monitoring
- Performs load testing

### Documentation Stage
- Creates developer guides
- Writes user documentation
- Generates API docs
- Updates architecture diagrams

### Upgrade Stage
- Updates dependencies
- Implements new features
- Optimizes performance
- Prepares for scaling

## Advanced Features

### Parallel Processing
Process multiple projects simultaneously:
```bash
./run_stage.sh ~/projects --stage addchange_check --parallel --max-parallel 4
```

### Dry Run Mode
Preview what would be executed:
```bash
./run_stage.sh ~/projects --stage addchange_check --dry-run
```

### Custom Instruction Files
Override default instruction patterns:
```bash
./run_stage.sh ~/projects --stage custom --coderun my_instructions.md
```

## Troubleshooting

### Stage Files Not Found
- Ensure stage files exist in one of the search locations
- Check file naming: `coderun_init_<stage>.md` and `coderun_continue_<stage>.md`
- Use `--dry-run` to see which files would be used

### WSL Path Issues
- Use WSL paths when running from WSL: `/mnt/d/projects`
- Use Windows paths when running from Windows: `D:\projects`

### Terminal Not Opening
- Ensure Windows Terminal is installed (for Windows)
- Check that `wsl` command is available
- Try running with `--verbose` for detailed logs

## Requirements

- Python 3.8+
- Claude Code CLI installed
- Git
- GitHub CLI (optional, for PR management)
- Windows Terminal (recommended for Windows)
- pexpect (optional, for better automation)

## Contributing

1. Add new stages by creating instruction files in the stages directory
2. Follow the Autonomous Development Protocol format
3. Test thoroughly before committing
4. Update documentation

## License

This project follows the same license as the base Claude Code Runner project.