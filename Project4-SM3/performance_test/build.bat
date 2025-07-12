@echo off
echo Building SM3 Performance Test...

:: Check if g++ is available
where g++ >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: g++ compiler not found. Please install MinGW or MSYS2.
    pause
    exit /b 1
)

:: Clean previous builds
if exist benchmark.exe del benchmark.exe
if exist *.o del *.o

:: Compile with both versions
echo Compiling benchmark with basic and SIMD versions...
g++ -std=c++11 -O3 -Wall -Wextra -march=native -mavx2 -msse4.2 -I../sm3_basic -I../sm3_simd -o benchmark.exe benchmark.cpp ../sm3_basic/sm3.cpp ../sm3_simd/sm3_simd.cpp

if %errorlevel% equ 0 (
    echo Build successful! Run benchmark.exe to test.
    echo.
    echo Running performance benchmark...
    benchmark.exe
) else (
    echo Build failed with error %errorlevel%
    echo.
    echo Note: Make sure both sm3_basic and sm3_simd folders contain the required source files.
)

pause 