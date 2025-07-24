# Complete Development Workflow with All Stages

## Overview

The enhanced Claude Code Runner now supports 14 distinct development stages, providing comprehensive coverage from initial planning through to production release and maintenance.

## Complete Stage Flow

```
┌─────────────────────────┐
│ planning_design_gitsetup│ ← Project inception
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│      api_design         │ ← Contract-first development
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    scaffolding_mvp      │ ← TDD implementation
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   integration_test      │ ← Service integration validation
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   database_design       │ ← Data layer implementation
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│      code_debug         │ ← Quality improvements
└───────────┬─────────────┘
            │
            ├─────────────┬──────────────┐
            ▼             ▼              ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│performance      │ │security_audit│ │addchange_check  │ ← Parallel quality gates
│baseline         │ └──────┬───────┘ └────────┬────────┘
└────────┬────────┘        │                  │
         │                 ▼                  │
         └────────►┌───────────────┐◄────────┘
                   │  deploy_test   │ ← Production readiness
                   └───────┬───────┘
                           │
                           ▼
                   ┌───────────────────────┐
                   │monitoring_observability│ ← Operational excellence
                   └───────┬───────────────┘
                           │
                           ▼
                   ┌─────────────────┐
                   │release_management│ ← Controlled releases
                   └───────┬─────────┘
                           │
                           ▼
                   ┌─────────────────┐
                   │    document     │ ← Knowledge preservation
                   └───────┬─────────┘
                           │
                           ▼
                   ┌─────────────────┐
                   │    upgrade      │ ← Continuous improvement
                   └─────────────────┘
```

## Stage Descriptions

### 1. **planning_design_gitsetup**
- **Purpose**: Establish project foundation
- **Key Activities**: Architecture design, Git setup, documentation templates
- **Review Focus**: Technology choices, architectural decisions

### 2. **api_design**
- **Purpose**: Define API contracts before implementation
- **Key Activities**: OpenAPI/GraphQL specs, mock servers, SDK generation
- **Review Focus**: API consistency, versioning strategy

### 3. **scaffolding_mvp**
- **Purpose**: Build core functionality with TDD
- **Key Activities**: Test framework setup, feature implementation, CI/CD basics
- **Review Focus**: Test coverage, code structure

### 4. **integration_test**
- **Purpose**: Validate component interactions
- **Key Activities**: E2E tests, contract testing, service mocking
- **Review Focus**: Integration coverage, test reliability

### 5. **database_design**
- **Purpose**: Implement data persistence layer
- **Key Activities**: Schema design, migrations, repository pattern
- **Review Focus**: Performance, data integrity

### 6. **code_debug**
- **Purpose**: Fix bugs and optimize code
- **Key Activities**: Bug hunting, refactoring, performance tuning
- **Review Focus**: Code quality metrics, bug resolution

### 7. **performance_baseline**
- **Purpose**: Establish and meet performance targets
- **Key Activities**: Load testing, profiling, optimization
- **Review Focus**: Response times, throughput, resource usage

### 8. **security_audit**
- **Purpose**: Identify and fix security vulnerabilities
- **Key Activities**: Dependency scanning, SAST/DAST, compliance checks
- **Review Focus**: Vulnerability status, OWASP compliance

### 9. **addchange_check**
- **Purpose**: Enforce code review and change management
- **Key Activities**: PR workflows, branch protection, rollback procedures
- **Review Focus**: PR metrics, rollback readiness

### 10. **deploy_test**
- **Purpose**: Production deployment preparation
- **Key Activities**: CI/CD pipelines, environment setup, smoke tests
- **Review Focus**: Deployment automation, environment parity

### 11. **monitoring_observability**
- **Purpose**: Implement comprehensive monitoring
- **Key Activities**: Metrics, logs, traces, alerting, dashboards
- **Review Focus**: Coverage, alert quality, MTTR capability

### 12. **release_management**
- **Purpose**: Automate version control and releases
- **Key Activities**: Semantic versioning, changelogs, release notes
- **Review Focus**: Release process, rollout strategies

### 13. **document**
- **Purpose**: Create comprehensive documentation
- **Key Activities**: API docs, user guides, runbooks
- **Review Focus**: Documentation completeness, accuracy

### 14. **upgrade**
- **Purpose**: Modernize and enhance the system
- **Key Activities**: Dependency updates, new features, tech debt reduction
- **Review Focus**: Breaking changes, performance impact

## Stage Execution Patterns

### Sequential Execution
Most stages follow a sequential pattern for initial development:
```bash
./run_stage.sh /projects --stage planning_design_gitsetup
# Complete planning stage...
./run_stage.sh /projects --stage api_design
# Continue through each stage...
```

### Parallel Execution
Some stages can run in parallel after code_debug:
```bash
# Run quality checks in parallel
./run_stage.sh /projects --stage performance_baseline --parallel &
./run_stage.sh /projects --stage security_audit --parallel &
./run_stage.sh /projects --stage addchange_check --parallel &
```

### Iterative Execution
Stages can be re-run as needed:
```bash
# After finding issues in security_audit
./run_stage.sh /projects --stage code_debug
./run_stage.sh /projects --stage security_audit
```

## Review Documents

Each stage creates timestamped review documents:
- `<stage>_review_<YYYYMMDD_HHMMSS>.md`
- Contains stage-specific metrics and checklists
- Requires human approval before proceeding
- Tracks decisions and progress

## Best Practices

1. **Complete Each Stage**: Don't skip stages even if they seem unnecessary
2. **Review Before Proceeding**: Always review the stage output before moving on
3. **Use Stage-Appropriate Commands**: Each stage has specific focus areas
4. **Maintain Review Documents**: Keep them in version control for audit trails
5. **Iterate When Needed**: Return to previous stages if issues are found

## Common Workflows

### New Project
```
planning → api_design → scaffolding → integration_test → database → 
code_debug → (performance + security + addchange) → deploy → 
monitoring → release → document → upgrade
```

### API-First Development
```
api_design → scaffolding → integration_test → ...
```

### Legacy Modernization
```
security_audit → code_debug → performance_baseline → 
addchange_check → monitoring → upgrade
```

### Hotfix Process
```
addchange_check → code_debug → security_audit → 
deploy_test → release_management
```

## Integration Points

### CI/CD Integration
- Stages can be triggered by CI/CD pipelines
- Review documents can block deployments
- Automated stage progression with approvals

### Tool Integration
- Git hooks can enforce stage completion
- IDE plugins can show current stage
- Dashboards can track stage progress

## Conclusion

The 14-stage development workflow provides comprehensive coverage of the entire software development lifecycle. By following these stages with Claude Code's assistance, teams can ensure consistent quality, security, and operational excellence across all projects.