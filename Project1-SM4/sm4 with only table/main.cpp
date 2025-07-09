/**
 * SM4加密的基础表查找实现 - 性能测试程序
 * 
 * 该实现使用查表法加速SM4算法，处理单个数据块
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
#include "SM4.h"
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
    cout << "  SM4 Table-based Implementation - Results and Performance Test" << endl;
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
    
    // 测试数据（单个128位块）
    unsigned char original_data[16] = { 
        0x02, 0x21, 0x45, 0x47, 0x89, 0xab, 0xcd, 0xef,
        0xbe, 0xde, 0xba, 0x08, 0x70, 0x58, 0x11, 0xae 
    };
    
    // 复制原始数据
    unsigned char data[16];
    memcpy(data, original_data, 16);
    
    // 显示原始数据
    cout << "Original Data:" << endl;
    cout << "\tBlock: ";
    for (int i = 0; i < 16; i++) {
        if (i > 0 && i % 4 == 0) cout << " ";
        cout << hex << setw(2) << setfill('0') << (int)data[i] << " ";
    }
    cout << dec << setfill(' ') << endl << endl;
    
    // 初始化SM4密钥
    SM4_Key sm4_key;
    SM4_KeyInit(key, &sm4_key);
    
    // 测量加密时间
    mytimer timer;
    timer.Reset();
    SM4_Encrypt(data, data, sm4_key);
    timer.UpDate();
    double timeSeconds = timer.GetSecond();
    double timeNanoseconds = timer.GetNanosecond();
    g_encryptionTime = timeSeconds;
    
    // 保存加密结果
    unsigned char encrypted_data[16];
    memcpy(encrypted_data, data, 16);
    
    // 显示加密结果
    cout << "Encryption Results:" << endl;
    cout << "\tBlock: ";
    for (int i = 0; i < 16; i++) {
        if (i > 0 && i % 4 == 0) cout << " ";
        cout << hex << setw(2) << setfill('0') << (int)data[i] << " ";
    }
    cout << dec << setfill(' ') << endl << endl;
    
    // 测量解密时间
    timer.Reset();
    SM4_Decrypt(data, data, sm4_key);
    timer.UpDate();
    double decryptTime = timer.GetMicrosecond();
    
    // 显示解密结果
    cout << "Decryption Results:" << endl;
    cout << "\tBlock: ";
    for (int i = 0; i < 16; i++) {
        if (i > 0 && i % 4 == 0) cout << " ";
        cout << hex << setw(2) << setfill('0') << (int)data[i] << " ";
    }
    cout << dec << setfill(' ') << endl << endl;
    
    // 验证解密是否成功
    bool decrypt_success = true;
    for (int i = 0; i < 16; i++) {
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
    cout << "  SM4 Table-based Performance Results" << endl;
    cout << "===========================================" << endl;
    cout << "Encryption Time: " << fixed << setprecision(3) << timeNanoseconds << " ns (" 
         << setprecision(9) << timeSeconds << " s)" << endl;
    cout << "Decryption Time: " << fixed << setprecision(3) << decryptTime << " us" << endl;
    cout << "Time Per Block: " << fixed << setprecision(3) << timeNanoseconds << " ns/block" << endl;
    cout << "Time Per Byte: " << fixed << setprecision(3) << timeNanoseconds / 16.0 << " ns/byte" << endl;
    cout << "Throughput: " << fixed << setprecision(3) << (16.0 * 1000000000.0 / timeNanoseconds) / (1024*1024) << " MB/s" << endl;
    cout << "===========================================" << endl;
    
    system("pause");
    return 0;
}