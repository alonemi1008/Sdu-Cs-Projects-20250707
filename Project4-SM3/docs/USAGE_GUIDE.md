# SM3算法使用指南

本文档详细介绍如何使用SM3哈希算法的各个版本实现。

## 快速开始

### 1. 系统要求检查

首先检查您的系统是否满足要求：

```bash
# 检查编译器版本
gcc --version
g++ --version

# 检查CPU SIMD支持
cd sm3_simd
make cpuinfo
```

### 2. 编译所有版本

```bash
# 编译基础版本
cd sm3_basic
make

# 编译SIMD版本
cd ../sm3_simd
make

# 编译性能测试
cd ../performance_test
make
```

### 3. 运行基本测试

```bash
# 测试基础版本
cd sm3_basic
./sm3_basic

# 测试SIMD版本
cd ../sm3_simd
./sm3_simd

# 运行性能对比
cd ../performance_test
./benchmark
```

## API 详细说明

### 基础版本 API

#### 数据结构

```cpp
typedef struct {
    uint32_t state[8];           // 256位中间状态
    uint64_t count;              // 已处理的字节数
    uint8_t buffer[SM3_BLOCK_SIZE]; // 缓冲区
    uint32_t buffer_len;         // 缓冲区中的字节数
} sm3_context_t;
```

#### 核心函数

**1. 初始化上下文**
```cpp
void sm3_init(sm3_context_t *ctx);
```
- 初始化SM3计算上下文
- 必须在开始计算前调用

**2. 更新数据**
```cpp
void sm3_update(sm3_context_t *ctx, const uint8_t *data, uint32_t len);
```
- 向上下文添加新数据
- 可以多次调用，支持流式处理
- `data`: 输入数据指针
- `len`: 数据长度（字节）

**3. 完成计算**
```cpp
void sm3_final(sm3_context_t *ctx, uint8_t *digest);
```
- 完成哈希计算，输出结果
- `digest`: 输出缓冲区，必须至少32字节

**4. 一次性计算**
```cpp
void sm3_hash(const uint8_t *data, uint32_t len, uint8_t *digest);
```
- 一次性计算数据的SM3哈希值
- 适合小数据块的快速计算

#### 使用示例

**基本用法**
```cpp
#include "sm3.h"
#include <stdio.h>
#include <string.h>

int main() {
    const char *message = "Hello, SM3!";
    uint8_t digest[SM3_DIGEST_SIZE];
    
    // 一次性计算
    sm3_hash((const uint8_t*)message, strlen(message), digest);
    
    // 打印结果
    printf("消息: %s\n", message);
    printf("SM3: ");
    for (int i = 0; i < SM3_DIGEST_SIZE; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");
    
    return 0;
}
```

**流式处理**
```cpp
#include "sm3.h"
#include <stdio.h>

int main() {
    sm3_context_t ctx;
    uint8_t digest[SM3_DIGEST_SIZE];
    
    // 初始化
    sm3_init(&ctx);
    
    // 分块添加数据
    sm3_update(&ctx, (const uint8_t*)"Hello, ", 7);
    sm3_update(&ctx, (const uint8_t*)"SM3!", 4);
    
    // 完成计算
    sm3_final(&ctx, digest);
    
    // 输出结果
    sm3_print_hex(digest, SM3_DIGEST_SIZE);
    
    return 0;
}
```

### SIMD版本 API

#### 单块处理

SIMD版本提供与基础版本兼容的API：

```cpp
void sm3_simd_hash(const uint8_t *data, uint32_t len, uint8_t *digest);
```

#### 多块并行处理

```cpp
void sm3_simd_multi_hash(const uint8_t **data, const uint32_t *lens, 
                         uint8_t **digests, uint32_t count);
```

**参数说明:**
- `data`: 指向数据指针数组
- `lens`: 各数据块长度数组
- `digests`: 指向输出缓冲区指针数组
- `count`: 并行处理的数据块数量

**使用示例:**
```cpp
#include "sm3_simd.h"

int main() {
    // 准备4个数据块
    const char* messages[4] = {
        "Message 1",
        "Message 2", 
        "Message 3",
        "Message 4"
    };
    
    const uint8_t* data[4];
    uint32_t lens[4];
    uint8_t digests[4][SM3_DIGEST_SIZE];
    uint8_t* digest_ptrs[4];
    
    // 设置输入参数
    for (int i = 0; i < 4; i++) {
        data[i] = (const uint8_t*)messages[i];
        lens[i] = strlen(messages[i]);
        digest_ptrs[i] = digests[i];
    }
    
    // 并行计算
    sm3_simd_multi_hash(data, lens, digest_ptrs, 4);
    
    // 输出结果
    for (int i = 0; i < 4; i++) {
        printf("消息 %d: %s\n", i+1, messages[i]);
        printf("哈希值: ");
        sm3_simd_print_hex(digests[i], SM3_DIGEST_SIZE);
    }
    
    return 0;
}
```

## 性能优化技巧

### 1. 数据对齐

对于大量数据处理，确保数据32字节对齐可以提升性能：

```cpp
// 分配对齐内存
uint8_t* aligned_data = (uint8_t*)_mm_malloc(size, 32);
// 使用完毕后释放
_mm_free(aligned_data);
```

### 2. 批量处理

对于多个小数据块，使用批量处理API：

```cpp
// 效率较低 - 逐个处理
for (int i = 0; i < count; i++) {
    sm3_hash(data[i], lens[i], digests[i]);
}

// 效率较高 - 批量处理
sm3_simd_multi_hash(data, lens, digests, count);
```

### 3. 内存预分配

避免频繁的内存分配：

```cpp
// 预分配足够的缓冲区
vector<uint8_t> buffer(max_size);
vector<uint8_t> digest(SM3_DIGEST_SIZE);

// 重复使用缓冲区
for (auto& input : inputs) {
    if (input.size() <= buffer.size()) {
        copy(input.begin(), input.end(), buffer.begin());
        sm3_hash(buffer.data(), input.size(), digest.data());
        // 处理结果...
    }
}
```

## 错误处理

### 常见错误

**1. 编译错误**
```
error: 'immintrin.h' file not found
```
解决方案：确保编译器支持AVX2指令集，或使用基础版本。

**2. 运行时错误**
```
Illegal instruction (SIGILL)
```
解决方案：CPU不支持所需的SIMD指令集，使用基础版本。

**3. 结果不匹配**
```
⚠️ 警告: 基础版本和SIMD版本结果不一致!
```
解决方案：检查编译选项，确保没有优化错误。

### 调试技巧

**1. 启用调试模式**
```bash
make debug
gdb ./sm3_basic
```

**2. 检查中间状态**
```cpp
sm3_context_t ctx;
sm3_init(&ctx);
sm3_print_state(ctx.state);  // 打印初始状态

sm3_update(&ctx, data, len);
sm3_print_state(ctx.state);  // 打印更新后状态
```

**3. 内存检查**
```bash
valgrind --tool=memcheck ./sm3_basic
```

## 性能测试

### 基准测试

运行完整的性能测试：

```bash
cd performance_test
make benchmark
```

### 自定义测试

创建自定义性能测试：

```cpp
#include <chrono>
using namespace std::chrono;

// 测试数据
vector<uint8_t> data(1024 * 1024);  // 1MB
uint8_t digest[SM3_DIGEST_SIZE];

// 计时开始
auto start = high_resolution_clock::now();

// 执行测试
for (int i = 0; i < 1000; i++) {
    sm3_hash(data.data(), data.size(), digest);
}

// 计时结束
auto end = high_resolution_clock::now();
auto duration = duration_cast<milliseconds>(end - start);

cout << "耗时: " << duration.count() << " ms" << endl;
```

## 集成到项目

### CMake集成

创建`CMakeLists.txt`：

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_CXX_STANDARD 11)

# 基础版本
add_library(sm3_basic 
    sm3_basic/sm3.cpp
)
target_include_directories(sm3_basic PUBLIC sm3_basic)

# SIMD版本
add_library(sm3_simd
    sm3_simd/sm3_simd.cpp
)
target_include_directories(sm3_simd PUBLIC sm3_simd)
target_compile_options(sm3_simd PRIVATE -mavx2 -msse4.2)

# 应用程序
add_executable(myapp main.cpp)
target_link_libraries(myapp sm3_basic sm3_simd)
```

### Makefile集成

```makefile
# 在您的项目Makefile中添加
SM3_DIR = path/to/Project4-SM3
CXXFLAGS += -I$(SM3_DIR)/sm3_basic -I$(SM3_DIR)/sm3_simd
LDFLAGS += -L$(SM3_DIR)/sm3_basic -L$(SM3_DIR)/sm3_simd
LIBS += -lsm3_basic -lsm3_simd
```

## 许可证和限制

- 本实现遵循MIT许可证
- 仅供学习和研究使用
- 生产环境请使用经过安全审计的实现
- 遵守相关法律法规和出口管制规定

## 技术支持

如遇到问题，请：

1. 查看README.md和本文档
2. 检查编译环境和系统要求
3. 运行内置的测试程序
4. 提交问题到项目仓库 