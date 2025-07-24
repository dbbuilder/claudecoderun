# Stage Review Document System

## Overview

Each development stage in the Autonomous Development Protocol now includes automated creation of review documents that provide checkpoints for human verification. These documents are created with timestamps to track progress and ensure quality control throughout the development lifecycle.

## Review Document Naming Convention

```
<stage_name>_review_<YYYYMMDD_HHMMSS>.md
```

Examples:
- `planning_design_gitsetup_review_20240115_143022.md`
- `scaffolding_mvp_review_20240116_091545.md`
- `database_design_review_20240117_162310.md`

## Review Document Structure

Each review document contains:

1. **Header Information**
   - Generation timestamp
   - Stage name
   - Current status

2. **Stage-Specific Metrics**
   - Test coverage (for stages with testing)
   - Performance benchmarks
   - Security checklist
   - Implementation statistics

3. **Completed Tasks**
   - Checklist of stage objectives
   - Key decisions made
   - Files created/modified

4. **Quality Gates**
   - Verification points before proceeding
   - Prerequisites for next stage
   - Known issues or technical debt

5. **Human Review Requirements**
   - Specific items needing validation
   - Architectural decisions to approve
   - Security measures to verify

6. **Update Sections**
   - For continuation sessions
   - Progress since last review
   - New issues discovered

## Stage-Specific Review Contents

### Planning & Design Stage
- Architecture decisions
- Technology stack choices
- Git workflow strategy
- Documentation completeness

### Scaffolding & MVP Stage
- Test coverage statistics
- TDD compliance verification
- API endpoint documentation
- Security implementation checklist

### Database Design Stage
- Schema overview and ERD
- Indexing strategy
- Performance benchmarks
- Migration status

### Code & Debug Stage
- Bug fix summary
- Performance improvements
- Code quality metrics
- Security vulnerability scan results

### Deploy & Test Stage
- Environment configurations
- CI/CD pipeline status
- Load testing results
- Production readiness checklist

### Documentation Stage
- Documentation coverage
- Missing sections identified
- Quality verification
- Publishing status

### Upgrade Stage
- Dependency update summary
- Breaking changes handled
- Performance improvements
- Feature additions

## Automation Implementation

### In Initial Files (`coderun_init_<stage>.md`)

```bash
# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create review document
cat > "<stage>_review_${TIMESTAMP}.md" << EOF
# Stage Review Content
EOF

# Commit to git
git add "<stage>_review_${TIMESTAMP}.md"
git commit -m "docs: add <stage> review document for human verification"
```

### In Continuation Files (`coderun_continue_<stage>.md`)

```bash
# Check for existing review
EXISTING_REVIEW=$(ls <stage>_review_*.md 2>/dev/null | head -1)

if [ -n "$EXISTING_REVIEW" ]; then
    # Update existing document
    cat >> "$EXISTING_REVIEW" << EOF
## Update - $(date +"%Y-%m-%d %H:%M:%S")
EOF
else
    # Create new document
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    # ... create full document
fi
```

## Benefits

1. **Traceability**: Timestamp tracking of stage completion
2. **Quality Control**: Human verification points
3. **Progress Tracking**: Clear documentation of what's been done
4. **Decision Documentation**: Record of architectural choices
5. **Issue Tracking**: Known problems documented for resolution
6. **Handoff Support**: Clear information for team transitions

## Usage Workflow

1. **Autonomous Execution**: Claude Code follows stage instructions
2. **Review Generation**: Creates timestamped review document
3. **Human Review**: Developer reviews the document
4. **Approval/Feedback**: Human approves or requests changes
5. **Stage Transition**: Move to next stage after approval

## Integration with Git

All review documents are:
- Automatically added to git
- Committed with descriptive messages
- Preserved in project history
- Available for future reference

## Example Review Document

```markdown
# Planning, Design & Git Setup - Stage Review
**Generated**: 2024-01-15 14:30:22
**Stage**: planning_design_gitsetup
**Status**: Ready for Human Review

## Completed Tasks
- ✓ Project structure created
- ✓ Git repository initialized
- ✓ Documentation foundation established
- ✓ Architecture design documented
- ✓ Development standards defined

## Key Decisions Made
- Technology stack: Node.js, React, PostgreSQL
- Architecture pattern: Microservices
- Git workflow: GitFlow with PR reviews
- Testing approach: TDD with Jest

## Files Created/Modified
- README.md
- REQUIREMENTS.md
- ARCHITECTURE.md
- STANDARDS.md
- TODO.md
- .gitignore

## Human Review Required
1. Verify technology choices align with requirements
2. Review architectural decisions
3. Confirm coding standards are appropriate
4. Approve Git workflow strategy
5. Validate documentation completeness

## Next Stage Prerequisites
- [ ] All planning documents complete
- [ ] Git repository properly configured
- [ ] Team can onboard using documentation
- [ ] Ready for scaffolding stage

## Notes for Reviewer
- Chose PostgreSQL over MongoDB due to ACID requirements
- Microservices architecture selected for independent scaling
- Consider adding Redis for session management in next stage
```

## Best Practices

1. **Review Promptly**: Don't let reviews accumulate
2. **Document Decisions**: Add notes about approvals/changes
3. **Version Control**: Keep all review documents in git
4. **Team Communication**: Share review documents with team
5. **Continuous Updates**: Update reviews during continuation sessions

This system ensures that autonomous development maintains human oversight at critical checkpoints while preserving the efficiency of automated workflows.