#ifndef SM3_H
#define SM3_H

#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

// SM3算法相关常量
#define SM3_DIGEST_SIZE 32
#define SM3_BLOCK_SIZE 64
#define SM3_WORD_SIZE 4

// 基础运算宏定义 - 避免函数调用开销
#define ROL(x, n) (((x) << (n)) | ((x) >> (32 - (n))))
#define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))

// SM3算法专用函数宏定义
#define FF0(x, y, z) ((x) ^ (y) ^ (z))
#define FF1(x, y, z) (((x) & (y)) | ((x) & (z)) | ((y) & (z)))

#define GG0(x, y, z) ((x) ^ (y) ^ (z))
#define GG1(x, y, z) (((x) & (y)) | ((~(x)) & (z)))

#define P0(x) ((x) ^ ROL((x), 9) ^ ROL((x), 17))
#define P1(x) ((x) ^ ROL((x), 15) ^ ROL((x), 23))

// SM3初始值IV
static const uint32_t SM3_IV[8] = {
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
};

// SM3常量T
static const uint32_t SM3_T[2] = {
    0x79CC4519, // T_j for j = 0, 1, ..., 15
    0x7A879D8A  // T_j for j = 16, 17, ..., 63
};

// SM3上下文结构
typedef struct {
    uint32_t state[8];           // 256位中间状态
    uint64_t count;              // 已处理的字节数
    uint8_t buffer[SM3_BLOCK_SIZE]; // 缓冲区
    uint32_t buffer_len;         // 缓冲区中的字节数
} sm3_context_t;

// 函数声明
void sm3_init(sm3_context_t *ctx);
void sm3_update(sm3_context_t *ctx, const uint8_t *data, uint32_t len);
void sm3_final(sm3_context_t *ctx, uint8_t *digest);
void sm3_hash(const uint8_t *data, uint32_t len, uint8_t *digest);

// 内部函数声明
void sm3_compress(sm3_context_t *ctx, const uint8_t *block);
void sm3_padding(sm3_context_t *ctx);

// 工具函数
void sm3_print_hex(const uint8_t *data, uint32_t len);
void sm3_print_state(const uint32_t *state);

#endif // SM3_H 