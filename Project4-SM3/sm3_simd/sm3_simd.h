#ifndef SM3_SIMD_H
#define SM3_SIMD_H

#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>  // AVX2/SSE指令集

// SM3算法相关常量
#define SM3_DIGEST_SIZE 32
#define SM3_BLOCK_SIZE 64
#define SM3_WORD_SIZE 4

// SIMD并行处理数量
#define SIMD_LANES 4    // 128位寄存器可处理4个32位整数
#define SIMD_LANES_256 8 // 256位寄存器可处理8个32位整数

// 基础运算宏定义
#define ROL(x, n) (((x) << (n)) | ((x) >> (32 - (n))))
#define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))

// SM3算法专用函数宏定义
#define FF0(x, y, z) ((x) ^ (y) ^ (z))
#define FF1(x, y, z) (((x) & (y)) | ((x) & (z)) | ((y) & (z)))

#define GG0(x, y, z) ((x) ^ (y) ^ (z))
#define GG1(x, y, z) (((x) & (y)) | ((~(x)) & (z)))

#define P0(x) ((x) ^ ROL((x), 9) ^ ROL((x), 17))
#define P1(x) ((x) ^ ROL((x), 15) ^ ROL((x), 23))

// SIMD版本的旋转运算
static inline __m128i _mm_rol_epi32(__m128i x, int k) {
    return _mm_or_si128(_mm_slli_epi32(x, k), _mm_srli_epi32(x, 32 - k));
}

static inline __m256i _mm256_rol_epi32(__m256i x, int k) {
    return _mm256_or_si256(_mm256_slli_epi32(x, k), _mm256_srli_epi32(x, 32 - k));
}

// SIMD版本的P0和P1函数
static inline __m128i _mm_P0_epi32(__m128i x) {
    return _mm_xor_si128(_mm_xor_si128(x, _mm_rol_epi32(x, 9)), _mm_rol_epi32(x, 17));
}

static inline __m128i _mm_P1_epi32(__m128i x) {
    return _mm_xor_si128(_mm_xor_si128(x, _mm_rol_epi32(x, 15)), _mm_rol_epi32(x, 23));
}

static inline __m256i _mm256_P0_epi32(__m256i x) {
    return _mm256_xor_si256(_mm256_xor_si256(x, _mm256_rol_epi32(x, 9)), _mm256_rol_epi32(x, 17));
}

static inline __m256i _mm256_P1_epi32(__m256i x) {
    return _mm256_xor_si256(_mm256_xor_si256(x, _mm256_rol_epi32(x, 15)), _mm256_rol_epi32(x, 23));
}

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
    uint32_t state[8];              // 256位中间状态
    uint64_t count;                 // 已处理的字节数
    uint8_t buffer[SM3_BLOCK_SIZE]; // 缓冲区
    uint32_t buffer_len;            // 缓冲区中的字节数
} sm3_simd_context_t;

// 多块并行处理的上下文
typedef struct {
    uint32_t state[8 * SIMD_LANES_256]; // 8路并行状态
    uint64_t count[SIMD_LANES_256];     // 每路的计数
    uint8_t buffer[SM3_BLOCK_SIZE * SIMD_LANES_256]; // 并行缓冲区
    uint32_t buffer_len[SIMD_LANES_256]; // 每路缓冲区长度
    uint32_t lanes;                      // 实际使用的并行路数
} sm3_simd_multi_context_t;

// 函数声明
void sm3_simd_init(sm3_simd_context_t *ctx);
void sm3_simd_update(sm3_simd_context_t *ctx, const uint8_t *data, uint32_t len);
void sm3_simd_final(sm3_simd_context_t *ctx, uint8_t *digest);
void sm3_simd_hash(const uint8_t *data, uint32_t len, uint8_t *digest);

// 多块并行处理函数
void sm3_simd_multi_init(sm3_simd_multi_context_t *ctx, uint32_t lanes);
void sm3_simd_multi_update(sm3_simd_multi_context_t *ctx, const uint8_t **data, const uint32_t *lens, uint32_t count);
void sm3_simd_multi_final(sm3_simd_multi_context_t *ctx, uint8_t **digests);
void sm3_simd_multi_hash(const uint8_t **data, const uint32_t *lens, uint8_t **digests, uint32_t count);

// 内部函数声明
void sm3_simd_compress(sm3_simd_context_t *ctx, const uint8_t *block);
void sm3_simd_compress_4blocks(const uint8_t *blocks[4], uint32_t states[4][8]);
void sm3_simd_compress_8blocks(const uint8_t *blocks[8], uint32_t states[8][8]);
void sm3_simd_padding(sm3_simd_context_t *ctx);

// 工具函数
void sm3_simd_print_hex(const uint8_t *data, uint32_t len);
void sm3_simd_print_state(const uint32_t *state);

// 性能测试函数
void sm3_simd_benchmark_single();
void sm3_simd_benchmark_parallel();
void sm3_simd_benchmark_comparison();

#endif // SM3_SIMD_H 