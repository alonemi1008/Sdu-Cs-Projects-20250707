/**
 * SM4加密的AES-NI指令集优化实现 - 性能测试程序
 * 
 * 该实现通过Intel AES-NI指令集优化加速SM4算法
 * 性能测量采用统计学方法，包含多次测量和CPU周期计数
 */
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <windows.h>
#include <fcntl.h>
#include <io.h>
#include <vector>
#include <algorithm>
#include <numeric>
#include "mytimer.hpp"
#include "sm4_aesni_x4.h"

using namespace std;

// 全局时间记录变量
double g_encryptionTime;

// 设置控制台支持输出
void SetupConsole() {
    // 设置控制台代码页为GBK
    SetConsoleOutputCP(936);  // 输出代码页
    
    // 获取标准输出句柄
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    
    // 获取当前控制台模式
    DWORD dwMode = 0;
    GetConsoleMode(hOut, &dwMode);
    
    // 启用处理虚拟终端序列
    dwMode |= ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT;
    SetConsoleMode(hOut, dwMode);
}

/**
 * 获取高精度CPU周期计数
 * @return 当前CPU周期计数
 */
__int64 GetCPUCycles() {
    LARGE_INTEGER li;
    QueryPerformanceCounter(&li);
    return li.QuadPart;
}

/**
 * 获取CPU频率（GHz）
 * @return CPU频率，单位GHz
 */
double GetCPUFrequencyGHz() {
    LARGE_INTEGER li;
    QueryPerformanceFrequency(&li);
    return li.QuadPart / 1000000000.0;
}

int main() {
    // 设置控制台
    SetupConsole();
    
    // 标题和说明
    cout << "===========================================" << endl;
    cout << "  SM4 AES-NI Implementation - Results and Performance Test" << endl;
    cout << "===========================================" << endl << endl;
    
    // 测试密钥（128位）
    unsigned char key[16] = { 
        0x02, 0x21, 0x45, 0x47, 0x89, 0xab, 0xcd, 0xef,
        0xbe, 0xde, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae 
    };
    
    // 显示密钥
    cout << "Key: ";
    for (int i = 0; i < 16; i++) {
        if (i > 0 && i % 4 == 0) cout << " ";
        cout << hex << setw(2) << setfill('0') << (int)key[i] << " ";
    }
    cout << dec << setfill(' ') << endl << endl;
    
    // 测试数据（8个128位块，共1024位）
    unsigned char original_data[16 * 8] = { 0 };
    unsigned char data[16 * 8] = { 0 };
    
    // 初始化测试数据
    for (int j = 0; j < 8; j++) {
        for (int i = 0; i < 16; i++) {
            data[i + 16 * j] = original_data[i + 16 * j] = (i + j * 16) % 256;
        }
    }
    
    // 显示原始数据
    cout << "Original Data:" << endl;
    for (int j = 0; j < 8; j++) {
        cout << "\tBlock " << j+1 << ": ";
        for (int i = 0; i < 16; i++) {
            if (i > 0 && i % 4 == 0) cout << " ";
            cout << hex << setw(2) << setfill('0') << (int)data[i + 16 * j] << " ";
        }
        cout << endl;
    }
    cout << dec << setfill(' ') << endl;
    
    // 测量参数设置
    const int WARMUP_RUNS = 100;      // 预热运行次数
    const int MEASUREMENT_RUNS = 1000; // 测量运行次数
    
    // 初始化SM4密钥
    SM4_Key sm4_key;
    SM4_KeyInit(key, &sm4_key);
    
    // 保存原始数据的副本
    unsigned char encrypted_data[16 * 8];
    memcpy(encrypted_data, data, 16 * 8);
    
    // 热身运行，预热CPU缓存
    for (int i = 0; i < WARMUP_RUNS; i++) {
        SM4_AESNI_Encrypt_x8(data, data, &sm4_key);
    }
    
    // 重置数据
    memcpy(data, original_data, 16 * 8);
    
    // 进行单次加密，保存结果用于显示
    mytimer single_timer;
    single_timer.Reset();
    SM4_AESNI_Encrypt_x8(encrypted_data, encrypted_data, &sm4_key);
    single_timer.UpDate();
    double single_encrypt_time = single_timer.GetNanosecond();
    
    // 多次测量加密时间和CPU周期
    vector<double> encryptTimesNs;
    vector<__int64> encryptCycles;
    
    for (int i = 0; i < MEASUREMENT_RUNS; i++) {
        mytimer timer;
        __int64 startCycles = GetCPUCycles();
        
        timer.Reset();
        SM4_AESNI_Encrypt_x8(data, data, &sm4_key);
        timer.UpDate();
        
        double ns = timer.GetNanosecond();
        __int64 endCycles = GetCPUCycles();
        
        encryptTimesNs.push_back(ns);
        encryptCycles.push_back(endCycles - startCycles);
    }
    
    // 显示加密结果
    cout << "Encryption Results (AES-NI):" << endl;
    for (int j = 0; j < 8; j++) {
        cout << "\tBlock " << j+1 << ": ";
        for (int i = 0; i < 16; i++) {
            if (i > 0 && i % 4 == 0) cout << " ";
            cout << hex << setw(2) << setfill('0') << (int)encrypted_data[i + 16 * j] << " ";
        }
        cout << endl;
    }
    cout << dec << setfill(' ') << endl;
    
    // 解密单次运行并显示结果
    unsigned char decrypted_data[16 * 8];
    memcpy(decrypted_data, encrypted_data, 16 * 8);
    
    single_timer.Reset();
    SM4_AESNI_Decrypt_x8(decrypted_data, decrypted_data, &sm4_key);
    single_timer.UpDate();
    double single_decrypt_time = single_timer.GetNanosecond();
    
    // 验证解密结果
    bool decrypt_success = true;
    for (int i = 0; i < 16 * 8; i++) {
        if (original_data[i] != decrypted_data[i]) {
            decrypt_success = false;
            break;
        }
    }
    
    // 显示解密结果
    cout << "Decryption Results (AES-NI):" << endl;
    for (int j = 0; j < 8; j++) {
        cout << "\tBlock " << j+1 << ": ";
        for (int i = 0; i < 16; i++) {
            if (i > 0 && i % 4 == 0) cout << " ";
            cout << hex << setw(2) << setfill('0') << (int)decrypted_data[i + 16 * j] << " ";
        }
        cout << endl;
    }
    cout << dec << setfill(' ') << endl;
    
    // 验证解密是否成功
    cout << "Verification: " << (decrypt_success ? "SUCCESS - Decrypted data matches original data" : "FAILED - Decrypted data does not match original data") << endl;
    cout << endl;
    
    // 多次测量解密时间和CPU周期
    vector<double> decryptTimesNs;
    vector<__int64> decryptCycles;
    
    for (int i = 0; i < MEASUREMENT_RUNS; i++) {
        mytimer timer;
        __int64 startCycles = GetCPUCycles();
        
        timer.Reset();
        SM4_AESNI_Decrypt_x8(encrypted_data, data, &sm4_key);
        timer.UpDate();
        
        double ns = timer.GetNanosecond();
        __int64 endCycles = GetCPUCycles();
        
        decryptTimesNs.push_back(ns);
        decryptCycles.push_back(endCycles - startCycles);
    }
    
    // 计算统计数据
    sort(encryptTimesNs.begin(), encryptTimesNs.end());
    sort(decryptTimesNs.begin(), decryptTimesNs.end());
    sort(encryptCycles.begin(), encryptCycles.end());
    sort(decryptCycles.begin(), decryptCycles.end());
    
    // 计算均值、中位数和最小值
    double avgEncryptNs = accumulate(encryptTimesNs.begin(), encryptTimesNs.end(), 0.0) / MEASUREMENT_RUNS;
    double avgDecryptNs = accumulate(decryptTimesNs.begin(), decryptTimesNs.end(), 0.0) / MEASUREMENT_RUNS;
    double medianEncryptNs = encryptTimesNs[MEASUREMENT_RUNS/2];
    double medianDecryptNs = decryptTimesNs[MEASUREMENT_RUNS/2];
    double minEncryptNs = encryptTimesNs.front();
    double minDecryptNs = decryptTimesNs.front();
    
    __int64 avgEncryptCycles = accumulate(encryptCycles.begin(), encryptCycles.end(), 0LL) / MEASUREMENT_RUNS;
    __int64 avgDecryptCycles = accumulate(decryptCycles.begin(), decryptCycles.end(), 0LL) / MEASUREMENT_RUNS;
    __int64 medianEncryptCycles = encryptCycles[MEASUREMENT_RUNS/2];
    __int64 medianDecryptCycles = decryptCycles[MEASUREMENT_RUNS/2];
    __int64 minEncryptCycles = encryptCycles.front();
    __int64 minDecryptCycles = decryptCycles.front();
    
    // 获取CPU频率
    double cpuFreqGHz = GetCPUFrequencyGHz();
    
    // 设置全局时间记录
    double timeSeconds = avgEncryptNs / 1000000000.0;
    g_encryptionTime = timeSeconds;
    
    // 显示高级性能测量结果
    cout << "===========================================" << endl;
    cout << "  SM4 AES-NI Implementation Performance Results" << endl;
    cout << "===========================================" << endl;
    
    // 计算吞吐量 (使用平均值而非最小值以获得更稳定的结果)
    double encryptNs = avgEncryptNs; // 使用平均值代替最小值
    double decryptNs = avgDecryptNs;
    double encryptThroughput = (16.0 * 8 * 1000000000.0 / encryptNs) / (1024*1024);
    double decryptThroughput = (16.0 * 8 * 1000000000.0 / decryptNs) / (1024*1024);
    
    // 显示详细的性能数据
    cout << "Encryption Time: " << fixed << setprecision(3) << encryptNs << " ns (" 
         << setprecision(9) << encryptNs/1000000000.0 << " s)" << endl;
    cout << "  Min: " << fixed << setprecision(3) << minEncryptNs << " ns" << endl;
    cout << "  Median: " << fixed << setprecision(3) << medianEncryptNs << " ns" << endl;
    cout << "  Cycles: " << avgEncryptCycles << " cycles" << endl;
    
    cout << "Decryption Time: " << fixed << setprecision(3) << decryptNs << " ns (" 
         << setprecision(9) << decryptNs/1000000000.0 << " s)" << endl;
    cout << "  Min: " << fixed << setprecision(3) << minDecryptNs << " ns" << endl;
    cout << "  Median: " << fixed << setprecision(3) << medianDecryptNs << " ns" << endl;
    cout << "  Cycles: " << avgDecryptCycles << " cycles" << endl;
    
    cout << "Time Per Block: " << fixed << setprecision(3) << encryptNs / 8.0 << " ns/block" << endl;
    cout << "Time Per Byte: " << fixed << setprecision(3) << encryptNs / (16.0 * 8) << " ns/byte" << endl;
    cout << "Throughput: " << fixed << setprecision(3) << encryptThroughput << " MB/s" << endl;
    cout << "===========================================" << endl;
    system("pause");
    return 0;
}