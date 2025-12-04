<#
.SYNOPSIS
    iDAWi Build Script for Windows

.DESCRIPTION
    Build script for the iDAWi Intelligent Digital Audio Workspace

.PARAMETER Command
    Build command: all, cpp, python, test, clean, help (default: all)

.PARAMETER Release
    Build in release mode (default: debug)

.PARAMETER SIMD
    Enable SIMD optimizations

.PARAMETER Parallel
    Number of parallel build jobs (default: auto-detect)

.PARAMETER NoTests
    Skip tests after build

.EXAMPLE
    .\build.ps1
    Build everything in debug mode

.EXAMPLE
    .\build.ps1 -Release -SIMD
    Build in release mode with SIMD optimizations

.EXAMPLE
    .\build.ps1 cpp -Release
    Build only C++ components in release mode

.EXAMPLE
    .\build.ps1 test
    Run all tests
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "cpp", "python", "test", "clean", "help")]
    [string]$Command = "all",

    [switch]$Release,
    [switch]$SIMD,
    [int]$Parallel = 0,
    [switch]$NoTests
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildDir = Join-Path $ScriptDir "build"
$BuildType = if ($Release) { "Release" } else { "Debug" }
$EnableSIMD = if ($SIMD) { "ON" } else { "OFF" }
$RunTests = if ($NoTests) { "OFF" } else { "ON" }

# Colors
function Write-ColorOutput {
    param([string]$Message, [ConsoleColor]$Color = "White")
    $previousColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Output $Message
    $Host.UI.RawUI.ForegroundColor = $previousColor
}

function Write-Step { param([string]$Message) Write-ColorOutput "===> $Message" "Cyan" }
function Write-Success { param([string]$Message) Write-ColorOutput "[OK] $Message" "Green" }
function Write-Warning { param([string]$Message) Write-ColorOutput "[WARN] $Message" "Yellow" }
function Write-Error { param([string]$Message) Write-ColorOutput "[ERROR] $Message" "Red" }

# Detect parallel jobs
function Get-ParallelJobs {
    if ($Parallel -gt 0) { return $Parallel }
    return [Environment]::ProcessorCount
}

# Check prerequisites
function Test-Prerequisites {
    Write-Step "Checking prerequisites..."

    $missing = @()

    # Check CMake
    try {
        $cmakeVersion = & cmake --version 2>$null | Select-Object -First 1
        Write-Success "CMake found: $cmakeVersion"
    }
    catch {
        $missing += "cmake"
    }

    # Check Visual Studio / MSVC
    $vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vsWhere) {
        $vsPath = & $vsWhere -latest -property installationPath
        if ($vsPath) {
            Write-Success "Visual Studio found: $vsPath"
        }
        else {
            $missing += "Visual Studio with C++ workload"
        }
    }
    else {
        # Try to find cl.exe directly
        try {
            $clVersion = & cl 2>&1 | Select-String "Version" | Select-Object -First 1
            Write-Success "MSVC Compiler found"
        }
        catch {
            $missing += "Visual Studio or MSVC compiler"
        }
    }

    # Check Python
    try {
        $pythonVersion = & python --version 2>$null
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        try {
            $pythonVersion = & python3 --version 2>$null
            Write-Success "Python3 found: $pythonVersion"
        }
        catch {
            $missing += "python"
        }
    }

    # Check pip
    try {
        & python -m pip --version 2>$null | Out-Null
        Write-Success "pip found"
    }
    catch {
        $missing += "pip"
    }

    # Check Ninja (optional)
    try {
        $ninjaVersion = & ninja --version 2>$null
        Write-Success "Ninja found: $ninjaVersion"
        $script:CMakeGenerator = "Ninja"
    }
    catch {
        Write-Warning "Ninja not found, using Visual Studio generator"
        $script:CMakeGenerator = ""
    }

    if ($missing.Count -gt 0) {
        Write-Error "Missing prerequisites: $($missing -join ', ')"
        Write-Output ""
        Write-Output "Please install:"
        Write-Output "  - CMake: https://cmake.org/download/"
        Write-Output "  - Visual Studio: https://visualstudio.microsoft.com/ (with C++ workload)"
        Write-Output "  - Python: https://python.org/downloads/"
        Write-Output "  - Ninja (optional): choco install ninja"
        exit 1
    }

    Write-Success "All prerequisites satisfied"
}

# Build C++ components
function Build-Cpp {
    Write-Step "Building C++ components..."

    New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
    Push-Location $BuildDir

    try {
        $cmakeArgs = @(
            "-DCMAKE_BUILD_TYPE=$BuildType"
            "-DPENTA_ENABLE_SIMD=$EnableSIMD"
            "-DPENTA_BUILD_TESTS=$RunTests"
            "-DPENTA_BUILD_PYTHON_BINDINGS=ON"
        )

        if ($script:CMakeGenerator) {
            $cmakeArgs += "-G", $script:CMakeGenerator
        }

        Write-ColorOutput "CMake configuration: $($cmakeArgs -join ' ')" "Cyan"

        $pentaCorePath = Join-Path $ScriptDir "penta-core"
        & cmake @cmakeArgs $pentaCorePath
        if ($LASTEXITCODE -ne 0) { throw "CMake configuration failed" }

        $jobs = Get-ParallelJobs
        & cmake --build . -j $jobs
        if ($LASTEXITCODE -ne 0) { throw "Build failed" }

        Write-Success "C++ build complete"
    }
    finally {
        Pop-Location
    }
}

# Install Python packages
function Build-Python {
    Write-Step "Installing Python packages..."

    # Install DAiW-Music-Brain
    $daiwPath = Join-Path $ScriptDir "DAiW-Music-Brain"
    if (Test-Path $daiwPath) {
        Write-ColorOutput "Installing DAiW-Music-Brain..." "Cyan"
        & python -m pip install -e "$daiwPath[audio,theory]" --quiet
        if ($LASTEXITCODE -ne 0) { throw "Failed to install DAiW-Music-Brain" }
        Write-Success "DAiW-Music-Brain installed"
    }

    # Install penta-core
    $pentaCorePath = Join-Path $ScriptDir "penta-core"
    if (Test-Path $pentaCorePath) {
        Write-ColorOutput "Installing penta-core..." "Cyan"
        & python -m pip install -e "$pentaCorePath[dev]" --quiet
        if ($LASTEXITCODE -ne 0) { throw "Failed to install penta-core" }
        Write-Success "penta-core installed"
    }

    Write-Success "Python packages installed"
}

# Run tests
function Invoke-Tests {
    Write-Step "Running tests..."

    $failed = $false

    # Run C++ tests
    if (Test-Path $BuildDir) {
        Write-ColorOutput "Running C++ tests..." "Cyan"
        Push-Location $BuildDir
        try {
            & ctest --output-on-failure
            if ($LASTEXITCODE -eq 0) {
                Write-Success "C++ tests passed"
            }
            else {
                Write-Error "C++ tests failed"
                $failed = $true
            }
        }
        finally {
            Pop-Location
        }
    }

    # Run Python tests
    Write-ColorOutput "Running Python tests..." "Cyan"

    $daiwTestsPath = Join-Path $ScriptDir "DAiW-Music-Brain\tests"
    if (Test-Path $daiwTestsPath) {
        & python -m pytest $daiwTestsPath -v --tb=short
        if ($LASTEXITCODE -eq 0) {
            Write-Success "DAiW-Music-Brain tests passed"
        }
        else {
            Write-Error "DAiW-Music-Brain tests failed"
            $failed = $true
        }
    }

    if ($failed) {
        Write-Error "Some tests failed"
        exit 1
    }

    Write-Success "All tests passed!"
}

# Clean build artifacts
function Clear-Build {
    Write-Step "Cleaning build artifacts..."

    if (Test-Path $BuildDir) {
        Remove-Item -Recurse -Force $BuildDir
    }

    Get-ChildItem -Path $ScriptDir -Include "__pycache__", "*.egg-info", ".pytest_cache" -Recurse -Directory |
        ForEach-Object { Remove-Item -Recurse -Force $_.FullName }

    Get-ChildItem -Path $ScriptDir -Include "*.pyc" -Recurse -File |
        ForEach-Object { Remove-Item -Force $_.FullName }

    Write-Success "Clean complete"
}

# Show help
function Show-Help {
    Get-Help $MyInvocation.PSCommandPath -Detailed
}

# Main
function Main {
    Write-Output ""
    Write-ColorOutput "==========================================" "Green"
    Write-ColorOutput "  iDAWi Build System (Windows)" "Green"
    Write-ColorOutput "==========================================" "Green"
    Write-Output ""
    Write-ColorOutput "Build type: $BuildType" "Cyan"
    Write-ColorOutput "SIMD: $EnableSIMD" "Cyan"
    Write-ColorOutput "Tests: $RunTests" "Cyan"
    Write-Output ""

    switch ($Command) {
        "all" {
            Test-Prerequisites
            Build-Cpp
            Build-Python
            if ($RunTests -eq "ON") {
                Invoke-Tests
            }
        }
        "cpp" {
            Test-Prerequisites
            Build-Cpp
        }
        "python" {
            Build-Python
        }
        "test" {
            Invoke-Tests
        }
        "clean" {
            Clear-Build
        }
        "help" {
            Show-Help
            return
        }
    }

    Write-Output ""
    Write-Success "Build completed successfully!"
}

Main
