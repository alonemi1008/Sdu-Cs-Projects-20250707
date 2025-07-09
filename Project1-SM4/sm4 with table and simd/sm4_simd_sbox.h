// sm4_simd_sbox.h - SIMD优化的SM4实现

#ifndef SM4_SIMD_SBOX_H
#define SM4_SIMD_SBOX_H

#include <stdint.h>

/**
 * @brief SM4 密钥结构 - SIMD优化版本
 */
typedef uint32_t* SM4_Key;

/**
 * @brief 初始化 SM4 密钥
 * @param key 128bit输入密钥
 * @param sm4_key SM4 密钥指针
 * @return 操作执行成功返回1，失败返回0
 */
int SM4_KeyInit(uint8_t* key, SM4_Key* sm4_key);

/**
 * @brief SM4 批量加密（8块同时），使用SIMD指令集优化
 * @param plaintext 输入128x8bit明文数据
 * @param ciphertext 输出128x8bit密文数据
 * @param sm4_key 用于加密的 SM4 密钥
 */
void SM4_Encrypt_x8(uint8_t* plaintext, uint8_t* ciphertext, SM4_Key sm4_key);

/**
 * @brief SM4 批量解密（8块同时），使用SIMD指令集优化
 * @param ciphertext 输入128x8bit密文数据
 * @param plaintext 输出128x8bit明文数据
 * @param sm4_key 用于解密的 SM4 密钥
 */
void SM4_Decrypt_x8(uint8_t* ciphertext, uint8_t* plaintext, SM4_Key sm4_key);

/**
 * @brief 删除 SM4 密钥，释放分配的内存
 * @param sm4_key SM4 密钥
 */
void SM4_KeyDelete(SM4_Key sm4_key);

#endif // !SM4_SIMD_SBOX_H