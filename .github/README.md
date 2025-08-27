# CCPM GitHub Actions Workflows

This directory contains GitHub Actions workflows for the CCPM (Cross-Platform Command Project Manager) project.

## Workflows Overview

### 🔄 `ci.yml` - Cross-Platform CI
**Triggers:** Pull Requests, Pushes to main, Manual dispatch
- **Purpose:** Comprehensive testing across Ubuntu, macOS, and Windows
- **Features:**
  - Multi-OS testing matrix
  - Makefile-based test execution
  - Install script validation
  - Automatic PR status comments
  - Test log artifacts
  - Smart change detection

### ⚡ `status-check.yml` - Quick Status Check  
**Triggers:** Pull Requests, Pushes to main
- **Purpose:** Fast validation for required status checks
- **Features:**
  - File existence validation
  - Makefile syntax checking
  - Shell script syntax validation
  - Portable shebang verification
  - Quick system tests

### 🚀 `release-test.yml` - Release Testing
**Triggers:** Release creation, Version tags, Manual dispatch
- **Purpose:** Comprehensive testing for releases
- **Features:**
  - Full test suite execution
  - Installation process validation
  - Release quality assurance
  - Multi-platform release reports

## Setting Up Branch Protection

To enforce passing status checks before merging PRs, configure branch protection rules:

### Required Status Checks

1. **Go to Repository Settings → Branches**
2. **Add or Edit protection rule for `main`/`master`**
3. **Enable "Require status checks to pass before merging"**
4. **Add these required status checks:**
   - `Quick Status Check`
   - `Test on Ubuntu Latest`  
   - `Test on macOS Latest`
   - `Test on Windows Latest`

### Recommended Branch Protection Settings

```yaml
# Example branch protection configuration
Branch: main
Settings:
  ✅ Require a pull request before merging
  ✅ Require approvals: 1
  ✅ Dismiss stale PR approvals when new commits are pushed
  ✅ Require review from code owners (if CODEOWNERS file exists)
  ✅ Require status checks to pass before merging
  ✅ Require branches to be up to date before merging
  ✅ Require conversation resolution before merging
  ✅ Include administrators (recommended for consistency)
```

## Workflow Features

### 🎯 Manual Dispatch Options

The `ci.yml` workflow supports manual execution with options:
- **Test Suite Selection:** `all`, `test-only`, `install-only`
- **Debug Mode:** Enable detailed debugging output

### 📊 Artifacts and Reporting

- **Test Logs:** Automatically uploaded for failed builds
- **PR Comments:** Automatic status updates on pull requests
- **Release Reports:** Detailed testing reports for releases

### 🔍 Smart Change Detection

The CI workflow includes intelligent change detection:
- Skips tests when only documentation changes
- Runs full tests for code/script/config changes
- Always runs on manual dispatch and releases

## Local Testing

Before pushing changes, test locally using the Makefile:

```bash
# Run all tests
make test

# Check system requirements  
make check-system

# Test on current platform
make info

# Test PM functionality
make pm-help
make validate

# Clean up
make clean-all
```

## Debugging Failed Workflows

### 1. Check Workflow Logs
- Go to Actions tab in GitHub
- Click on failed workflow run
- Expand failed job steps

### 2. Download Artifacts
- Test logs are saved as artifacts
- Download and examine for detailed error information

### 3. Manual Reproduction
- Use workflow dispatch with debug enabled
- Run equivalent commands locally using Makefile

### 4. Platform-Specific Issues
Each OS has different considerations:
- **Windows:** PowerShell vs Command Prompt, path separators
- **macOS:** Case-sensitive filesystem, Xcode tools
- **Ubuntu:** Package availability, permissions

## Maintenance

### Updating Runner Versions
Update runner versions in workflow files:
- `ubuntu-latest` → `ubuntu-22.04` (for pinned versions)
- `macos-latest` → `macos-13` (for pinned versions)  
- `windows-latest` → `windows-2022` (for pinned versions)

### Adding New Platforms
To add new platforms (e.g., `ubuntu-20.04`):
1. Update the matrix in `ci.yml`
2. Add platform-specific configuration
3. Update required status checks in branch protection

### Workflow Optimization
- Use caching for dependencies if needed
- Adjust `fail-fast` strategy based on requirements
- Optimize artifact retention periods

## Security Considerations

- Workflows only trigger on specific events
- No secrets exposure in logs
- Limited permissions using `actions/checkout@v4`
- Temporary directories for install testing

## Contributing

When modifying workflows:
1. Test changes in a fork first
2. Use workflow dispatch for testing
3. Update this documentation
4. Verify branch protection rules still work
5. Test across all supported platforms