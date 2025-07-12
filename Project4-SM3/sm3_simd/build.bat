@echo off
echo Building SM3 SIMD Version...

:: Check if g++ is available
where g++ >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: g++ compiler not found. Please install MinGW or MSYS2.
    pause
    exit /b 1
)

:: Clean previous builds
if exist sm3_simd.exe del sm3_simd.exe
if exist *.o del *.o

:: Compile with SIMD optimization
echo Compiling with AVX2/SSE support...
g++ -std=c++11 -O3 -Wall -Wextra -march=native -mavx2 -msse4.2 -o sm3_simd.exe sm3_simd.cpp main_simd.cpp

if %errorlevel% equ 0 (
    echo Build successful! Run sm3_simd.exe to test.
    echo.
    echo Running SIMD test...
    sm3_simd.exe
) else (
    echo Build failed with error %errorlevel%
    echo.
    echo Note: Your CPU might not support AVX2/SSE4.2 instructions.
    echo Try building the basic version instead.
)

pause 