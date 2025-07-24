# Add/Change Check Stage - Overview

## Purpose

The `addchange_check` stage is a critical quality gate introduced between the `code_debug` and `deploy_test` stages. It enforces disciplined change management through GitHub pull request workflows, ensuring code quality, reviewability, and rollback capabilities.

## Why This Stage Matters

After debugging and optimization in the `code_debug` stage, code is functionally correct but may still pose risks when deployed. The `addchange_check` stage provides:

1. **Protection**: Prevents accidental or unreviewed changes to production code
2. **Visibility**: All changes are documented and reviewed
3. **Reversibility**: Every change can be safely rolled back
4. **Quality**: Enforces code review and automated testing
5. **Collaboration**: Facilitates knowledge sharing across the team

## Key Components

### 1. Branch Protection Rules
```yaml
Main Branch Protection:
  - Require pull request reviews: ✓
  - Required approving reviews: 1-2
  - Dismiss stale PR approvals: ✓
  - Require status checks: ✓
  - Require branches up to date: ✓
  - Include administrators: ✓
  - Restrict force pushes: ✓
```

### 2. Pull Request Template
Every PR must include:
- Description of changes
- Type of change (feature/bugfix/refactor)
- Testing checklist
- Rollback plan
- Related issues
- Screenshots (if UI changes)

### 3. Automated CI/CD Checks
```yaml
Required Checks:
  - Unit Tests: Must pass 100%
  - Integration Tests: Must pass
  - Linting: No errors allowed
  - Security Scan: No vulnerabilities
  - Build: Must complete successfully
  - Code Coverage: Must not decrease
```

### 4. Change Organization
Changes are organized into logical, reviewable units:
- **Feature branches**: New functionality
- **Bugfix branches**: Issue corrections
- **Refactor branches**: Code improvements
- **Hotfix branches**: Emergency fixes
- **Chore branches**: Maintenance tasks

## Workflow Example

```bash
# 1. Create feature branch
git checkout -b feature/add-user-notifications

# 2. Make changes with atomic commits
git add src/notifications/
git commit -m "feat: add notification service"

git add tests/notifications/
git commit -m "test: add notification service tests"

# 3. Push branch
git push -u origin feature/add-user-notifications

# 4. Create pull request
gh pr create --title "Add user notification system" \
             --body "$(cat .github/pull_request_template.md)"

# 5. Address review feedback
git add src/notifications/email.js
git commit -m "fix: address review comments on email handling"
git push

# 6. Merge after approval
# (Automated via GitHub when all checks pass)
```

## Rollback Strategies

### 1. GitHub PR Revert
- One-click revert through GitHub UI
- Creates a new PR that undoes changes
- Maintains full audit trail

### 2. Git Revert
```bash
git revert -m 1 <merge-commit-hash>
git push origin main
```

### 3. Feature Flags
```javascript
if (featureFlags.isEnabled('user-notifications')) {
  // New feature code
} else {
  // Previous behavior
}
```

### 4. Database Rollbacks
```bash
# Revert last migration
npm run db:rollback
# or
./manage.py migrate app_name previous_migration_name
```

## Review Document Contents

The stage creates a comprehensive review document including:

1. **Branch Protection Status**
   - Configuration verification
   - Rule effectiveness

2. **PR Metrics**
   - Number of PRs created
   - Review turnaround time
   - Changes requested rate
   - Merge success rate

3. **Code Quality Indicators**
   - Average PR size
   - Test coverage trends
   - CI/CD pass rates

4. **Risk Assessment**
   - High-risk changes identified
   - Mitigation strategies
   - Rollback readiness

## Integration with Other Stages

### From Code & Debug
- Takes debugged, optimized code
- Organizes into reviewable changes
- Adds protection layer

### To Deploy & Test
- Provides reviewed, tested code
- Ensures rollback capability
- Documents all changes

## Best Practices

1. **Small, Focused PRs**
   - Easier to review
   - Lower risk
   - Faster approval

2. **Descriptive PR Titles**
   - Clear change summary
   - Follows conventional commits
   - Searchable history

3. **Comprehensive Testing**
   - Test before creating PR
   - Add tests for new features
   - Verify no regressions

4. **Timely Reviews**
   - Respond to feedback quickly
   - Don't let PRs go stale
   - Keep branches up to date

5. **Documentation**
   - Update docs with code
   - Explain complex changes
   - Document rollback steps

## Common Scenarios

### Hotfix Process
```bash
# For critical production issues
git checkout -b hotfix/critical-bug-fix main
# Make minimal fix
git commit -m "hotfix: resolve critical issue"
git push -u origin hotfix/critical-bug-fix
# Create PR with expedited review
```

### Feature Toggle Implementation
```javascript
// Add feature flag before risky deployment
if (config.features.newPaymentSystem) {
  return processPaymentV2(order);
} else {
  return processPaymentV1(order);
}
```

### Breaking Changes
1. Document in PR description
2. Update API version
3. Provide migration guide
4. Coordinate deployment

## Success Metrics

- **Zero** direct commits to main
- **100%** PR compliance
- **<24hr** review turnaround
- **>95%** CI/CD pass rate
- **<5min** rollback time

## Conclusion

The `addchange_check` stage transforms the development workflow from individual coding to collaborative engineering. It provides the safety net needed for continuous deployment while maintaining velocity through automation and clear processes.

By enforcing pull request workflows, the stage ensures that every change is:
- Reviewed by peers
- Tested automatically
- Documented properly
- Reversible if needed

This stage is essential for teams practicing continuous deployment or working on critical systems where stability and rollback capabilities are paramount.