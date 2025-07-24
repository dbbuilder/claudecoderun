# Optional Stages System - Overview

## Concept

The Claude Code Runner now supports both **required** and **optional** stages. Optional stages are prefixed with `opt_` and can be skipped based on project requirements, allowing for flexible workflows that adapt to different project types and constraints.

## Optional Stages Available

### 1. **opt_api_design**
- **Use when**: Building APIs, need documentation, multiple clients
- **Skip when**: No API, internal tools, using existing patterns
- **Quick alternative**: Basic REST conventions documentation

### 2. **opt_security_audit**
- **Use when**: Handling sensitive data, compliance requirements, public-facing
- **Skip when**: Prototypes, internal tools, learning projects
- **Quick alternative**: Basic dependency scan and secrets check

### 3. **opt_performance_baseline**
- **Use when**: High traffic, SLA requirements, real-time systems
- **Skip when**: Internal tools, prototypes, low user count
- **Quick alternative**: Basic response time verification

### 4. **opt_integration_test**
- **Use when**: Multiple services, complex integrations, microservices
- **Skip when**: Monolithic apps, simple projects, no external dependencies
- **Quick alternative**: Basic API endpoint testing

### 5. **opt_monitoring_observability**
- **Use when**: Production systems, 24/7 operations, distributed systems
- **Skip when**: Development only, prototypes, short-lived projects
- **Quick alternative**: Basic health endpoint and logs

### 6. **opt_release_management**
- **Use when**: Regular releases, multiple environments, team collaboration
- **Skip when**: Single developer, continuous deployment, prototypes
- **Quick alternative**: Simple git tags for versions

## Required vs Optional Flow

### Required Stages (Always Execute)
```
1. planning_design_gitsetup     ← Always needed
2. scaffolding_mvp             ← Core development
3. database_design             ← Data layer
4. code_debug                  ← Quality assurance
5. addchange_check             ← Change management
6. deploy_test                 ← Deployment readiness
7. document                    ← Knowledge preservation
8. upgrade                     ← Maintenance
```

### Optional Stages (As Needed)
```
opt_api_design                 ← If building APIs
opt_security_audit             ← If security matters
opt_performance_baseline       ← If performance critical
opt_integration_test          ← If complex integrations
opt_monitoring_observability  ← If production operations
opt_release_management        ← If formal releases
```

## Decision Framework

### When to Use Optional Stages

```
Project Type Decision Tree:

Is this a production system?
├── YES → Consider all optional stages
│   ├── Public-facing? → opt_security_audit required
│   ├── High traffic? → opt_performance_baseline required
│   ├── Multiple services? → opt_integration_test required
│   └── 24/7 operation? → opt_monitoring_observability required
└── NO → Evaluate each optional stage
    ├── Prototype? → Skip most optional stages
    ├── Internal tool? → Skip security, performance, monitoring
    └── Learning project? → Skip all optional stages
```

## Implementation Patterns

### 1. **Minimal Project** (Prototype/POC)
```bash
# Required stages only
./run_stage.sh /project --stage planning_design_gitsetup
./run_stage.sh /project --stage scaffolding_mvp
./run_stage.sh /project --stage database_design
./run_stage.sh /project --stage code_debug
./run_stage.sh /project --stage deploy_test
./run_stage.sh /project --stage document
```

### 2. **Standard Project** (Internal Tool)
```bash
# Required + basic optional stages
./run_stage.sh /project --stage planning_design_gitsetup
./run_stage.sh /project --stage scaffolding_mvp
./run_stage.sh /project --stage opt_integration_test  # If has integrations
./run_stage.sh /project --stage database_design
./run_stage.sh /project --stage code_debug
./run_stage.sh /project --stage deploy_test
./run_stage.sh /project --stage document
```

### 3. **Enterprise Project** (Production System)
```bash
# All stages including optional
./run_stage.sh /project --stage planning_design_gitsetup
./run_stage.sh /project --stage opt_api_design
./run_stage.sh /project --stage scaffolding_mvp
./run_stage.sh /project --stage opt_integration_test
./run_stage.sh /project --stage database_design
./run_stage.sh /project --stage code_debug
./run_stage.sh /project --stage opt_performance_baseline
./run_stage.sh /project --stage opt_security_audit
./run_stage.sh /project --stage addchange_check
./run_stage.sh /project --stage deploy_test
./run_stage.sh /project --stage opt_monitoring_observability
./run_stage.sh /project --stage opt_release_management
./run_stage.sh /project --stage document
./run_stage.sh /project --stage upgrade
```

## Optional Stage Features

### 1. **Skip Documentation**
Each optional stage can be formally skipped with documentation:
```bash
# Creates .skip-{stage-name} file
# Documents reason for skipping
# Commits decision to git
```

### 2. **Minimal Implementation**
Optional stages support minimal implementation:
- Quick checks instead of full audits
- Basic documentation instead of comprehensive specs
- Simple monitoring instead of full observability

### 3. **Risk-Based Depth**
Optional stages adjust depth based on risk:
- **Low Risk**: 5-minute basic checks
- **Medium Risk**: Essential features only  
- **High Risk**: Full stage implementation
- **Critical**: Complete with compliance

### 4. **Review Documents**
Optional stage reviews include:
- Stage execution decision (full/partial/skipped)
- Justification if skipped
- Minimal measures taken
- Risk assessment

## Best Practices

### 1. **Document Skip Decisions**
Always document why an optional stage was skipped:
```bash
cat > .skip-opt_security_audit << EOF
Reason: Internal tool with no sensitive data
Risk Level: Low
Date: $(date)
Reviewed by: [name]
EOF
```

### 2. **Revisit Decisions**
As projects evolve, revisit optional stages:
- Prototype → Production: Add security, monitoring
- Internal → External: Add API design, security
- Low traffic → High traffic: Add performance baseline

### 3. **Use Quick Checks**
Even when skipping, use quick checks:
- 5-minute security scan
- Basic performance test
- Simple integration verification

### 4. **Gradual Implementation**
Start minimal, add depth as needed:
1. Skip initially for MVP
2. Add basic implementation for beta
3. Full implementation for production

## Stage Selection Guide

| Project Type | Required Stages | Recommended Optional | Can Skip |
|--------------|-----------------|---------------------|----------|
| Prototype | All required | None | All optional |
| Internal Tool | All required | opt_integration_test | Rest |
| Public API | All required | opt_api_design, opt_security_audit | Monitoring (initially) |
| Enterprise App | All required | All optional stages | None |
| Microservice | All required | integration, monitoring, api | Performance (initially) |
| High-Traffic | All required | performance, monitoring, security | Release (if CD) |

## Command Examples

### Skip with Documentation
```bash
./run_stage.sh /project --stage opt_security_audit --skip-reason "Internal prototype"
```

### Minimal Implementation
```bash
./run_stage.sh /project --stage opt_performance_baseline --minimal
```

### Full Implementation
```bash
./run_stage.sh /project --stage opt_security_audit --full
```

## Benefits

1. **Flexibility**: Adapt to project needs
2. **Efficiency**: Skip unnecessary work
3. **Documentation**: Clear record of decisions
4. **Scalability**: Start simple, add complexity
5. **Risk Management**: Match effort to risk level

## Conclusion

The optional stages system allows teams to maintain high standards for production systems while enabling rapid development for prototypes and internal tools. By making informed decisions about which stages to include, teams can optimize their development workflow for their specific needs.