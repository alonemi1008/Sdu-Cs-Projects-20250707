#pragma once
#ifndef SM4_AESNI_X4_H
#define SM4_AESNI_X4_H

#include "sm4.h"

/**
 * @brief 使用AES-NI指令集实现的SM4批量加密（8块同时）
 * @param plaintext 输入明文缓冲区，大小为128字节（8个128bit块）
 * @param ciphertext 输出密文缓冲区，大小为128字节
 * @param sm4_key 用于加密的SM4密钥
 */
void SM4_AESNI_Encrypt_x8(uint8_t* plaintext, uint8_t* ciphertext, SM4_Key* sm4_key);

/**
 * @brief 使用AES-NI指令集实现的SM4批量解密（8块同时）
 * @param ciphertext 输入密文缓冲区，大小为128字节（8个128bit块）
 * @param plaintext 输出明文缓冲区，大小为128字节
 * @param sm4_key 用于解密的SM4密钥
 */
void SM4_AESNI_Decrypt_x8(uint8_t* ciphertext, uint8_t* plaintext, SM4_Key* sm4_key);

#endif // !SM4_AESNI_X4_H 