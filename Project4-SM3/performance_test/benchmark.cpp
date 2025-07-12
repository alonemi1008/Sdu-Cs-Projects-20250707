#include <iostream>
#include <iomanip>
#include <vector>
#include <chrono>
#include <cstring>
#include <memory>
#include <sstream>

// 包含两个版本的头文件
#include "../sm3_basic/sm3.h"
#include "../sm3_simd/sm3_simd.h"

using namespace std;
using namespace std::chrono;

struct BenchmarkResult {
    string version;
    size_t data_size;
    double time_ms;
    double throughput_mbps;
    string digest_hex;
};

class SM3Benchmark {
private:
    vector<BenchmarkResult> results;
    
public:
    // 将字节数组转换为十六进制字符串
    string bytes_to_hex(const uint8_t* bytes, size_t len) {
        stringstream ss;
        for (size_t i = 0; i < len; i++) {
            ss << hex << setw(2) << setfill('0') << (int)bytes[i];
        }
        return ss.str();
    }
    
    // 基础版本性能测试
    BenchmarkResult test_basic_version(const vector<uint8_t>& data) {
        uint8_t digest[SM3_DIGEST_SIZE];
        
        auto start = high_resolution_clock::now();
        sm3_hash(data.data(), data.size(), digest);
        auto end = high_resolution_clock::now();
        
        auto duration = duration_cast<microseconds>(end - start);
        double time_ms = duration.count() / 1000.0;
        double throughput = (double)data.size() / (1024 * 1024) / (time_ms / 1000.0);
        
        BenchmarkResult result;
        result.version = "Basic";
        result.data_size = data.size();
        result.time_ms = time_ms;
        result.throughput_mbps = throughput;
        result.digest_hex = bytes_to_hex(digest, SM3_DIGEST_SIZE);
        
        return result;
    }
    
    // SIMD版本性能测试
    BenchmarkResult test_simd_version(const vector<uint8_t>& data) {
        uint8_t digest[SM3_DIGEST_SIZE];
        
        auto start = high_resolution_clock::now();
        sm3_simd_hash(data.data(), data.size(), digest);
        auto end = high_resolution_clock::now();
        
        auto duration = duration_cast<microseconds>(end - start);
        double time_ms = duration.count() / 1000.0;
        double throughput = (double)data.size() / (1024 * 1024) / (time_ms / 1000.0);
        
        BenchmarkResult result;
        result.version = "SIMD";
        result.data_size = data.size();
        result.time_ms = time_ms;
        result.throughput_mbps = throughput;
        result.digest_hex = bytes_to_hex(digest, SM3_DIGEST_SIZE);
        
        return result;
    }
    
    // 运行单个数据大小的基准测试
    void run_benchmark_for_size(size_t size, int iterations = 1) {
        cout << "\nTest data size: " << size / 1024 << " KB";
        if (iterations > 1) {
            cout << " (average of " << iterations << " runs)";
        }
        cout << endl;
        
        // 准备测试数据
        vector<uint8_t> data(size);
        for (size_t i = 0; i < size; i++) {
            data[i] = (uint8_t)(i & 0xFF);
        }
        
        // 多次运行求平均值
        double basic_total_time = 0, simd_total_time = 0;
        string basic_digest, simd_digest;
        
        for (int i = 0; i < iterations; i++) {
            auto basic_result = test_basic_version(data);
            auto simd_result = test_simd_version(data);
            
            basic_total_time += basic_result.time_ms;
            simd_total_time += simd_result.time_ms;
            
            if (i == 0) {
                basic_digest = basic_result.digest_hex;
                simd_digest = simd_result.digest_hex;
            }
        }
        
        double basic_avg_time = basic_total_time / iterations;
        double simd_avg_time = simd_total_time / iterations;
        double basic_throughput = (double)size / (1024 * 1024) / (basic_avg_time / 1000.0);
        double simd_throughput = (double)size / (1024 * 1024) / (simd_avg_time / 1000.0);
        double speedup = basic_avg_time / simd_avg_time;
        
        cout << fixed << setprecision(2);
        cout << "Basic version: " << basic_avg_time << " ms, " << basic_throughput << " MB/s" << endl;
        cout << "SIMD version: " << simd_avg_time << " ms, " << simd_throughput << " MB/s" << endl;
        cout << "Speedup: " << speedup << "x" << endl;
        
        // 验证结果一致性
        if (basic_digest != simd_digest) {
            cout << "Warning: Basic and SIMD version results are inconsistent!" << endl;
            cout << "Basic version: " << basic_digest.substr(0, 16) << "..." << endl;
            cout << "SIMD version: " << simd_digest.substr(0, 16) << "..." << endl;
        } else {
            cout << "Result verification passed" << endl;
        }
        
        // 保存结果
        BenchmarkResult basic_result;
        basic_result.version = "Basic";
        basic_result.data_size = size;
        basic_result.time_ms = basic_avg_time;
        basic_result.throughput_mbps = basic_throughput;
        basic_result.digest_hex = basic_digest;
        results.push_back(basic_result);
        
        BenchmarkResult simd_result;
        simd_result.version = "SIMD";
        simd_result.data_size = size;
        simd_result.time_ms = simd_avg_time;
        simd_result.throughput_mbps = simd_throughput;
        simd_result.digest_hex = simd_digest;
        results.push_back(simd_result);
    }
    
    // 运行完整的基准测试套件
    void run_full_benchmark() {
        cout << "=== SM3 Performance Benchmark ===" << endl;
        cout << "Basic Version vs SIMD Optimized Version" << endl;
        cout << "=========================" << endl;
        
        // 不同大小的测试数据
        vector<pair<size_t, int>> test_cases = {
            {1024, 10},         // 1KB, 10次平均
            {16 * 1024, 5},     // 16KB, 5次平均
            {64 * 1024, 3},     // 64KB, 3次平均
            {256 * 1024, 3},    // 256KB, 3次平均
            {1024 * 1024, 3},   // 1MB, 3次平均
            {4 * 1024 * 1024, 1}, // 4MB, 1次
            {16 * 1024 * 1024, 1} // 16MB, 1次
        };
        
        for (auto& test_case : test_cases) {
            run_benchmark_for_size(test_case.first, test_case.second);
        }
    }
    
    // 测试向量验证
    void run_correctness_test() {
        cout << "\n=== Correctness Verification Test ===" << endl;
        
        vector<pair<string, string>> test_vectors = {
            {"", "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b"},
            {"abc", "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"},
            {"abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd", 
             "debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732"}
        };
        
        for (auto& tv : test_vectors) {
            uint8_t basic_digest[SM3_DIGEST_SIZE];
            uint8_t simd_digest[SM3_DIGEST_SIZE];
            
            const uint8_t* data = (const uint8_t*)tv.first.c_str();
            uint32_t len = tv.first.length();
            
            sm3_hash(data, len, basic_digest);
            sm3_simd_hash(data, len, simd_digest);
            
            string basic_hex = bytes_to_hex(basic_digest, SM3_DIGEST_SIZE);
            string simd_hex = bytes_to_hex(simd_digest, SM3_DIGEST_SIZE);
            
            cout << "Input: \"" << tv.first << "\"" << endl;
            cout << "Expected: " << tv.second << endl;
            cout << "Basic: " << basic_hex << (basic_hex == tv.second ? " Pass" : " Fail") << endl;
            cout << "SIMD: " << simd_hex << (simd_hex == tv.second ? " Pass" : " Fail") << endl;
            cout << "Consistent: " << (basic_hex == simd_hex ? "Yes" : "No") << endl;
            cout << endl;
        }
    }
    
    // 生成性能报告
    void generate_report() {
        cout << "\n=== Performance Test Report ===" << endl;
        cout << left << setw(12) << "Version" 
             << setw(12) << "Data Size" 
             << setw(12) << "Time(ms)" 
             << setw(15) << "Throughput(MB/s)" 
             << "Hash(16chars)" << endl;
        cout << string(65, '-') << endl;
        
        for (size_t i = 0; i < results.size(); i += 2) {
            const auto& basic = results[i];
            const auto& simd = results[i + 1];
            
            cout << fixed << setprecision(2);
            cout << left << setw(12) << basic.version
                 << setw(12) << (basic.data_size / 1024) << "KB"
                 << setw(12) << basic.time_ms
                 << setw(15) << basic.throughput_mbps
                 << basic.digest_hex.substr(0, 16) << endl;
            
            cout << left << setw(12) << simd.version
                 << setw(12) << (simd.data_size / 1024) << "KB"
                 << setw(12) << simd.time_ms
                 << setw(15) << simd.throughput_mbps
                 << simd.digest_hex.substr(0, 16) << endl;
            
            double speedup = basic.time_ms / simd.time_ms;
            cout << left << setw(12) << "Speedup"
                 << setw(12) << ""
                 << setw(12) << speedup << "x"
                 << setw(15) << ""
                 << endl;
            cout << endl;
        }
    }
    
    // 批量处理性能测试
    void run_batch_test() {
        cout << "\n=== Batch Processing Performance Test ===" << endl;
        
        const int num_chunks = 100;
        const size_t chunk_size = 64 * 1024; // 64KB per chunk
        
        vector<uint8_t> data(chunk_size);
        for (size_t i = 0; i < chunk_size; i++) {
            data[i] = (uint8_t)(i & 0xFF);
        }
        
        uint8_t digest[SM3_DIGEST_SIZE];
        
        // 基础版本批量测试
        auto start = high_resolution_clock::now();
        for (int i = 0; i < num_chunks; i++) {
            sm3_hash(data.data(), chunk_size, digest);
        }
        auto end = high_resolution_clock::now();
        auto basic_duration = duration_cast<milliseconds>(end - start);
        
        // SIMD版本批量测试
        start = high_resolution_clock::now();
        for (int i = 0; i < num_chunks; i++) {
            sm3_simd_hash(data.data(), chunk_size, digest);
        }
        end = high_resolution_clock::now();
        auto simd_duration = duration_cast<milliseconds>(end - start);
        
        double total_mb = (double)(num_chunks * chunk_size) / (1024 * 1024);
        double basic_throughput = total_mb / (basic_duration.count() / 1000.0);
        double simd_throughput = total_mb / (simd_duration.count() / 1000.0);
        double speedup = (double)basic_duration.count() / simd_duration.count();
        
                cout << "Batch processing " << num_chunks << " chunks of " << chunk_size / 1024 << "KB each" << endl;
        cout << "Basic version: " << basic_duration.count() << " ms, "
             << fixed << setprecision(2) << basic_throughput << " MB/s" << endl;
        cout << "SIMD version: " << simd_duration.count() << " ms, "
             << fixed << setprecision(2) << simd_throughput << " MB/s" << endl;
        cout << "Batch processing speedup: " << speedup << "x" << endl;
    }
};

int main() {
    cout << "SM3 Hash Algorithm Performance Benchmark" << endl;
    cout << "========================" << endl;
    
    SM3Benchmark benchmark;
    
    try {
        benchmark.run_correctness_test();
        benchmark.run_full_benchmark();
        benchmark.run_batch_test();
        benchmark.generate_report();
        
        cout << "\nBenchmark completed!" << endl;
        
    } catch (const exception& e) {
        cerr << "Error occurred during benchmark: " << e.what() << endl;
        return 1;
    }
    
    return 0;
} 