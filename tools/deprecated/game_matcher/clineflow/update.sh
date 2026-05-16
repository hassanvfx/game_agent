#!/bin/bash

# ClineFlow Update Script
# Updates ClineFlow template files while preserving user customizations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub repository
REPO_URL="https://raw.githubusercontent.com/hassanvfx/clineflow/main"

# Files that get updated (template files)
TEMPLATE_FILES=(
    "clineflow/PROCEDURES.md"
    "clineflow/JOURNAL_TEMPLATE.md"
    "clineflow/WORKING_WITH_CLINE.md"
    "clineflow/README.md"
    "setup-refs.sh"
    ".clineflow.example"
    "VERSION"
)

# Files that are NEVER updated (user files)
PROTECTED_FILES=(
    ".clinerules"
    ".clineflow.local"
    "docs/journals/*"
)

DRY_RUN=false
SKIP_CONFIRMATION=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --yes|-y)
            SKIP_CONFIRMATION=true
            shift
            ;;
        --help|-h)
            echo "ClineFlow Update Script"
            echo ""
            echo "Usage: ./update.sh [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run     Show what would be updated without making changes"
            echo "  --yes, -y     Skip confirmation prompt"
            echo "  --help, -h    Show this help message"
            echo ""
            echo "What gets updated:"
            echo "  - clineflow/* documentation files"
            echo "  - setup-refs.sh script"
            echo "  - .clineflow.example config template"
            echo ""
            echo "What stays protected:"
            echo "  - .clinerules (your custom rules)"
            echo "  - .clineflow.local (your local config)"
            echo "  - docs/journals/* (your task journals)"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ClineFlow Update                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if ClineFlow is installed
if [ ! -d "clineflow" ]; then
    echo -e "${RED}Error: ClineFlow not found in current directory${NC}"
    echo "Please run this script from a directory with ClineFlow installed"
    exit 1
fi

# Fetch current version if it exists
CURRENT_VERSION="unknown"
if [ -f "VERSION" ]; then
    CURRENT_VERSION=$(cat VERSION)
fi

echo -e "${BLUE}Current version:${NC} $CURRENT_VERSION"
echo ""

# Check what would be updated
echo -e "${YELLOW}Checking for updates...${NC}"
echo ""

UPDATES_AVAILABLE=()
for file in "${TEMPLATE_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Download to temp file
        TEMP_FILE=$(mktemp)
        if curl -fsSL "$REPO_URL/template/$file" -o "$TEMP_FILE" 2>/dev/null; then
            # Compare files
            if ! cmp -s "$file" "$TEMP_FILE" 2>/dev/null; then
                UPDATES_AVAILABLE+=("$file")
                echo -e "  ${GREEN}✓${NC} $file - update available"
            else
                echo -e "  ${BLUE}•${NC} $file - already up to date"
            fi
            rm "$TEMP_FILE"
        else
            echo -e "  ${YELLOW}⚠${NC} $file - could not check (network issue?)"
        fi
    else
        # File doesn't exist locally - would be created
        UPDATES_AVAILABLE+=("$file")
        echo -e "  ${GREEN}+${NC} $file - will be created"
    fi
done

echo ""

# Check if any updates available
if [ ${#UPDATES_AVAILABLE[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ ClineFlow is already up to date!${NC}"
    exit 0
fi

echo -e "${GREEN}${#UPDATES_AVAILABLE[@]} file(s) will be updated${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Dry run complete. No files were modified.${NC}"
    exit 0
fi

# Confirm with user
if [ "$SKIP_CONFIRMATION" = false ]; then
    echo -e "${YELLOW}⚠ This will update the files listed above${NC}"
    echo -e "${BLUE}Protected files (will NOT be touched):${NC}"
    for pfile in "${PROTECTED_FILES[@]}"; do
        echo "  • $pfile"
    done
    echo ""
    read -p "Continue with update? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Update cancelled"
        exit 0
    fi
fi

# Perform updates
echo ""
echo -e "${BLUE}Updating files...${NC}"
echo ""

UPDATED_COUNT=0
FAILED_COUNT=0

for file in "${UPDATES_AVAILABLE[@]}"; do
    # Create directory if needed
    mkdir -p "$(dirname "$file")"
    
    # Download file
    if curl -fsSL "$REPO_URL/template/$file" -o "$file" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Updated $file"
        UPDATED_COUNT=$((UPDATED_COUNT + 1))
    else
        echo -e "  ${RED}✗${NC} Failed to update $file"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
done

# Make setup-refs.sh executable if it was updated
if [[ " ${UPDATES_AVAILABLE[@]} " =~ " setup-refs.sh " ]]; then
    chmod +x setup-refs.sh
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"

if [ $FAILED_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ Update complete!${NC}"
    echo ""
    echo -e "${GREEN}Updated: $UPDATED_COUNT file(s)${NC}"
    if [ -f "VERSION" ]; then
        echo -e "${BLUE}Version: $(cat VERSION)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Update completed with warnings${NC}"
    echo ""
    echo -e "${GREEN}Updated: $UPDATED_COUNT file(s)${NC}"
    echo -e "${RED}Failed: $FAILED_COUNT file(s)${NC}"
fi

echo ""
echo -e "${BLUE}Your customizations are safe:${NC}"
echo "  • .clinerules preserved"
echo "  • .clineflow.local preserved"
echo "  • All journals in docs/journals/ preserved"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  • Review updated files for any breaking changes"
echo "  • Check CHANGELOG.md for update notes (if available)"
echo "  • Continue your work!"
echo ""
