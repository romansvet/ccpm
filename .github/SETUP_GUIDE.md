# GitHub Actions Setup Guide for CCPM

This guide walks through setting up the GitHub Actions workflows and branch protection for the CCPM project.

## 🚀 Quick Setup

### 1. Repository Setup
The workflows are now configured in your repository. After pushing these changes, you'll have:

- **Cross-Platform CI** (`ci.yml`) - Full testing on Ubuntu, macOS, Windows
- **Quick Status Check** (`status-check.yml`) - Fast validation for PRs  
- **Release Testing** (`release-test.yml`) - Comprehensive release validation

### 2. Enable Workflows
1. Push the `.github/` directory to your repository
2. Go to **Actions** tab in GitHub
3. Workflows will be automatically enabled

### 3. Set Up Branch Protection (Recommended)

#### Navigate to Branch Protection Settings
1. Go to **Settings** → **Branches** in your repository
2. Click **Add rule** or edit existing rule for `main`/`master`

#### Configure Required Status Checks
Enable these required status checks:
```
✅ Quick Status Check
✅ Test on Ubuntu Latest  
✅ Test on macOS Latest
✅ Test on Windows Latest
```

#### Recommended Protection Rules
```yaml
Branch name pattern: main
Settings:
  ✅ Require a pull request before merging
  ✅ Require approvals (1 minimum recommended)
  ✅ Dismiss stale PR approvals when new commits are pushed  
  ✅ Require status checks to pass before merging
  ✅ Require branches to be up to date before merging
  ✅ Require conversation resolution before merging
  ✅ Restrict pushes that create files larger than 100MB
```

## 🔧 Workflow Features

### Manual Trigger Options
You can manually run the CI workflow with custom options:

1. Go to **Actions** → **Cross-Platform CI**
2. Click **Run workflow**
3. Choose options:
   - **Test Suite:** `all`, `test-only`, `install-only`
   - **Debug Mode:** Enable for detailed logs

### What Each Workflow Does

#### `ci.yml` - Cross-Platform CI
- **Runs on:** PR creation/updates, pushes to main, manual dispatch
- **Tests:** Full Makefile test suite on all platforms
- **Features:**
  - Smart change detection (skips tests for doc-only changes)
  - Install script validation  
  - Automatic PR status comments
  - Test artifact uploads
  - Debug mode support

#### `status-check.yml` - Quick Status Check
- **Runs on:** PR creation/updates, pushes to main  
- **Tests:** Fast validation checks
- **Features:**
  - File existence validation
  - Makefile syntax checking
  - Shell script syntax validation
  - Portable shebang verification

#### `release-test.yml` - Release Testing  
- **Runs on:** Release creation, version tags, manual dispatch
- **Tests:** Comprehensive release validation
- **Features:**
  - Full test suite execution
  - Installation process validation
  - Release quality reports

## 🧪 Testing the Setup

### Local Testing
Before creating PRs, test locally:
```bash
# Run the same tests as CI
make test

# Check system compatibility
make check-system  

# Validate PM system
make validate

# Test install scripts (simulation)
make info
```

### Testing Workflows
1. **Create a test branch:**
   ```bash
   git checkout -b test-ci-setup
   echo "# Test change" >> README.md
   git add . && git commit -m "test: trigger CI"
   git push origin test-ci-setup
   ```

2. **Create a PR** to trigger the workflows

3. **Check Results** in the Actions tab

## 📊 Understanding Workflow Results

### Success Indicators
- ✅ Green checkmarks next to commit/PR
- Automatic PR comment with success message
- All required status checks passing

### Failure Troubleshooting
- ❌ Red X indicates failure
- Click on failed check for detailed logs
- Download artifacts for test logs
- Use manual dispatch with debug enabled

### Common Issues and Solutions

#### Windows-Specific Issues
```yaml
Issue: Make command not found
Solution: Workflow automatically installs make via chocolatey

Issue: PowerShell vs CMD differences  
Solution: Workflow uses PowerShell (pwsh) consistently
```

#### macOS-Specific Issues
```yaml
Issue: Permission denied on scripts
Solution: Workflow automatically makes scripts executable

Issue: Missing Xcode tools
Solution: GitHub macOS runners include required tools
```

#### Ubuntu-Specific Issues
```yaml
Issue: Missing dependencies
Solution: Workflow installs Python and required tools

Issue: File permissions
Solution: Scripts made executable in workflow
```

## 🔒 Security Considerations

### Workflow Permissions
- Workflows run with minimal required permissions
- No repository secrets exposed in logs  
- Temporary directories used for testing

### Safe Manual Dispatch
- Manual triggers require repository access
- Debug mode only shows sanitized information
- No sensitive data in workflow outputs

## 📈 Monitoring and Maintenance

### Regular Maintenance Tasks
1. **Update runner versions** quarterly
2. **Review workflow efficiency** monthly
3. **Check artifact storage usage** as needed
4. **Update status check requirements** when adding features

### Performance Optimization
- Use caching for dependencies if build times increase
- Adjust matrix strategy based on actual usage
- Monitor artifact storage and adjust retention

### Workflow Updates
When updating workflows:
1. Test in a fork first
2. Use manual dispatch for validation
3. Update documentation  
4. Verify branch protection still works

## 🎯 Next Steps

### For Development Teams
1. **Train team members** on PR workflow
2. **Set up code review process**  
3. **Configure notifications** for workflow failures
4. **Establish merge policies**

### For Repository Maintainers  
1. **Monitor workflow usage** and costs
2. **Review and update** protection rules as needed
3. **Keep workflows** updated with latest actions
4. **Document any custom** setup requirements

## 📞 Support

### Debugging Resources
- **Workflow logs:** Actions tab → failed workflow → job details
- **Local reproduction:** Use identical `make` commands locally
- **Community help:** GitHub Actions community forums

### Common Commands for Troubleshooting
```bash
# Reproduce CI locally
make check-system
make test

# Debug specific components
make test-pm
make pm-help

# Clean and retry
make clean-all
make test
```

This setup ensures your CCPM project maintains high quality across all supported platforms while providing a smooth development experience for contributors! 🚀