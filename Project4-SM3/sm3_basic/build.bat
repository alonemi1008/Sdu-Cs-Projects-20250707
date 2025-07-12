@echo off
echo Building SM3 Basic Version...

:: Check if g++ is available
where g++ >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: g++ compiler not found. Please install MinGW or MSYS2.
    pause
    exit /b 1
)

:: Clean previous builds
if exist sm3_basic.exe del sm3_basic.exe
if exist *.o del *.o

:: Compile with optimization
echo Compiling with g++...
g++ -std=c++11 -O3 -Wall -Wextra -march=native -o sm3_basic.exe sm3.cpp main.cpp

if %errorlevel% equ 0 (
    echo Build successful! Run sm3_basic.exe to test.
    echo.
    echo Running basic test...
    sm3_basic.exe
) else (
    echo Build failed with error %errorlevel%
)

pause 