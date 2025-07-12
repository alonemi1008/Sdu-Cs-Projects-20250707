# SM3 算法 GCC 编译与性能测试指南

本指南详细说明如何使用gcc编译器编译SM3算法的不同版本，并进行性能测试。

## 编译指令

### 1. 基础优化版本

```bash
cd Project4-SM3/sm3_basic
g++ -O3 -std=c++11 -Wall -Wextra -march=native -o sm3_basic sm3.cpp main.cpp
./sm3_basic
```

**编译选项说明：**
- `-O3`: 最高级别优化
- `-std=c++11`: 使用C++11标准
- `-march=native`: 针对当前CPU优化
- `-Wall -Wextra`: 启用详细警告

### 2. SIMD优化版本

```bash
cd Project4-SM3/sm3_simd
g++ -O3 -std=c++11 -Wall -Wextra -march=native -mavx2 -msse4.2 -o sm3_simd sm3_simd.cpp main_simd.cpp
./sm3_simd
```

**SIMD编译选项说明：**
- `-mavx2`: 启用AVX2指令集
- `-msse4.2`: 启用SSE4.2指令集
- 需要CPU支持相应指令集

### 3. 性能对比测试

```bash
cd Project4-SM3/performance_test
g++ -O3 -std=c++11 -Wall -Wextra -march=native -mavx2 -msse4.2 \
    -I../sm3_basic -I../sm3_simd \
    -o benchmark benchmark.cpp ../sm3_basic/sm3.cpp ../sm3_simd/sm3_simd.cpp
./benchmark
```

## CPU指令集检测

在编译SIMD版本前，请检查CPU是否支持所需指令集：

### Linux系统
```bash
# 检查CPU特性
cat /proc/cpuinfo | grep flags

# 检查AVX2支持
grep -o avx2 /proc/cpuinfo | head -1

# 检查SSE4.2支持  
grep -o sse4_2 /proc/cpuinfo | head -1
```

### Windows系统
```cmd
# 使用wmic命令
wmic cpu get Name,Description

# 或在PowerShell中
Get-WmiObject -Class Win32_Processor | Select-Object Name,Description
```

## 性能测试方法

### 1. 基础性能测试

测试不同数据大小的处理性能：

```bash
# 编译基础版本
g++ -O3 -std=c++11 -march=native -o sm3_basic sm3.cpp main.cpp

# 编译SIMD版本
g++ -O3 -std=c++11 -march=native -mavx2 -msse4.2 -o sm3_simd sm3_simd.cpp main_simd.cpp

# 运行测试
echo "基础版本性能测试："
time ./sm3_basic

echo "SIMD版本性能测试："
time ./sm3_simd
```

### 2. 详细性能分析

使用benchmark程序进行详细性能分析：

```bash
cd Project4-SM3/performance_test

# 编译性能测试程序
g++ -O3 -std=c++11 -march=native -mavx2 -msse4.2 \
    -I../sm3_basic -I../sm3_simd \
    -o benchmark benchmark.cpp ../sm3_basic/sm3.cpp ../sm3_simd/sm3_simd.cpp

# 运行完整基准测试
./benchmark

# 保存测试结果
./benchmark > performance_results.txt 2>&1
```

### 3. 大数据量性能测试

创建自定义测试脚本：

```bash
# 创建测试脚本
cat > test_performance.sh << 'EOF'
#!/bin/bash

echo "SM3 算法性能测试"
echo "=================="

# 测试不同数据大小
for size in 1024 65536 1048576 16777216; do
    echo "测试数据大小: $((size/1024)) KB"
    
    # 基础版本
    echo -n "基础版本: "
    echo $size | ./sm3_basic
    
    # SIMD版本  
    echo -n "SIMD版本: "
    echo $size | ./sm3_simd
    
    echo "---"
done
EOF

chmod +x test_performance.sh
./test_performance.sh
```

## 编译优化选项对比

### 不同优化级别测试

```bash
# O0 - 无优化
g++ -O0 -std=c++11 -o sm3_O0 sm3.cpp main.cpp

# O1 - 基本优化  
g++ -O1 -std=c++11 -o sm3_O1 sm3.cpp main.cpp

# O2 - 标准优化
g++ -O2 -std=c++11 -o sm3_O2 sm3.cpp main.cpp

# O3 - 最高优化
g++ -O3 -std=c++11 -o sm3_O3 sm3.cpp main.cpp

# 性能对比
echo "优化级别性能对比："
for opt in O0 O1 O2 O3; do
    echo -n "$opt: "
    time ./sm3_$opt > /dev/null
done
```

### 特定CPU优化

```bash
# 通用优化
g++ -O3 -std=c++11 -o sm3_generic sm3.cpp main.cpp

# 本机CPU优化
g++ -O3 -std=c++11 -march=native -o sm3_native sm3.cpp main.cpp

# Intel CPU优化
g++ -O3 -std=c++11 -march=skylake -o sm3_skylake sm3.cpp main.cpp

# AMD CPU优化  
g++ -O3 -std=c++11 -march=znver2 -o sm3_znver2 sm3.cpp main.cpp
```

## 性能分析工具

### 1. 使用perf进行性能分析

```bash
# 安装perf (Ubuntu/Debian)
sudo apt-get install linux-tools-common linux-tools-generic

# 性能分析
perf record ./sm3_simd
perf report

# 查看缓存命中率
perf stat -e cache-misses,cache-references ./sm3_simd
```

### 2. 使用gprof进行函数级分析

```bash
# 编译时添加性能分析选项
g++ -O3 -std=c++11 -pg -o sm3_profile sm3.cpp main.cpp

# 运行程序生成分析数据
./sm3_profile

# 查看分析结果
gprof sm3_profile gmon.out > profile_report.txt
```

### 3. 使用valgrind进行内存分析

```bash
# 安装valgrind
sudo apt-get install valgrind

# 内存使用分析
valgrind --tool=massif ./sm3_basic

# 缓存性能分析
valgrind --tool=cachegrind ./sm3_simd
```

## 预期性能结果

基于测试，预期性能表现如下：

| 数据大小 | 基础版本 (MB/s) | SIMD版本 (MB/s) | 加速比 |
|---------|----------------|----------------|--------|
| 1KB     | 40-50          | 55-65          | 1.2-1.4x |
| 64KB    | 150-170        | 220-250        | 1.4-1.6x |
| 1MB     | 220-250        | 350-400        | 1.6-1.8x |
| 16MB    | 250-280        | 420-480        | 1.7-2.0x |

## 故障排除

### 编译错误处理

1. **AVX2不支持错误**
```bash
# 错误信息: illegal instruction
# 解决方案: 检查CPU支持或使用基础版本
grep avx2 /proc/cpuinfo || echo "CPU不支持AVX2"
```

2. **头文件缺失错误**
```bash
# 错误信息: immintrin.h not found  
# 解决方案: 安装完整的GCC开发包
sudo apt-get install build-essential
```

3. **链接错误**
```bash
# 确保所有源文件都在编译命令中
g++ -O3 -std=c++11 -o program file1.cpp file2.cpp
```

### 性能问题诊断

1. **性能不如预期**
   - 检查编译优化选项是否正确
   - 确认CPU频率设置（关闭节能模式）
   - 检查系统负载

2. **SIMD版本比基础版本慢**
   - 可能是数据量太小，SIMD开销大于收益
   - 检查内存对齐
   - 确认指令集正确启用

## 自动化测试脚本

创建完整的自动化测试：

```bash
cat > full_test.sh << 'EOF'
#!/bin/bash

echo "SM3算法完整编译和性能测试"
echo "============================"

# 检查编译器
if ! command -v g++ &> /dev/null; then
    echo "错误: g++编译器未找到"
    exit 1
fi

# 检查CPU特性
echo "CPU特性检查:"
grep -o "avx2\|sse4_2" /proc/cpuinfo | sort | uniq

# 编译所有版本
echo "编译基础版本..."
cd sm3_basic
g++ -O3 -std=c++11 -march=native -o sm3_basic sm3.cpp main.cpp
if [ $? -eq 0 ]; then echo "✓ 基础版本编译成功"; else echo "✗ 基础版本编译失败"; fi

echo "编译SIMD版本..."
cd ../sm3_simd  
g++ -O3 -std=c++11 -march=native -mavx2 -msse4.2 -o sm3_simd sm3_simd.cpp main_simd.cpp
if [ $? -eq 0 ]; then echo "✓ SIMD版本编译成功"; else echo "✗ SIMD版本编译失败"; fi

echo "编译性能测试..."
cd ../performance_test
g++ -O3 -std=c++11 -march=native -mavx2 -msse4.2 \
    -I../sm3_basic -I../sm3_simd \
    -o benchmark benchmark.cpp ../sm3_basic/sm3.cpp ../sm3_simd/sm3_simd.cpp
if [ $? -eq 0 ]; then echo "✓ 性能测试编译成功"; else echo "✗ 性能测试编译失败"; fi

# 运行测试
echo "运行性能测试..."
./benchmark

echo "测试完成!"
EOF

chmod +x full_test.sh
```

使用此脚本可以一键完成所有编译和测试工作。 