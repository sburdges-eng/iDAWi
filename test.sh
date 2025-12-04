#!/usr/bin/env bash
#
# iDAWi Unified Test Runner
# Runs all C++ and Python tests with aggregated results
#
# Usage: ./test.sh [options]
#
# Options:
#   --cpp-only     Run only C++ tests
#   --python-only  Run only Python tests
#   --coverage     Generate coverage report
#   --verbose      Verbose output
#   --fast         Skip slow tests
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"

# Options
RUN_CPP=true
RUN_PYTHON=true
COVERAGE=false
VERBOSE=""
FAST=""

# Results tracking
CPP_PASSED=0
CPP_FAILED=0
PYTHON_PASSED=0
PYTHON_FAILED=0

print_header() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
}

print_result() {
    local name=$1
    local passed=$2
    local failed=$3
    local total=$((passed + failed))

    if [[ $failed -eq 0 ]]; then
        echo -e "${GREEN}  [PASS]${NC} $name: $passed/$total tests passed"
    else
        echo -e "${RED}  [FAIL]${NC} $name: $passed/$total tests passed ($failed failed)"
    fi
}

run_cpp_tests() {
    print_header "C++ Tests (GoogleTest)"

    if [[ ! -d "$BUILD_DIR" ]]; then
        echo -e "${YELLOW}Build directory not found. Run ./build.sh first.${NC}"
        return 1
    fi

    cd "$BUILD_DIR"

    # Run CTest and capture output
    local test_output
    local exit_code=0

    if [[ -n "$VERBOSE" ]]; then
        ctest --output-on-failure -V || exit_code=$?
    else
        test_output=$(ctest --output-on-failure 2>&1) || exit_code=$?
        echo "$test_output"
    fi

    # Parse results
    local passed=$(echo "$test_output" | grep -oE '[0-9]+ tests passed' | grep -oE '[0-9]+' || echo "0")
    local total=$(echo "$test_output" | grep -oE 'Total Tests: [0-9]+' | grep -oE '[0-9]+' || echo "0")

    if [[ -z "$passed" ]]; then passed=0; fi
    if [[ -z "$total" ]]; then total=0; fi

    local failed=$((total - passed))
    if [[ $failed -lt 0 ]]; then failed=0; fi

    CPP_PASSED=$passed
    CPP_FAILED=$failed

    cd "$SCRIPT_DIR"

    return $exit_code
}

run_python_tests() {
    print_header "Python Tests (pytest)"

    local pytest_args=("-v" "--tb=short")

    if [[ -n "$COVERAGE" && "$COVERAGE" == "true" ]]; then
        pytest_args+=("--cov=music_brain" "--cov=penta_core" "--cov-report=html" "--cov-report=term")
    fi

    if [[ -n "$FAST" ]]; then
        pytest_args+=("-m" "not slow")
    fi

    local exit_code=0
    local test_dirs=()

    # Find test directories
    if [[ -d "${SCRIPT_DIR}/DAiW-Music-Brain/tests" ]]; then
        test_dirs+=("${SCRIPT_DIR}/DAiW-Music-Brain/tests")
    fi

    if [[ -d "${SCRIPT_DIR}/penta-core/tests" ]]; then
        test_dirs+=("${SCRIPT_DIR}/penta-core/tests")
    fi

    if [[ ${#test_dirs[@]} -eq 0 ]]; then
        echo -e "${YELLOW}No Python test directories found.${NC}"
        return 0
    fi

    # Run pytest
    local test_output
    test_output=$(python3 -m pytest "${pytest_args[@]}" "${test_dirs[@]}" 2>&1) || exit_code=$?
    echo "$test_output"

    # Parse results
    local summary=$(echo "$test_output" | grep -E '^=.*(passed|failed|error).*=$' | tail -1)
    PYTHON_PASSED=$(echo "$summary" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo "0")
    PYTHON_FAILED=$(echo "$summary" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")

    if [[ -z "$PYTHON_PASSED" ]]; then PYTHON_PASSED=0; fi
    if [[ -z "$PYTHON_FAILED" ]]; then PYTHON_FAILED=0; fi

    return $exit_code
}

print_summary() {
    print_header "Test Summary"

    local total_passed=$((CPP_PASSED + PYTHON_PASSED))
    local total_failed=$((CPP_FAILED + PYTHON_FAILED))
    local total=$((total_passed + total_failed))

    if [[ "$RUN_CPP" == "true" ]]; then
        print_result "C++ Tests" "$CPP_PASSED" "$CPP_FAILED"
    fi

    if [[ "$RUN_PYTHON" == "true" ]]; then
        print_result "Python Tests" "$PYTHON_PASSED" "$PYTHON_FAILED"
    fi

    echo ""
    echo -e "${CYAN}--------------------------------------------${NC}"

    if [[ $total_failed -eq 0 ]]; then
        echo -e "${GREEN}  OVERALL: $total_passed/$total tests passed${NC}"
        echo -e "${GREEN}  All tests passed!${NC}"
    else
        echo -e "${RED}  OVERALL: $total_passed/$total tests passed${NC}"
        echo -e "${RED}  $total_failed tests failed${NC}"
    fi

    echo ""

    return $total_failed
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --cpp-only)
            RUN_CPP=true
            RUN_PYTHON=false
            shift
            ;;
        --python-only)
            RUN_CPP=false
            RUN_PYTHON=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        --help|-h)
            head -15 "$0" | tail -12 | sed 's/^#//'
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Main
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  iDAWi Unified Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"

cpp_exit=0
python_exit=0

if [[ "$RUN_CPP" == "true" ]]; then
    run_cpp_tests || cpp_exit=$?
fi

if [[ "$RUN_PYTHON" == "true" ]]; then
    run_python_tests || python_exit=$?
fi

# Print summary and exit with appropriate code
print_summary
exit_code=$?

if [[ $exit_code -gt 0 ]]; then
    exit 1
fi

exit 0
