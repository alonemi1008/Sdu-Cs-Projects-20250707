#include "sm3_simd.h"
#include <chrono>
#include <iostream>
#include <vector>
#include <iomanip>

using namespace std;
using namespace std::chrono;

// 测试SIMD版本正确性
void test_sm3_simd_correctness() {
    cout << "=== SM3 SIMD Correctness Test ===" << endl;
    
    // 测试向量1: "abc"
    const char* msg1 = "abc";
    uint8_t digest1[SM3_DIGEST_SIZE];
    sm3_simd_hash((const uint8_t*)msg1, strlen(msg1), digest1);
    
    cout << "Test 1 - Input: \"abc\"" << endl;
    cout << "SIMD Output: ";
    sm3_simd_print_hex(digest1, SM3_DIGEST_SIZE);
    cout << "Expected: 66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0" << endl;
    
    // 测试向量2: "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
    const char* msg2 = "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd";
    uint8_t digest2[SM3_DIGEST_SIZE];
    sm3_simd_hash((const uint8_t*)msg2, strlen(msg2), digest2);
    
    cout << "\nTest 2 - Input: \"" << msg2 << "\"" << endl;
    cout << "SIMD Output: ";
    sm3_simd_print_hex(digest2, SM3_DIGEST_SIZE);
    cout << "Expected: debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732" << endl;
    
    // 测试向量3: 空字符串
    uint8_t digest3[SM3_DIGEST_SIZE];
    sm3_simd_hash(nullptr, 0, digest3);
    
    cout << "\nTest 3 - Input: Empty string" << endl;
    cout << "SIMD Output: ";
    sm3_simd_print_hex(digest3, SM3_DIGEST_SIZE);
    cout << "Expected: 1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b" << endl;
    
    cout << endl;
}

// SIMD性能测试
void test_sm3_simd_performance() {
    cout << "=== SM3 SIMD Performance Test ===" << endl;
    
    // 测试不同大小的数据
    vector<size_t> test_sizes = {
        1024,           // 1KB
        1024 * 1024,    // 1MB
        16 * 1024 * 1024, // 16MB
        64 * 1024 * 1024  // 64MB
    };
    
    for (size_t size : test_sizes) {
        cout << "\nTest data size: " << size / 1024 << " KB" << endl;
        
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
        
        cout << "SIMD Time: " << duration.count() << " ms" << endl;
        cout << "SIMD Throughput: " << fixed << setprecision(2) << throughput << " MB/s" << endl;
        cout << "Hash: ";
        sm3_simd_print_hex(digest, SM3_DIGEST_SIZE);
    }
}

// 并行处理测试
void test_parallel_processing() {
    cout << "\n=== Parallel Processing Test ===" << endl;
    
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
    
    cout << "Parallel processing " << num_messages << " messages of " << msg_size / 1024 << "KB each" << endl;
    cout << "Total time: " << duration.count() << " ms" << endl;
    cout << "Total throughput: " << fixed << setprecision(2) << throughput << " MB/s" << endl;
    cout << "Average per message throughput: " << fixed << setprecision(2) << throughput / num_messages << " MB/s" << endl;
    
    // 显示前几个摘要
    cout << "First 3 message hashes:" << endl;
    for (int i = 0; i < min(3, num_messages); i++) {
        cout << "Message " << i << ": ";
        sm3_simd_print_hex(digests[i].data(), SM3_DIGEST_SIZE);
    }
}

// SIMD指令集功能测试
void test_simd_instructions() {
    cout << "\n=== SIMD Instruction Set Test ===" << endl;
    
    // 测试SIMD旋转运算
    uint32_t test_values[4] = {0x12345678, 0x87654321, 0xABCDEF00, 0x00FEDCBA};
    __m128i test_vec = _mm_loadu_si128((__m128i*)test_values);
    
    cout << "Original values: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << test_values[i] << " ";
    }
    cout << endl;
    
    // 测试左旋转12位
    __m128i rotated = sm3_mm_rol_epi32(test_vec, 12);
    uint32_t rotated_values[4];
    _mm_storeu_si128((__m128i*)rotated_values, rotated);
    
    cout << "Left rotate 12 bits: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << rotated_values[i] << " ";
    }
    cout << endl;
    
    // 验证结果
    cout << "Verification (scalar): ";
    for (int i = 0; i < 4; i++) {
        uint32_t expected = ROL(test_values[i], 12);
        cout << hex << expected << " ";
        if (expected != rotated_values[i]) {
            cout << "\nError: SIMD rotation result mismatch!" << endl;
            return;
        }
    }
    cout << "\nSIMD rotation test passed!" << endl;
    
    // 测试P0和P1函数
    __m128i p0_result = sm3_mm_P0_epi32(test_vec);
    __m128i p1_result = sm3_mm_P1_epi32(test_vec);
    
    uint32_t p0_values[4], p1_values[4];
    _mm_storeu_si128((__m128i*)p0_values, p0_result);
    _mm_storeu_si128((__m128i*)p1_values, p1_result);
    
    cout << "P0 SIMD: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << p0_values[i] << " ";
    }
    cout << endl;
    
    cout << "P0 scalar: ";
    for (int i = 0; i < 4; i++) {
        uint32_t expected = P0(test_values[i]);
        cout << hex << expected << " ";
        if (expected != p0_values[i]) {
            cout << "\nError: P0 SIMD result mismatch!" << endl;
            return;
        }
    }
    cout << "\nP0 SIMD function test passed!" << endl;
    
    cout << "P1 SIMD: ";
    for (int i = 0; i < 4; i++) {
        cout << hex << p1_values[i] << " ";
    }
    cout << endl;
    
    cout << "P1 scalar: ";
    for (int i = 0; i < 4; i++) {
        uint32_t expected = P1(test_values[i]);
        cout << hex << expected << " ";
        if (expected != p1_values[i]) {
            cout << "\nError: P1 SIMD result mismatch!" << endl;
            return;
        }
    }
    cout << "\nP1 SIMD function test passed!" << endl;
    
    cout << dec; // 恢复十进制输出
}

// 内存对齐测试
void test_memory_alignment() {
    cout << "\n=== Memory Alignment Test ===" << endl;
    
    // 测试对齐内存分配
    uint32_t *aligned_mem = (uint32_t*)_mm_malloc(68 * sizeof(uint32_t), 32);
    
    if (aligned_mem == nullptr) {
        cout << "Memory allocation failed!" << endl;
        return;
    }
    
    cout << "Aligned memory address: " << hex << (uintptr_t)aligned_mem << endl;
    cout << "32-byte alignment check: " << ((uintptr_t)aligned_mem % 32 == 0 ? "Pass" : "Fail") << endl;
    
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
            __m128i result = sm3_mm_rol_epi32(data, 7);
            _mm_store_si128((__m128i*)(aligned_mem + i), result);
        }
    }
    
    auto end_time = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(end_time - start_time);
    
    cout << dec << "Aligned memory access test (" << iterations << " iterations): " 
         << duration.count() << " microseconds" << endl;
    
    _mm_free(aligned_mem);
    cout << "Memory alignment test completed!" << endl;
}

int main() {
    cout << "SM3 Hash Algorithm - SIMD Optimized Version Test" << endl;
    cout << "========================================" << endl;
    
    try {
        test_sm3_simd_correctness();
        test_sm3_simd_performance();
        test_parallel_processing();
        test_simd_instructions();
        test_memory_alignment();
        
        cout << "\nAll SIMD tests completed!" << endl;
        
    } catch (const exception& e) {
        cerr << "Error occurred during testing: " << e.what() << endl;
        return 1;
    }
    
    return 0;
} 