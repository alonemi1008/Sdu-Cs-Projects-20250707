/**
 * SM4加密的SIMD优化实现 - 性能测试程序
 * 
 * 该实现通过SIMD指令集优化加速SM4算法，可同时处理8个数据块
 */
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <windows.h>
#include <fcntl.h>
#include <io.h>
#include "mytimer.hpp"
#include "sm4_simd_sbox.h"
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

int main() {
    // 设置控制台
    SetupConsole();
    
    // 标题和说明
    cout << "===========================================" << endl;
    cout << "  SM4 SIMD Implementation - Results and Performance Test" << endl;
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
    unsigned char original_data[16*8] = { 
        // 块1
        0x02, 0x21, 0x45, 0x47, 0x89, 0xab, 0xcd, 0xef,
        0xbe, 0xde, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae,
        // 块2
        0x01, 0x21, 0x45, 0x47, 0x89, 0xab, 0xcd, 0xef,
        0xbe, 0xde, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae,
        // 块3
        0x03, 0x21, 0x45, 0x43, 0x89, 0xab, 0x6d, 0xef,
        0xb1, 0xde, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae,
        // 块4
        0xb2, 0x21, 0x46, 0x46, 0x89, 0xa5, 0xcd, 0xef,
        0xbe, 0xde, 0xba, 0x08, 0x45, 0x47, 0x89, 0xae,
        // 块5
        0xac, 0xc5, 0x42, 0x47, 0x89, 0xab, 0xcd, 0xef,
        0xbe, 0xde, 0x6a, 0x08, 0x70, 0x58, 0x11, 0xae,
        // 块6
        0x89, 0x28, 0x01, 0x67, 0x89, 0xab, 0xcd, 0xef,
        0xbe, 0xee, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae,
        // 块7
        0x33, 0x41, 0xc0, 0x45, 0x89, 0xab, 0xcd, 0xef,
        0xbe, 0xdd, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae,
        // 块8
        0x12, 0x21, 0x45, 0x57, 0x89, 0xcb, 0xcd, 0xef,
        0xbe, 0xde, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae 
    };
    
    // 复制原始数据
    unsigned char data[16*8];
    memcpy(data, original_data, 16*8);
    
    // 显示原始数据
    cout << "Original Data (8 blocks):" << endl;
    for (int j = 0; j < 8; j++) {
        cout << "\tBlock " << j+1 << ": ";
        for (int i = 0; i < 16; i++) {
            if (i > 0 && i % 4 == 0) cout << " ";
            cout << hex << setw(2) << setfill('0') << (int)data[i + 16 * j] << " ";
        }
        cout << endl;
    }
    cout << dec << setfill(' ') << endl;
    
    // 初始化SM4密钥
    SM4_Key sm4_key;
    int success = SM4_KeyInit(key, &sm4_key);
    
    if (success) {
        // 测量加密时间
        mytimer timer;
        timer.Reset();
        SM4_Encrypt_x8(data, data, sm4_key);
        timer.UpDate();
        double timeSeconds = timer.GetSecond();
        double timeNanoseconds = timer.GetNanosecond();
        g_encryptionTime = timeSeconds;
        
        // 保存加密结果
        unsigned char encrypted_data[16*8];
        memcpy(encrypted_data, data, 16*8);
        
        // 显示加密结果
        cout << "Encryption Results (8 blocks):" << endl;
        for (int j = 0; j < 8; j++) {
            cout << "\tBlock " << j+1 << ": ";
            for (int i = 0; i < 16; i++) {
                if (i > 0 && i % 4 == 0) cout << " ";
                cout << hex << setw(2) << setfill('0') << (int)data[i + 16 * j] << " ";
            }
            cout << endl;
        }
        cout << dec << setfill(' ') << endl;

        // 测量解密时间
        timer.Reset();
        SM4_Decrypt_x8(data, data, sm4_key);
        timer.UpDate();
        double decryptTime = timer.GetMicrosecond();
        
        // 显示解密结果
        cout << "Decryption Results (8 blocks):" << endl;
        for (int j = 0; j < 8; j++) {
            cout << "\tBlock " << j+1 << ": ";
            for (int i = 0; i < 16; i++) {
                if (i > 0 && i % 4 == 0) cout << " ";
                cout << hex << setw(2) << setfill('0') << (int)data[i + 16 * j] << " ";
            }
            cout << endl;
        }
        cout << dec << setfill(' ') << endl;
        
        // 验证解密是否成功
        bool decrypt_success = true;
        for (int i = 0; i < 16*8; i++) {
            if (original_data[i] != data[i]) {
                decrypt_success = false;
                break;
            }
        }
        cout << "Verification: " << (decrypt_success ? "SUCCESS - Decrypted data matches original data" : "FAILED - Decrypted data does not match original data") << endl;
        cout << endl;
        
        // 清理密钥
        SM4_KeyDelete(sm4_key);
        
        // 显示性能测量结果
        cout << "===========================================" << endl;
        cout << "  SM4 SIMD Implementation Performance Results" << endl;
        cout << "===========================================" << endl;
        cout << "Encryption Time: " << fixed << setprecision(3) << timeNanoseconds << " ns (" 
             << setprecision(9) << timeSeconds << " s)" << endl;
        cout << "Decryption Time: " << fixed << setprecision(3) << decryptTime << " us" << endl;
        cout << "Time Per Block: " << fixed << setprecision(3) << timeNanoseconds / 8.0 << " ns/block" << endl;
        cout << "Time Per Byte: " << fixed << setprecision(3) << timeNanoseconds / (16.0 * 8) << " ns/byte" << endl;
        cout << "Throughput: " << fixed << setprecision(3) << (16.0 * 8 * 1000000000.0 / timeNanoseconds) / (1024*1024) << " MB/s" << endl;
        cout << "===========================================" << endl;
    }
    
    system("pause");
    return 0;
}