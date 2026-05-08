#!/bin/bash
# ClineFlow Installation & Git Safety Test Suite
# Tests complete installation flow with mock repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_URL="https://raw.githubusercontent.com/hassanvfx/clineflow/main/install.sh"
TEST_DIR=""
VERBOSE=false
NO_CLEANUP=false
FAILED=0
PASSED=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --no-cleanup)
            NO_CLEANUP=true
            shift
            ;;
        --help|-h)
            echo "ClineFlow Test Suite"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v     Show detailed output"
            echo "  --no-cleanup      Keep test environment after completion"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Helper function for verbose output
verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}    [VERBOSE] $1${NC}"
    fi
}

# Test result tracking
pass_test() {
    echo -e "${GREEN}  ✅ $1${NC}"
    PASSED=$((PASSED + 1))
}

fail_test() {
    echo -e "${RED}  ❌ $1${NC}"
    FAILED=$((FAILED + 1))
}

warn_test() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

# Cleanup function
cleanup() {
    if [ "$NO_CLEANUP" = true ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Test environment preserved at: $TEST_DIR${NC}"
        return
    fi
    
    if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
        verbose "Cleaning up test environment: $TEST_DIR"
        rm -rf "$TEST_DIR"
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Phase 1: Create test environment
create_test_environment() {
    echo ""
    echo -e "${BLUE}📦 Phase 1: Environment Setup${NC}"
    
    # Create unique test directory
    TEST_DIR=$(mktemp -d /tmp/clineflow-test-XXXXXX)
    verbose "Created test directory: $TEST_DIR"
    
    # Create test project directory
    mkdir -p "$TEST_DIR/test-project"
    cd "$TEST_DIR/test-project"
    git init > /dev/null 2>&1
    git config user.name "Test User" > /dev/null 2>&1
    git config user.email "test@example.com" > /dev/null 2>&1
    pass_test "Created test project directory"
    
    # Create mock repositories
    create_mock_repository "mock-backend-api" "Backend API"
    create_mock_repository "mock-frontend-app" "Frontend App"
    
    pass_test "Created 2 mock repositories"
}

# Helper to create mock repository
create_mock_repository() {
    local repo_name=$1
    local repo_desc=$2
    
    verbose "Creating mock repository: $repo_name"
    
    mkdir -p "$TEST_DIR/$repo_name"
    cd "$TEST_DIR/$repo_name"
    
    # Initialize git
    git init > /dev/null 2>&1
    git config user.name "Test User" > /dev/null 2>&1
    git config user.email "test@example.com" > /dev/null 2>&1
    
    # Create realistic file structure
    echo "# $repo_desc" > README.md
    mkdir -p src docs
    echo "console.log('$repo_name');" > src/index.js
    echo "# Documentation" > docs/API.md
    
    # Create git history
    git add . > /dev/null 2>&1
    git commit -m "Initial commit" > /dev/null 2>&1
    
    verbose "  Created files and git history for $repo_name"
}

# Phase 2: Run ClineFlow installation
run_installation() {
    echo ""
    echo -e "${BLUE}📥 Phase 2: ClineFlow Installation${NC}"
    
    cd "$TEST_DIR/test-project"
    
    # Download install script
    verbose "Downloading install script from: $INSTALL_URL"
    if curl -fsSL "$INSTALL_URL" -o install.sh 2>&1 | grep -q "error"; then
        fail_test "Failed to download install script"
        return 1
    fi
    pass_test "Downloaded install script from GitHub"
    
    # Make executable
    chmod +x install.sh
    
    # Run installation (suppress output unless verbose)
    verbose "Running installation..."
    if [ "$VERBOSE" = true ]; then
        bash install.sh
    else
        bash install.sh > /dev/null 2>&1
    fi
    
    pass_test "Installation completed successfully"
    
    # Verify files were created
    if [ -f .clinerules ] && [ -d clineflow ] && [ -d docs/journals ]; then
        pass_test "All files created in correct locations"
    else
        fail_test "Missing expected files after installation"
        return 1
    fi
}

# Phase 3: Setup reference system
setup_reference_system() {
    echo ""
    echo -e "${BLUE}🔗 Phase 3: Reference System Setup${NC}"
    
    cd "$TEST_DIR/test-project"
    
    # Create .clineflow.local configuration
    verbose "Creating .clineflow.local configuration"
    cat > .clineflow.local << EOF
# ClineFlow Reference System Configuration
# Test configuration with mock repositories

MOCK_BACKEND_API_PATH="$TEST_DIR/mock-backend-api"
MOCK_FRONTEND_APP_PATH="$TEST_DIR/mock-frontend-app"
EOF
    
    pass_test "Configured .clineflow.local with mock paths"
    
    # Run setup-refs.sh
    verbose "Running setup-refs.sh"
    if [ "$VERBOSE" = true ]; then
        bash setup-refs.sh
    else
        bash setup-refs.sh > /dev/null 2>&1
    fi
    
    pass_test "Ran setup-refs.sh successfully"
    
    # Verify symlinks were created
    if [ -L clineflow/mock-backend-api ] && [ -L clineflow/mock-frontend-app ]; then
        pass_test "Created 2 symlinks"
    else
        fail_test "Symlinks were not created"
        return 1
    fi
}

# Phase 4: Test git safety features
test_git_safety() {
    echo ""
    echo -e "${BLUE}🔒 Phase 4: Git Safety Verification${NC}"
    
    cd "$TEST_DIR/test-project"
    
    # Test 1: Symlinks exist and are valid
    if [ -L clineflow/mock-backend-api ] && [ -d clineflow/mock-backend-api ]; then
        pass_test "Symlinks exist and are valid"
    else
        fail_test "Symlinks are broken or missing"
    fi
    
    # Test 2: .git/info/exclude configured
    if grep -q "# ClineFlow reference symlinks" .git/info/exclude 2>/dev/null; then
        pass_test ".git/info/exclude configured correctly"
    else
        fail_test ".git/info/exclude not configured"
    fi
    
    # Test 3: Symlinks visible via ls
    if ls -la clineflow/ | grep -q "mock-backend-api"; then
        pass_test "Symlinks visible via ls/VSCode"
    else
        fail_test "Symlinks not visible in directory listing"
    fi
    
    # Test 4: Git status doesn't show symlinks
    git add .clinerules clineflow/*.md docs/ > /dev/null 2>&1
    if ! git status --porcelain | grep -q "clineflow/mock"; then
        pass_test "git status shows clean (no symlinks)"
    else
        fail_test "git status shows symlinks (they should be excluded)"
    fi
    
    # Test 5: Staged symlink warning
    verbose "Testing staged symlink warning..."
    # Try to stage a symlink manually
    git add clineflow/mock-backend-api > /dev/null 2>&1 || true
    # Run setup-refs.sh again to trigger warning check
    if bash setup-refs.sh 2>&1 | grep -q "WARNING.*Symlinks detected"; then
        warn_test "Staged symlink warning triggered (expected)"
        # Unstage for next tests
        git reset HEAD clineflow/mock-backend-api > /dev/null 2>&1 || true
    else
        # This is actually OK if git auto-excluded it
        verbose "Symlink auto-excluded by git (also correct behavior)"
    fi
    
    # Test 6: Idempotency - run setup again
    verbose "Testing idempotency - running setup-refs.sh again"
    if [ "$VERBOSE" = true ]; then
        bash setup-refs.sh
    else
        bash setup-refs.sh > /dev/null 2>&1
    fi
    
    if [ -L clineflow/mock-backend-api ]; then
        pass_test "Idempotency: Second run successful"
    else
        fail_test "Idempotency: Second run broke symlinks"
    fi
}

# Phase 5: Test file access
test_file_access() {
    echo ""
    echo -e "${BLUE}📚 Phase 5: Reference Access${NC}"
    
    cd "$TEST_DIR/test-project"
    
    # Test reading through symlink
    if [ -f clineflow/mock-backend-api/README.md ]; then
        if grep -q "Backend API" clineflow/mock-backend-api/README.md; then
            pass_test "Can read mock-backend-api/README.md"
        else
            fail_test "Can read file but content is wrong"
        fi
    else
        fail_test "Cannot access mock-backend-api/README.md"
    fi
    
    if [ -f clineflow/mock-frontend-app/src/index.js ]; then
        if grep -q "mock-frontend-app" clineflow/mock-frontend-app/src/index.js; then
            pass_test "Can read mock-frontend-app/src/index.js"
        else
            fail_test "Can read file but content is wrong"
        fi
    else
        fail_test "Cannot access mock-frontend-app/src/index.js"
    fi
}

# Generate final report
generate_report() {
    local total=$((PASSED + FAILED))
    local duration=$SECONDS
    
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All $PASSED tests passed!${NC}"
    else
        echo -e "${RED}❌ $FAILED test(s) failed, $PASSED passed${NC}"
    fi
    
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}📊 Test Summary:${NC}"
    echo -e "   Duration: ${duration} seconds"
    echo -e "   Tests: $PASSED passed, $FAILED failed"
    echo -e "   Environment: $TEST_DIR"
    
    if [ "$NO_CLEANUP" = false ]; then
        echo -e "   Cleaned up: ✅"
    else
        echo -e "   Cleaned up: ⚠️  Preserved for debugging"
    fi
    
    echo ""
    
    # Return appropriate exit code
    if [ $FAILED -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🧪 ClineFlow Installation & Git Safety Test Suite${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    
    # Track execution time
    SECONDS=0
    
    # Run test phases
    create_test_environment
    run_installation
    setup_reference_system
    test_git_safety
    test_file_access
    
    # Generate report and exit with appropriate code
    generate_report
}

# Run main function
main
