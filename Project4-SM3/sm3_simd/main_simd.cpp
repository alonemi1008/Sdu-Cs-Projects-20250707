#include "sm3_simd.h"
#include <chrono>
#include <iostream>
#include <vector>
#include <iomanip>

using namespace std;
using namespace std::chrono;

// 测试SIMD版本正确性
void test_sm3_simd_correctness() {
    cout << "=== SM3 SIMD版本正确性测试 ===" << endl;
    
    // 测试向量1: "abc"
    const char* msg1 = "abc";
    uint8_t digest1[SM3_DIGEST_SIZE];
    sm3_simd_hash((const uint8_t*)msg1, strlen(msg1), digest1);
    
    cout << "测试1 - 输入: \"abc\"" << endl;
    cout << "SIMD输出: ";
    sm3_simd_print_hex(digest1, SM3_DIGEST_SIZE);
    cout << "期望输出: 66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0" << endl;
    
    // 测试向量2: "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
    const char* msg2 = "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd";
    uint8_t digest2[SM3_DIGEST_SIZE];
    sm3_simd_hash((const uint8_t*)msg2, strlen(msg2), digest2);
    
    cout << "\n测试2 - 输入: \"" << msg2 << "\"" << endl;
    cout << "SIMD输出: ";
    sm3_simd_print_hex(digest2, SM3_DIGEST_SIZE);
    cout << "期望输出: debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732" << endl;
    
    // 测试向量3: 空字符串
    uint8_t digest3[SM3_DIGEST_SIZE];
    sm3_simd_hash(nullptr, 0, digest3);
    
    cout << "\n测试3 - 输入: 空字符串" << endl;
    cout << "SIMD输出: ";
    sm3_simd_print_hex(digest3, SM3_DIGEST_SIZE);
    cout << "期望输出: 1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b" << endl;
    
    cout << endl;
}

// SIMD性能测试
void test_sm3_simd_performance() {
    cout << "=== SM3 SIMD版本性能测试 ===" << endl;
    
    // 测试不同大小的数据
    vector<size_t> test_sizes = {
        1024,           // 1KB
        1024 * 1024,    // 1MB
        16 * 1024 * 1024, // 16MB
        64 * 1024 * 1024  // 64MB
    };
    
    for (size_t size : test_sizes) {
        cout << "\n测试数据大小: " << size / 1024 << " KB" << endl;
        
        // 准备测试数据
        vector<uint8_t> data(size);
        for (size_t i = 0; i < size; i++) {
            data[i] = (uint8_t)(i & 0xFF);
        }
        
        uint8_t digest[SM3_DIGEST_SIZE];
        
        // SIMD性能测试
        auto start_time = high_resolution_clock::now();
        sm3_simd_hash(data.data(), size, digest);
        auto end_time = high_resolution_clock::now();
        
        auto duration = duration_cast<milliseconds>(end_time - start_time);
        double throughput = (double)size / (1024 * 1024) / (duration.count() / 1000.0);
        
        cout << "SIMD耗时: " << duration.count() << " ms" << endl;
        cout << "SIMD吞吐量: " << fixed << setprecision(2) << throughput << " MB/s" << endl;
        cout << "摘要: ";
        sm3_simd_print_hex(digest, SM3_DIGEST_SIZE);
    }
}

// 并行处理测试
void test_parallel_processing() {
    cout << "\n=== 并行处理测试 ===" << endl;
    
    const int num_messages = 8;
    const size_t msg_size = 1024 * 1024; // 1MB per message
    
    // 准备测试数据
    vector<vector<uint8_t>> messages(num_messages);
    vector<const uint8_t*> data_ptrs(num_messages);
    vector<uint32_t> data_lens(num_messages);
    vector<vector<uint8_t>> digests(num_messages);
    vector<uint8_t*> digest_ptrs(num_messages);
    
    for (int i = 0; i < num_messages; i++) {
        messages[i].resize(msg_size);
        digests[i].resize(SM3_DIGEST_SIZE);
        
        // 为每个消息生成不同的数据
        for (size_t j = 0; j < msg_size; j++) {
            messages[i][j] = (uint8_t)((i * msg_size + j) & 0xFF);
        }
        
        data_ptrs[i] = messages[i].data();
        data_lens[i] = msg_size;
        digest_ptrs[i] = digests[i].data();
    }
    
    // 测试并行处理性能
    auto start_time = high_resolution_clock::now();
    sm3_simd_multi_hash(data_ptrs.data(), data_lens.data(), digest_ptrs.data(), num_messages);
    auto end_time = high_resolution_clock::now();
    
    auto duration = duration_cast<milliseconds>(end_time - start_time);
    double total_mb = (double)(msg_size * num_messages) / (1024 * 1024);
    double throughput = total_mb / (duration.count() / 1000.0);
    
    cout << "并行处理 " << num_messages << " 个 " << msg_size / 1024 << "KB 消息" << endl;
    cout << "总耗时: " << duration.count() << " ms" << endl;
    cout << "总吞吐量: " << fixed << setprecision(2) << throughput << " MB/s" << endl;
    cout << "平均每消息吞吐量: " << fixed << setprecision(2) << throughput / num_messages << " MB/s" << endl;
    
    // 显示前几个摘要
    cout << "前3个消息的摘要:" << endl;
    for (int i = 0; i < min(3, num_messages); i++) {
        cout << "消息 " << i << ": ";
        sm3_simd_print_hex(digests[i].data(), SM3_DIGEST_SIZE);
    }
}

// SIMD指令集功能测试
void test_simd_instructions() {
    cout << "\n=== SIMD指令集功能测试 ===" << endl;
    
    // 测试SIMD旋转运算
    uint32_t test_values[4] = {0x12345678, 0x87654321, 0xABCDEF00, 0x00FEDCBA};
    __m128i test_vec = _mm_loadu_si128((__m128i*)test_values);
    
    cout << "原始值: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << test_values[i] << " ";
    }
    cout << endl;
    
    // 测试左旋转12位
    __m128i rotated = _mm_rol_epi32(test_vec, 12);
    uint32_t rotated_values[4];
    _mm_storeu_si128((__m128i*)rotated_values, rotated);
    
    cout << "左旋12位: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << rotated_values[i] << " ";
    }
    cout << endl;
    
    // 验证结果
    cout << "验证 (标量): ";
    for (int i = 0; i < 4; i++) {
        uint32_t expected = ROL(test_values[i], 12);
        cout << hex << expected << " ";
        if (expected != rotated_values[i]) {
            cout << "\n错误：SIMD旋转结果不匹配！" << endl;
            return;
        }
    }
    cout << "\nSIMD旋转运算测试通过！" << endl;
    
    // 测试P0和P1函数
    __m128i p0_result = _mm_P0_epi32(test_vec);
    __m128i p1_result = _mm_P1_epi32(test_vec);
    
    uint32_t p0_values[4], p1_values[4];
    _mm_storeu_si128((__m128i*)p0_values, p0_result);
    _mm_storeu_si128((__m128i*)p1_values, p1_result);
    
    cout << "P0 SIMD: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << p0_values[i] << " ";
    }
    cout << endl;
    
    cout << "P0 标量: ";
    for (int i = 0; i < 4; i++) {
        uint32_t expected = P0(test_values[i]);
        cout << hex << expected << " ";
        if (expected != p0_values[i]) {
            cout << "\n错误：P0 SIMD结果不匹配！" << endl;
            return;
        }
    }
    cout << "\nP0 SIMD函数测试通过！" << endl;
    
    cout << "P1 SIMD: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << p1_values[i] << " ";
    }
    cout << endl;
    
    cout << "P1 标量: ";
    for (int i = 0; i < 4; i++) {
        uint32_t expected = P1(test_values[i]);
        cout << hex << expected << " ";
        if (expected != p1_values[i]) {
            cout << "\n错误：P1 SIMD结果不匹配！" << endl;
            return;
        }
    }
    cout << "\nP1 SIMD函数测试通过！" << endl;
    
    cout << dec; // 恢复十进制输出
}

// 内存对齐测试
void test_memory_alignment() {
    cout << "\n=== 内存对齐测试 ===" << endl;
    
    // 测试对齐内存分配
    uint32_t *aligned_mem = (uint32_t*)_mm_malloc(68 * sizeof(uint32_t), 32);
    
    if (aligned_mem == nullptr) {
        cout << "内存分配失败！" << endl;
        return;
    }
    
    cout << "对齐内存地址: " << hex << (uintptr_t)aligned_mem << endl;
    cout << "32字节对齐检查: " << ((uintptr_t)aligned_mem % 32 == 0 ? "通过" : "失败") << endl;
    
    // 测试对齐访问性能
    const int iterations = 1000000;
    
    // 填充测试数据
    for (int i = 0; i < 68; i++) {
        aligned_mem[i] = i;
    }
    
    auto start_time = high_resolution_clock::now();
    
    for (int iter = 0; iter < iterations; iter++) {
        for (int i = 0; i < 64; i += 4) {
            __m128i data = _mm_load_si128((__m128i*)(aligned_mem + i));
            __m128i result = _mm_rol_epi32(data, 7);
            _mm_store_si128((__m128i*)(aligned_mem + i), result);
        }
    }
    
    auto end_time = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(end_time - start_time);
    
    cout << dec << "对齐内存访问测试 (" << iterations << " 次迭代): " 
         << duration.count() << " 微秒" << endl;
    
    _mm_free(aligned_mem);
    cout << "内存对齐测试完成！" << endl;
}

int main() {
    cout << "SM3 哈希算法 - SIMD优化版本测试" << endl;
    cout << "========================================" << endl;
    
    try {
        test_sm3_simd_correctness();
        test_sm3_simd_performance();
        test_parallel_processing();
        test_simd_instructions();
        test_memory_alignment();
        
        cout << "\n所有SIMD测试完成！" << endl;
        
    } catch (const exception& e) {
        cerr << "测试过程中发生错误: " << e.what() << endl;
        return 1;
    }
    
    return 0;
} 