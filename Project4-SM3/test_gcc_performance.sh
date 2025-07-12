#!/bin/bash

echo "========================================"
echo "SM3 算法 GCC 编译性能测试"
echo "========================================"

# 检查编译器
if ! command -v g++ &> /dev/null; then
    echo "错误: 未找到g++编译器"
    exit 1
fi

echo "编译器版本:"
g++ --version | head -1

# 检查CPU特性
echo
echo "CPU特性检查:"
if [ -f /proc/cpuinfo ]; then
    echo "CPU型号: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2)"
    echo -n "AVX2支持: "
    grep -q avx2 /proc/cpuinfo && echo "✓" || echo "✗"
    echo -n "SSE4.2支持: "
    grep -q sse4_2 /proc/cpuinfo && echo "✓" || echo "✗"
fi

echo
echo "1. 编译基础优化版本..."
cd sm3_basic
g++ -O3 -std=c++11 -Wall -Wextra -march=native -o sm3_basic_gcc sm3.cpp main.cpp
if [ $? -eq 0 ]; then
    echo "✓ 基础版本编译成功"
    basic_compiled=1
else
    echo "✗ 基础版本编译失败"
    basic_compiled=0
fi

echo
echo "2. 编译SIMD优化版本..."
cd ../sm3_simd
g++ -O3 -std=c++11 -Wall -Wextra -march=native -mavx2 -msse4.2 -o sm3_simd_gcc sm3_simd.cpp main_simd.cpp
if [ $? -eq 0 ]; then
    echo "✓ SIMD版本编译成功"
    simd_compiled=1
else
    echo "✗ SIMD版本编译失败"
    echo "注意: 您的CPU可能不支持AVX2/SSE4.2指令集"
    simd_compiled=0
fi

echo
echo "3. 编译性能对比测试..."
cd ../performance_test
g++ -O3 -std=c++11 -Wall -Wextra -march=native -mavx2 -msse4.2 \
    -I../sm3_basic -I../sm3_simd \
    -o benchmark_gcc benchmark.cpp ../sm3_basic/sm3.cpp ../sm3_simd/sm3_simd.cpp
if [ $? -eq 0 ]; then
    echo "✓ 性能测试编译成功"
    benchmark_compiled=1
else
    echo "✗ 性能测试编译失败"
    benchmark_compiled=0
fi

echo
echo "========================================"
echo "开始性能测试"
echo "========================================"

# 基础版本测试
if [ $basic_compiled -eq 1 ]; then
    echo
    echo "基础版本性能测试:"
    echo "------------------"
    cd ../sm3_basic
    echo "开始时间: $(date)"
    time ./sm3_basic_gcc
    echo "结束时间: $(date)"
fi

# SIMD版本测试
if [ $simd_compiled -eq 1 ]; then
    echo
    echo "SIMD版本性能测试:"
    echo "------------------"
    cd ../sm3_simd
    echo "开始时间: $(date)"
    time ./sm3_simd_gcc
    echo "结束时间: $(date)"
fi

# 综合性能测试
if [ $benchmark_compiled -eq 1 ]; then
    echo
    echo "综合性能对比测试:"
    echo "------------------"
    cd ../performance_test
    echo "开始时间: $(date)"
    time ./benchmark_gcc
    echo "结束时间: $(date)"
fi

echo
echo "========================================"
echo "性能测试完成！"
echo "========================================"

# 显示编译结果
echo
echo "生成的可执行文件:"
[ -f sm3_basic/sm3_basic_gcc ] && echo "✓ sm3_basic/sm3_basic_gcc"
[ -f sm3_simd/sm3_simd_gcc ] && echo "✓ sm3_simd/sm3_simd_gcc"
[ -f performance_test/benchmark_gcc ] && echo "✓ performance_test/benchmark_gcc"

echo
echo "编译选项说明:"
echo "-O3: 最高级别优化"
echo "-std=c++11: C++11标准"
echo "-march=native: 针对当前CPU优化"
echo "-mavx2 -msse4.2: SIMD指令集支持"

# 性能分析建议
echo
echo "性能分析建议:"
echo "1. 使用 time 命令测量执行时间"
echo "2. 使用 perf stat 分析缓存性能"
echo "3. 使用 valgrind --tool=cachegrind 进行详细分析"
echo "4. 比较不同优化级别 (-O0, -O1, -O2, -O3) 的性能差异" 