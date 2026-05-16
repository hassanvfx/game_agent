# ClineFlow Test Suite

Comprehensive end-to-end testing for ClineFlow installation and git safety features.

## 🎯 What Gets Tested

### Installation Flow
- ✅ Download install script from GitHub
- ✅ Execute installation in fresh directory
- ✅ Verify all files created correctly

### Reference System
- ✅ Create mock repositories
- ✅ Configure `.clineflow.local`
- ✅ Run `setup-refs.sh`
- ✅ Verify symlinks created

### Git Safety Features
- ✅ Symlinks visible in filesystem
- ✅ `.git/info/exclude` configured correctly
- ✅ Symlinks excluded from `git status`
- ✅ Warning shown for staged symlinks
- ✅ Idempotency (safe to run multiple times)

### File Access
- ✅ Can reference files via symlinks
- ✅ @ mention pattern works
- ✅ Direct paths work

## 🚀 Quick Start

### Run the Test Suite

```bash
# From the repository root
./tests/test-installation-flow.sh

# Or from tests directory
cd tests
./test-installation-flow.sh
```

### Expected Output

```
🧪 ClineFlow Installation & Git Safety Test Suite
==================================================

📦 Phase 1: Environment Setup
  ✅ Created test project directory
  ✅ Created 2 mock repositories
  ✅ All mock repos have git history

📥 Phase 2: ClineFlow Installation
  ✅ Downloaded install script from GitHub
  ✅ Installation completed successfully
  ✅ All files created in correct locations

🔗 Phase 3: Reference System Setup
  ✅ Configured .clineflow.local with mock paths
  ✅ Ran setup-refs.sh successfully
  ✅ Created 2 symlinks

🔒 Phase 4: Git Safety Verification
  ✅ Symlinks exist and are valid
  ✅ .git/info/exclude configured correctly
  ✅ Symlinks visible via ls/VSCode
  ✅ git status shows clean (no symlinks)
  ⚠️  Staged symlink warning triggered (expected)
  ✅ Idempotency: Second run successful

📚 Phase 5: Reference Access
  ✅ Can read mock-backend-api/README.md
  ✅ Can read mock-frontend-app/src/App.tsx

🎉 All 14 tests passed!

📊 Test Summary:
   Duration: 3.2 seconds
   Tests: 14 passed, 0 failed
   Environment: /tmp/clineflow-test-abc123
   Cleaned up: ✅
```

## 📁 Test Environment

Tests run in isolated temporary directory:
```
/tmp/clineflow-test-XXXXX/
├── test-project/           # Fresh ClineFlow installation
│   ├── .clinerules
│   ├── clineflow/
│   ├── docs/
│   └── .clineflow.local
├── mock-backend-api/       # Mock external repo
│   ├── README.md
│   ├── src/
│   └── .git/
└── mock-frontend-app/      # Mock external repo
    ├── README.md
    ├── src/
    └── .git/
```

**Cleanup:** All test files are automatically removed after tests complete.

## 🐛 Troubleshooting

### Test Fails: "curl: command not found"
Install curl:
```bash
# macOS
brew install curl

# Ubuntu/Debian
sudo apt-get install curl

# Or use wget version (edit script)
```

### Test Fails: "git: command not found"
Install git:
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt-get install git
```

### Tests Hang or Timeout
- Check internet connection (downloads from GitHub)
- Verify `/tmp` directory is writable
- Check disk space

### Manual Cleanup
If test crashes before cleanup:
```bash
# Find test directories
ls -la /tmp/clineflow-test-*

# Remove manually
rm -rf /tmp/clineflow-test-XXXXX
```

## 🔧 Customization

### Test Specific Branch/Commit

Edit `test-installation-flow.sh`:
```bash
# Change this line
INSTALL_URL="https://raw.githubusercontent.com/hassanvfx/clineflow/main/install.sh"

# To test a specific branch
INSTALL_URL="https://raw.githubusercontent.com/hassanvfx/clineflow/feature-branch/install.sh"
```

### Verbose Output

Run with verbose flag:
```bash
./test-installation-flow.sh --verbose
```

### Keep Test Environment

For debugging, keep test files:
```bash
./test-installation-flow.sh --no-cleanup
```

## 📊 CI/CD Integration

### GitHub Actions Example

```yaml
name: Test ClineFlow

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Test Suite
        run: ./tests/test-installation-flow.sh
```

### Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed
- `2` - Test environment setup failed

## 📝 Adding New Tests

To add new test cases, edit `test-installation-flow.sh`:

```bash
# Add to test functions section
test_new_feature() {
    echo "  Testing new feature..."
    
    # Your test logic here
    if [[ condition ]]; then
        echo "    ✅ New feature test passed"
        return 0
    else
        echo "    ❌ New feature test failed"
        return 1
    fi
}

# Add to test execution section
run_tests() {
    test_symlinks_created || FAILED=$((FAILED + 1))
    test_git_exclusion || FAILED=$((FAILED + 1))
    test_new_feature || FAILED=$((FAILED + 1))  # Add here
    # ... other tests
}
```

## 🤝 Contributing

When adding new features to ClineFlow:

1. Add corresponding tests to `test-installation-flow.sh`
2. Update this README if new test scenarios added
3. Run tests locally before submitting PR
4. Ensure all tests pass in CI/CD

## 📚 Related Documentation

- [ClineFlow Main README](../README.md)
- [PROCEDURES.md](../clineflow/PROCEDURES.md)
- [Symlink Git Safety Journal](../docs/journals/symlink-git-safety.md)

---

**Last Updated:** November 9, 2025
