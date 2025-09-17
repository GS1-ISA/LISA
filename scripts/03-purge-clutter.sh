#!/bin/bash

# Phase 3: Dead-Code & Clutter Removal Script
# This script safely moves identified clutter files to /tmp/project-trashcan/
# for review before permanent deletion.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Trash directory
TRASH_DIR="/tmp/project-trashcan"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TRASH_SESSION="$TRASH_DIR/session_$TIMESTAMP"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to create trash directory
setup_trash() {
    if [ ! -d "$TRASH_DIR" ]; then
        mkdir -p "$TRASH_DIR"
        print_info "Created trash directory: $TRASH_DIR"
    fi

    mkdir -p "$TRASH_SESSION"
    print_info "Created session directory: $TRASH_SESSION"
}

# Function to confirm action
confirm_action() {
    local message="$1"
    echo -e "${YELLOW}$message${NC}"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Operation cancelled by user."
        exit 0
    fi
}

# Function to safely move file/directory
safe_move() {
    local source="$1"
    local target="$2"

    if [ -e "$source" ]; then
        print_info "Moving: $source -> $target"
        mv "$source" "$target" 2>/dev/null || {
            print_error "Failed to move: $source"
            return 1
        }
        return 0
    else
        print_warning "Source not found: $source"
        return 1
    fi
}

# Function to clean Next.js build cache
clean_nextjs_cache() {
    print_info "Cleaning Next.js build cache..."

    local moved_count=0

    # Move cache files
    if [ -d "frontend/.next/cache" ]; then
        safe_move "frontend/.next/cache" "$TRASH_SESSION/nextjs_cache" && ((moved_count++))
    fi

    # Move server chunks
    if [ -d "frontend/.next/server" ]; then
        safe_move "frontend/.next/server" "$TRASH_SESSION/nextjs_server" && ((moved_count++))
    fi

    print_success "Moved $moved_count Next.js cache directories"
}

# Function to clean macOS metadata files
clean_macos_metadata() {
    print_info "Cleaning macOS metadata files (__MACOSX)..."

    local moved_count=0

    # Find and move all __MACOSX directories
    while IFS= read -r -d '' macos_dir; do
        local relative_path="${macos_dir#./}"
        local target_dir="$TRASH_SESSION/$(dirname "$relative_path")"
        mkdir -p "$target_dir"
        safe_move "$macos_dir" "$target_dir/$(basename "$macos_dir")" && ((moved_count++))
    done < <(find . -type d -name "__MACOSX" -print0 2>/dev/null)

    print_success "Moved $moved_count __MACOSX directories"
}

# Function to clean temporary files
clean_temp_files() {
    print_info "Cleaning temporary files..."

    local moved_count=0

    # Clean temp_unzip directory
    if [ -d "temp_unzip" ]; then
        safe_move "temp_unzip" "$TRASH_SESSION/temp_unzip" && ((moved_count++))
    fi

    # Clean other common temp patterns (be careful here)
    # Add more patterns as needed based on analysis

    print_success "Moved $moved_count temporary directories"
}

# Function to show summary
show_summary() {
    print_info "Cleanup Summary:"
    echo "Trash session: $TRASH_SESSION"
    echo "Total files moved: $(find "$TRASH_SESSION" -type f 2>/dev/null | wc -l)"
    echo "Total size moved: $(du -sh "$TRASH_SESSION" 2>/dev/null | cut -f1)"
    echo ""
    print_warning "Files have been moved to: $TRASH_SESSION"
    print_warning "Review the contents and delete permanently when ready."
    print_info "To restore: mv $TRASH_SESSION/* ./"
}

# Main execution
main() {
    echo "=================================================="
    echo "  Phase 3: Dead-Code & Clutter Removal Script"
    echo "=================================================="
    echo ""

    # Setup
    setup_trash

    # Show what will be cleaned
    echo "This script will clean:"
    echo "1. Next.js build cache (frontend/.next/cache and frontend/.next/server)"
    echo "2. macOS metadata files (__MACOSX directories)"
    echo "3. Temporary files (temp_unzip)"
    echo ""

    # Confirm
    confirm_action "This will move files to $TRASH_SESSION for review. Continue?"

    # Perform cleanup
    clean_nextjs_cache
    clean_macos_metadata
    clean_temp_files

    echo ""
    show_summary

    print_success "Cleanup completed successfully!"
    print_info "You can now review the moved files in: $TRASH_SESSION"
}

# Run main function
main "$@"