#pragma once
#ifndef SM4_CORE_H
#define SM4_CORE_H

#include <stdint.h>

/**
 * @brief SM4 密钥结构 - 核心实现
 */
typedef struct _SM4_Key {
    uint32_t rk[32]; // 32轮密钥
} SM4_Key;

/**
 * @brief 初始化 SM4 密钥
 * @param key 128bit输入密钥
 * @param sm4_key SM4 密钥结构指针
 */
void SM4_KeyInit(uint8_t* key, SM4_Key* sm4_key);

#endif // !SM4_CORE_H