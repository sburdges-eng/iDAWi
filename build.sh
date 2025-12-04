#!/usr/bin/env bash
#
# iDAWi Build Script for Linux/macOS
# Usage: ./build.sh [command] [options]
#
# Commands:
#   all        - Build everything (default)
#   cpp        - Build C++ components only
#   python     - Install Python packages only
#   test       - Run all tests
#   clean      - Clean build artifacts
#   help       - Show this help message
#
# Options:
#   --release  - Build in release mode (default: debug)
#   --simd     - Enable SIMD optimizations
#   --parallel - Number of parallel jobs (default: auto-detect)
#   --no-tests - Skip tests after build
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
BUILD_TYPE="Debug"
ENABLE_SIMD="OFF"
RUN_TESTS="ON"
PARALLEL_JOBS=""

# Detect number of CPU cores
detect_parallel_jobs() {
    if [[ -z "$PARALLEL_JOBS" ]]; then
        if [[ "$(uname)" == "Darwin" ]]; then
            PARALLEL_JOBS=$(sysctl -n hw.ncpu)
        else
            PARALLEL_JOBS=$(nproc)
        fi
    fi
}

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

print_step() {
    print_msg "$BLUE" "===> $1"
}

print_success() {
    print_msg "$GREEN" "[OK] $1"
}

print_warning() {
    print_msg "$YELLOW" "[WARN] $1"
}

print_error() {
    print_msg "$RED" "[ERROR] $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."

    local missing=()

    # Check for CMake
    if ! command -v cmake &> /dev/null; then
        missing+=("cmake")
    else
        local cmake_version=$(cmake --version | head -1 | grep -oE '[0-9]+\.[0-9]+')
        print_success "CMake found: $(cmake --version | head -1)"
    fi

    # Check for C++ compiler
    if command -v clang++ &> /dev/null; then
        print_success "Clang++ found: $(clang++ --version | head -1)"
    elif command -v g++ &> /dev/null; then
        print_success "G++ found: $(g++ --version | head -1)"
    else
        missing+=("c++ compiler (clang++ or g++)")
    fi

    # Check for Python
    if command -v python3 &> /dev/null; then
        print_success "Python3 found: $(python3 --version)"
    else
        missing+=("python3")
    fi

    # Check for pip
    if command -v pip3 &> /dev/null || python3 -m pip --version &> /dev/null; then
        print_success "pip found"
    else
        missing+=("pip")
    fi

    # Check for ninja (optional but preferred)
    if command -v ninja &> /dev/null; then
        print_success "Ninja found: $(ninja --version)"
        CMAKE_GENERATOR="Ninja"
    else
        print_warning "Ninja not found, using default generator (Make)"
        CMAKE_GENERATOR=""
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "Missing prerequisites: ${missing[*]}"
        echo ""
        echo "Please install the missing tools:"
        echo "  Ubuntu/Debian: sudo apt install cmake build-essential python3 python3-pip ninja-build"
        echo "  macOS:         brew install cmake python ninja"
        echo "  Fedora:        sudo dnf install cmake gcc-c++ python3 python3-pip ninja-build"
        exit 1
    fi

    print_success "All prerequisites satisfied"
}

# Build C++ components
build_cpp() {
    print_step "Building C++ components..."

    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"

    local cmake_args=(
        -DCMAKE_BUILD_TYPE="$BUILD_TYPE"
        -DPENTA_ENABLE_SIMD="$ENABLE_SIMD"
        -DPENTA_BUILD_TESTS="$RUN_TESTS"
        -DPENTA_BUILD_PYTHON_BINDINGS=ON
    )

    if [[ -n "$CMAKE_GENERATOR" ]]; then
        cmake_args+=(-G "$CMAKE_GENERATOR")
    fi

    print_msg "$BLUE" "CMake configuration: ${cmake_args[*]}"

    cmake "${cmake_args[@]}" "${SCRIPT_DIR}/penta-core"

    detect_parallel_jobs
    cmake --build . -j "$PARALLEL_JOBS"

    cd "$SCRIPT_DIR"
    print_success "C++ build complete"
}

# Install Python packages
build_python() {
    print_step "Installing Python packages..."

    # Install DAiW-Music-Brain
    if [[ -d "${SCRIPT_DIR}/DAiW-Music-Brain" ]]; then
        print_msg "$BLUE" "Installing DAiW-Music-Brain..."
        pip3 install -e "${SCRIPT_DIR}/DAiW-Music-Brain[audio,theory]" --quiet
        print_success "DAiW-Music-Brain installed"
    fi

    # Install penta-core Python bindings
    if [[ -d "${SCRIPT_DIR}/penta-core" ]]; then
        print_msg "$BLUE" "Installing penta-core..."
        pip3 install -e "${SCRIPT_DIR}/penta-core[dev]" --quiet
        print_success "penta-core installed"
    fi

    print_success "Python packages installed"
}

# Run tests
run_tests() {
    print_step "Running tests..."

    local failed=0

    # Run C++ tests
    if [[ -d "$BUILD_DIR" ]]; then
        print_msg "$BLUE" "Running C++ tests..."
        cd "$BUILD_DIR"
        if ctest --output-on-failure; then
            print_success "C++ tests passed"
        else
            print_error "C++ tests failed"
            failed=1
        fi
        cd "$SCRIPT_DIR"
    fi

    # Run Python tests
    print_msg "$BLUE" "Running Python tests..."

    if [[ -d "${SCRIPT_DIR}/DAiW-Music-Brain/tests" ]]; then
        if python3 -m pytest "${SCRIPT_DIR}/DAiW-Music-Brain/tests" -v --tb=short; then
            print_success "DAiW-Music-Brain tests passed"
        else
            print_error "DAiW-Music-Brain tests failed"
            failed=1
        fi
    fi

    if [[ -d "${SCRIPT_DIR}/penta-core/tests" ]]; then
        if python3 -m pytest "${SCRIPT_DIR}/penta-core/tests" -v --tb=short 2>/dev/null; then
            print_success "penta-core Python tests passed"
        else
            print_warning "penta-core Python tests not found or failed"
        fi
    fi

    if [[ $failed -eq 0 ]]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed"
        exit 1
    fi
}

# Clean build artifacts
clean_build() {
    print_step "Cleaning build artifacts..."

    rm -rf "$BUILD_DIR"
    find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$SCRIPT_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find "$SCRIPT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

    print_success "Clean complete"
}

# Show help
show_help() {
    head -25 "$0" | tail -22 | sed 's/^#//'
}

# Parse arguments
parse_args() {
    COMMAND="${1:-all}"
    shift || true

    while [[ $# -gt 0 ]]; do
        case $1 in
            --release)
                BUILD_TYPE="Release"
                shift
                ;;
            --simd)
                ENABLE_SIMD="ON"
                shift
                ;;
            --parallel)
                PARALLEL_JOBS="$2"
                shift 2
                ;;
            --no-tests)
                RUN_TESTS="OFF"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Main
main() {
    parse_args "$@"

    echo ""
    print_msg "$GREEN" "=========================================="
    print_msg "$GREEN" "  iDAWi Build System"
    print_msg "$GREEN" "=========================================="
    echo ""
    print_msg "$BLUE" "Build type: $BUILD_TYPE"
    print_msg "$BLUE" "SIMD: $ENABLE_SIMD"
    print_msg "$BLUE" "Tests: $RUN_TESTS"
    echo ""

    case $COMMAND in
        all)
            check_prerequisites
            build_cpp
            build_python
            if [[ "$RUN_TESTS" == "ON" ]]; then
                run_tests
            fi
            ;;
        cpp)
            check_prerequisites
            build_cpp
            ;;
        python)
            build_python
            ;;
        test)
            run_tests
            ;;
        clean)
            clean_build
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac

    echo ""
    print_success "Build completed successfully!"
}

main "$@"
