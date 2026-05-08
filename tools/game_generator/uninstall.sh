#!/bin/bash
# ClineFlow Uninstaller
# https://github.com/hassanvfx/clineflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script version
VERSION="1.0.0"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to show what will be removed
show_removal_list() {
    echo -e "${YELLOW}The following will be removed:${NC}"
    echo ""
    
    echo "  ${BLUE}Agent Configuration Files:${NC}"
    [ -f .clinerules ] && echo "    • .clinerules (Cline)"
    [ -f AGENTS.md ] && echo "    • AGENTS.md (Cursor, Copilot)"
    [ -f .github/copilot-instructions.md ] && echo "    • .github/copilot-instructions.md (GitHub Copilot)"
    [ -f .windsurf/rules/clineflow.md ] && echo "    • .windsurf/rules/clineflow.md (Windsurf)"
    
    echo ""
    echo "  ${BLUE}Workflow Files:${NC}"
    [ -d clineflow ] && echo "    • clineflow/ (including any reference symlinks)"
    [ -f setup-refs.sh ] && echo "    • setup-refs.sh"
    [ -f .clineflow.example ] && echo "    • .clineflow.example"
    [ -f .clineflow.local ] && echo "    • .clineflow.local"
    [ -f .github/workflows/test.yml ] && echo "    • .github/workflows/test.yml (CI/CD workflow)"
    
    echo ""
    echo -e "${GREEN}The following will be PRESERVED:${NC}"
    echo "  • docs/journals/ (your task journals are safe)"
    [ -d .github/workflows ] && [ "$(ls -A .github/workflows 2>/dev/null | grep -v test.yml | wc -l)" -gt 0 ] && echo "  • .github/workflows/ (your other workflows)"
    [ -d .github ] && [ -f .github/copilot-instructions.md ] && [ "$(ls -A .github 2>/dev/null | grep -v copilot-instructions.md | wc -l)" -gt 0 ] && echo "  • .github/ (your other GitHub files)"
    [ -d .windsurf ] && [ -f .windsurf/rules/clineflow.md ] && [ "$(find .windsurf -type f ! -path '.windsurf/rules/clineflow.md' | wc -l)" -gt 0 ] && echo "  • .windsurf/ (your other Windsurf configurations)"
    echo ""
}

# Function to clean reference symlinks
clean_refs() {
    if [ -f setup-refs.sh ]; then
        print_info "Cleaning reference symlinks..."
        if bash setup-refs.sh --clean 2>/dev/null; then
            print_success "Reference symlinks cleaned"
        else
            print_warning "Could not clean reference symlinks (continuing anyway)"
        fi
    fi
}

# Function to remove files
remove_files() {
    local removed_count=0
    
    print_info "Removing ClineFlow files..."
    echo ""
    
    # Remove agent configuration files
    print_info "Removing agent configuration files..."
    
    # Remove .clinerules (Cline)
    if [ -f .clinerules ]; then
        rm -f .clinerules
        print_success "Removed .clinerules (Cline)"
        removed_count=$((removed_count + 1))
    fi
    
    # Remove AGENTS.md (Cursor, Copilot, universal)
    if [ -f AGENTS.md ]; then
        rm -f AGENTS.md
        print_success "Removed AGENTS.md (Cursor, Copilot)"
        removed_count=$((removed_count + 1))
    fi
    
    # Remove .github/copilot-instructions.md (GitHub Copilot)
    if [ -f .github/copilot-instructions.md ]; then
        rm -f .github/copilot-instructions.md
        print_success "Removed .github/copilot-instructions.md (GitHub Copilot)"
        removed_count=$((removed_count + 1))
    fi
    
    # Remove .windsurf/rules/clineflow.md (Windsurf)
    if [ -f .windsurf/rules/clineflow.md ]; then
        rm -f .windsurf/rules/clineflow.md
        print_success "Removed .windsurf/rules/clineflow.md (Windsurf)"
        removed_count=$((removed_count + 1))
        
        # Remove .windsurf/rules directory if now empty
        if [ -d .windsurf/rules ] && [ -z "$(ls -A .windsurf/rules 2>/dev/null)" ]; then
            rmdir .windsurf/rules
            print_success "Removed empty .windsurf/rules/"
        fi
        
        # Remove .windsurf directory if now empty
        if [ -d .windsurf ] && [ -z "$(ls -A .windsurf 2>/dev/null)" ]; then
            rmdir .windsurf
            print_success "Removed empty .windsurf/"
        fi
    fi
    
    echo ""
    print_info "Removing workflow files..."
    
    # Remove clineflow directory
    if [ -d clineflow ]; then
        rm -rf clineflow
        print_success "Removed clineflow/"
        removed_count=$((removed_count + 1))
    fi
    
    # Remove setup-refs.sh
    if [ -f setup-refs.sh ]; then
        rm -f setup-refs.sh
        print_success "Removed setup-refs.sh"
        removed_count=$((removed_count + 1))
    fi
    
    # Remove .clineflow.example
    if [ -f .clineflow.example ]; then
        rm -f .clineflow.example
        print_success "Removed .clineflow.example"
        removed_count=$((removed_count + 1))
    fi
    
    # Remove .clineflow.local if exists
    if [ -f .clineflow.local ]; then
        rm -f .clineflow.local
        print_success "Removed .clineflow.local"
        removed_count=$((removed_count + 1))
    fi
    
    # Remove GitHub Actions workflow (only our specific file)
    if [ -f .github/workflows/test.yml ]; then
        rm -f .github/workflows/test.yml
        print_success "Removed .github/workflows/test.yml"
        removed_count=$((removed_count + 1))
        
        # Remove .github/workflows directory if now empty
        if [ -d .github/workflows ] && [ -z "$(ls -A .github/workflows 2>/dev/null)" ]; then
            rmdir .github/workflows
            print_success "Removed empty .github/workflows/"
            
            # Remove .github directory if now empty
            if [ -d .github ] && [ -z "$(ls -A .github 2>/dev/null)" ]; then
                rmdir .github
                print_success "Removed empty .github/"
            fi
        fi
    fi
    
    echo ""
    return $removed_count
}

# Function to show help
show_help() {
    echo "ClineFlow Uninstaller"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --dry-run      Preview what would be removed without removing"
    echo "  --yes, -y      Skip confirmation prompt"
    echo "  --version      Show version"
    echo "  --help, -h     Show this help message"
    echo ""
    exit 0
}

# Parse command line arguments
DRY_RUN=false
SKIP_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --yes|-y)
            SKIP_CONFIRM=true
            shift
            ;;
        --version)
            echo "ClineFlow Uninstaller v${VERSION}"
            exit 0
            ;;
        --help|-h)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main uninstall flow
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "   ClineFlow Uninstaller v${VERSION}"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Show what will be removed
show_removal_list

# Dry run mode
if [ "$DRY_RUN" = true ]; then
    print_info "DRY RUN MODE - No files will be removed"
    echo ""
    exit 0
fi

# Check if anything to remove
if [ ! -f .clinerules ] && [ ! -f AGENTS.md ] && [ ! -f .github/copilot-instructions.md ] && [ ! -f .windsurf/rules/clineflow.md ] && [ ! -d clineflow ] && [ ! -f setup-refs.sh ] && [ ! -f .clineflow.example ] && [ ! -f .clineflow.local ]; then
    print_warning "No ClineFlow files found to remove"
    exit 0
fi

# Confirmation prompt
if [ "$SKIP_CONFIRM" = false ]; then
    echo -e "${YELLOW}⚠ Are you sure you want to remove ClineFlow?${NC}"
    read -p "Type 'yes' to confirm: " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Uninstall cancelled"
        exit 0
    fi
fi

# Clean reference symlinks first
clean_refs

echo ""

# Remove files
remove_files
removed_count=$?

# Success message
echo ""
echo "═══════════════════════════════════════════════════════════"
if [ $removed_count -gt 0 ]; then
    echo -e "${GREEN}✓ Uninstall complete! Removed $removed_count item(s)${NC}"
else
    echo -e "${YELLOW}⚠ No files were removed${NC}"
fi
echo "═══════════════════════════════════════════════════════════"
echo ""

# Reminder about journals
if [ -d docs/journals ]; then
    echo -e "${BLUE}📚 Note: Your journals are preserved in docs/journals/${NC}"
    echo -e "${BLUE}   Remove manually if desired:${NC} rm -rf docs/journals/"
    echo ""
fi

print_success "ClineFlow has been uninstalled"
echo ""
