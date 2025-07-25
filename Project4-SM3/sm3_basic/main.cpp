#include "sm3.h"
#include <chrono>
#include <iostream>
#include <vector>
#include <iomanip>

using namespace std;
using namespace std::chrono;

// 测试向量验证
void test_sm3_correctness() {
    cout << "=== SM3 Correctness Test ===" << endl;
    
    // 测试向量1: "abc"
    const char* msg1 = "abc";
    uint8_t digest1[SM3_DIGEST_SIZE];
    sm3_hash((const uint8_t*)msg1, strlen(msg1), digest1);
    
    cout << "Test 1 - Input: \"abc\"" << endl;
    cout << "Output: ";
    sm3_print_hex(digest1, SM3_DIGEST_SIZE);
    cout << "Expected: 66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0" << endl;
    
    // 测试向量2: "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
    const char* msg2 = "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd";
    uint8_t digest2[SM3_DIGEST_SIZE];
    sm3_hash((const uint8_t*)msg2, strlen(msg2), digest2);
    
    cout << "\nTest 2 - Input: \"" << msg2 << "\"" << endl;
    cout << "Output: ";
    sm3_print_hex(digest2, SM3_DIGEST_SIZE);
    cout << "Expected: debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732" << endl;
    
    // 测试向量3: 空字符串
    uint8_t digest3[SM3_DIGEST_SIZE];
    sm3_hash(nullptr, 0, digest3);
    
    cout << "\nTest 3 - Input: Empty string" << endl;
    cout << "Output: ";
    sm3_print_hex(digest3, SM3_DIGEST_SIZE);
    cout << "Expected: 1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b" << endl;
    
    cout << endl;
}

// 性能测试
void test_sm3_performance() {
    cout << "=== SM3 Performance Test ===" << endl;
    
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
        
        // 性能测试
        auto start_time = high_resolution_clock::now();
        sm3_hash(data.data(), size, digest);
        auto end_time = high_resolution_clock::now();
        
        auto duration = duration_cast<milliseconds>(end_time - start_time);
        double throughput = (double)size / (1024 * 1024) / (duration.count() / 1000.0);
        
        cout << "Time: " << duration.count() << " ms" << endl;
        cout << "Throughput: " << fixed << setprecision(2) << throughput << " MB/s" << endl;
        cout << "Hash: ";
        sm3_print_hex(digest, SM3_DIGEST_SIZE);
    }
}

// 批量性能测试
void test_batch_performance() {
    cout << "\n=== Batch Processing Performance Test ===" << endl;
    
    const size_t block_size = 64 * 1024; // 64KB
    const int iterations = 1000;
    
    vector<uint8_t> data(block_size);
    for (size_t i = 0; i < block_size; i++) {
        data[i] = (uint8_t)(i & 0xFF);
    }
    
    uint8_t digest[SM3_DIGEST_SIZE];
    
    auto start_time = high_resolution_clock::now();
    
    for (int i = 0; i < iterations; i++) {
        sm3_hash(data.data(), block_size, digest);
    }
    
    auto end_time = high_resolution_clock::now();
    auto duration = duration_cast<milliseconds>(end_time - start_time);
    
    double total_mb = (double)(block_size * iterations) / (1024 * 1024);
    double throughput = total_mb / (duration.count() / 1000.0);
    
    cout << "Batch processing " << iterations << " times of " << block_size / 1024 << "KB data" << endl;
    cout << "Total time: " << duration.count() << " ms" << endl;
    cout << "Average throughput: " << fixed << setprecision(2) << throughput << " MB/s" << endl;
    cout << "Final hash: ";
    sm3_print_hex(digest, SM3_DIGEST_SIZE);
}

// 内存使用测试
void test_memory_usage() {
    cout << "\n=== Memory Usage Test ===" << endl;
    
    sm3_context_t ctx;
    cout << "SM3 context size: " << sizeof(ctx) << " bytes" << endl;
    cout << "State array size: " << sizeof(ctx.state) << " bytes" << endl;
    cout << "Buffer size: " << sizeof(ctx.buffer) << " bytes" << endl;
    
    // 测试增量更新
    const char* test_data = "The quick brown fox jumps over the lazy dog";
    uint8_t digest[SM3_DIGEST_SIZE];
    
    sm3_init(&ctx);
    
    // 分块更新
    size_t len = strlen(test_data);
    size_t chunk_size = 8;
    
    auto start_time = high_resolution_clock::now();
    
    for (size_t i = 0; i < len; i += chunk_size) {
        size_t remaining = len - i;
        size_t current_chunk = (remaining < chunk_size) ? remaining : chunk_size;
        sm3_update(&ctx, (const uint8_t*)test_data + i, current_chunk);
    }
    
    sm3_final(&ctx, digest);
    auto end_time = high_resolution_clock::now();
    
    auto duration = duration_cast<microseconds>(end_time - start_time);
    
    cout << "Incremental update test data: \"" << test_data << "\"" << endl;
    cout << "Chunk size: " << chunk_size << " bytes" << endl;
    cout << "Time: " << duration.count() << " microseconds" << endl;
    cout << "Hash: ";
    sm3_print_hex(digest, SM3_DIGEST_SIZE);
}

int main() {
    cout << "SM3 Hash Algorithm - Basic Optimized Version Test" << endl;
    cout << "======================================" << endl;
    
    try {
        test_sm3_correctness();
        test_sm3_performance();
        test_batch_performance();
        test_memory_usage();
        
        cout << "\nAll tests completed!" << endl;
        
    } catch (const exception& e) {
        cerr << "Error occurred during testing: " << e.what() << endl;
        return 1;
    }
    
    return 0;
} 