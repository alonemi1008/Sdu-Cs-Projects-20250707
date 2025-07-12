@echo off
echo ========================================
echo SM3 算法 GCC 编译性能测试
echo ========================================

:: 检查g++编译器
where g++ >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到g++编译器，请安装MinGW或MSYS2
    pause
    exit /b 1
)

echo.
echo 1. 编译基础优化版本...
cd sm3_basic
g++ -O3 -std=c++11 -Wall -Wextra -march=native -o sm3_basic_gcc.exe sm3.cpp main.cpp
if %errorlevel% equ 0 (
    echo ✓ 基础版本编译成功
) else (
    echo ✗ 基础版本编译失败
    pause
    exit /b 1
)

echo.
echo 2. 编译SIMD优化版本...
cd ../sm3_simd
g++ -O3 -std=c++11 -Wall -Wextra -march=native -mavx2 -msse4.2 -o sm3_simd_gcc.exe sm3_simd.cpp main_simd.cpp
if %errorlevel% equ 0 (
    echo ✓ SIMD版本编译成功
) else (
    echo ✗ SIMD版本编译失败
    echo 注意: 您的CPU可能不支持AVX2/SSE4.2指令集
)

echo.
echo 3. 编译性能对比测试...
cd ../performance_test
g++ -O3 -std=c++11 -Wall -Wextra -march=native -mavx2 -msse4.2 -I../sm3_basic -I../sm3_simd -o benchmark_gcc.exe benchmark.cpp ../sm3_basic/sm3.cpp ../sm3_simd/sm3_simd.cpp
if %errorlevel% equ 0 (
    echo ✓ 性能测试编译成功
) else (
    echo ✗ 性能测试编译失败
)

echo.
echo ========================================
echo 开始性能测试
echo ========================================

echo.
echo 基础版本性能测试:
echo ------------------
cd ../sm3_basic
echo 开始时间: %time%
sm3_basic_gcc.exe
echo 结束时间: %time%

echo.
echo SIMD版本性能测试:
echo ------------------
cd ../sm3_simd
if exist sm3_simd_gcc.exe (
    echo 开始时间: %time%
    sm3_simd_gcc.exe
    echo 结束时间: %time%
) else (
    echo SIMD版本编译失败，跳过测试
)

echo.
echo 综合性能对比测试:
echo ------------------
cd ../performance_test
if exist benchmark_gcc.exe (
    echo 开始时间: %time%
    benchmark_gcc.exe
    echo 结束时间: %time%
) else (
    echo 性能测试编译失败，跳过测试
)

echo.
echo ========================================
echo 性能测试完成！
echo ========================================

:: 显示编译结果文件
echo.
echo 生成的可执行文件:
if exist sm3_basic\sm3_basic_gcc.exe echo ✓ sm3_basic\sm3_basic_gcc.exe
if exist sm3_simd\sm3_simd_gcc.exe echo ✓ sm3_simd\sm3_simd_gcc.exe  
if exist performance_test\benchmark_gcc.exe echo ✓ performance_test\benchmark_gcc.exe

echo.
echo 编译选项说明:
echo -O3: 最高级别优化
echo -std=c++11: C++11标准
echo -march=native: 针对当前CPU优化
echo -mavx2 -msse4.2: SIMD指令集支持

pause 