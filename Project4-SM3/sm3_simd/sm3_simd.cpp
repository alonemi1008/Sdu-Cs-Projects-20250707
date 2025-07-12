#include "sm3_simd.h"

// 初始化SIMD上下文
void sm3_simd_init(sm3_simd_context_t *ctx) {
    ctx->count = 0;
    ctx->buffer_len = 0;
    memset(ctx->buffer, 0, SM3_BLOCK_SIZE);
    
    // 设置初始状态
    for (int i = 0; i < 8; i++) {
        ctx->state[i] = SM3_IV[i];
    }
}

// 更新SIMD上下文
void sm3_simd_update(sm3_simd_context_t *ctx, const uint8_t *data, uint32_t len) {
    uint32_t left = ctx->buffer_len;
    uint32_t fill = SM3_BLOCK_SIZE - left;
    
    ctx->count += len;
    
    // 如果缓冲区加上新数据够一个块
    if (left && len >= fill) {
        memcpy(ctx->buffer + left, data, fill);
        sm3_simd_compress(ctx, ctx->buffer);
        data += fill;
        len -= fill;
        left = 0;
    }
    
    // 处理完整的块
    while (len >= SM3_BLOCK_SIZE) {
        sm3_simd_compress(ctx, data);
        data += SM3_BLOCK_SIZE;
        len -= SM3_BLOCK_SIZE;
    }
    
    // 剩余数据放入缓冲区
    if (len > 0) {
        memcpy(ctx->buffer + left, data, len);
    }
    ctx->buffer_len = left + len;
}

// 完成SIMD计算
void sm3_simd_final(sm3_simd_context_t *ctx, uint8_t *digest) {
    sm3_simd_padding(ctx);
    
    // 输出最终的哈希值（大端序）
    for (int i = 0; i < 8; i++) {
        digest[i * 4 + 0] = (ctx->state[i] >> 24) & 0xFF;
        digest[i * 4 + 1] = (ctx->state[i] >> 16) & 0xFF;
        digest[i * 4 + 2] = (ctx->state[i] >> 8) & 0xFF;
        digest[i * 4 + 3] = (ctx->state[i] >> 0) & 0xFF;
    }
}

// One-time SIMD hash calculation
void sm3_simd_hash(const uint8_t *data, uint32_t len, uint8_t *digest) {
    sm3_simd_context_t ctx;
    sm3_simd_init(&ctx);
    sm3_simd_update(&ctx, data, len);
    sm3_simd_final(&ctx, digest);
}

// SIMD优化的压缩函数 - 单块处理
void sm3_simd_compress(sm3_simd_context_t *ctx, const uint8_t *block) {
    uint32_t W[68] __attribute__((aligned(32)));  // 扩展字，32字节对齐
    uint32_t W1[64] __attribute__((aligned(32))); // W'，32字节对齐
    uint32_t A, B, C, D, E, F, G, H;
    uint32_t SS1, SS2, TT1, TT2;
    uint32_t T;
    
    // 1. 消息扩展 - 使用SIMD优化
    // 将512位消息分组划分为16个32位字
    for (int i = 0; i < 16; i++) {
        W[i] = ((uint32_t)block[i * 4 + 0] << 24) |
               ((uint32_t)block[i * 4 + 1] << 16) |
               ((uint32_t)block[i * 4 + 2] << 8) |
               ((uint32_t)block[i * 4 + 3] << 0);
    }
    
    // 使用SIMD指令扩展生成W[16]到W[67]
    // 每次处理4个字，利用128位寄存器
    for (int j = 16; j < 68; j += 4) {
        __m128i w_minus_16 = _mm_loadu_si128((__m128i*)(W + j - 16));
        __m128i w_minus_9 = _mm_loadu_si128((__m128i*)(W + j - 9));
        __m128i w_minus_3 = _mm_loadu_si128((__m128i*)(W + j - 3));
        __m128i w_minus_13 = _mm_loadu_si128((__m128i*)(W + j - 13));
        __m128i w_minus_6 = _mm_loadu_si128((__m128i*)(W + j - 6));
        
        // temp = W[j-16] ^ W[j-9] ^ ROL(W[j-3], 15)
        __m128i temp = _mm_xor_si128(w_minus_16, w_minus_9);
        temp = _mm_xor_si128(temp, sm3_mm_rol_epi32(w_minus_3, 15));
        
        // W[j] = P1(temp) ^ ROL(W[j-13], 7) ^ W[j-6]
        __m128i result = _mm_xor_si128(sm3_mm_P1_epi32(temp), sm3_mm_rol_epi32(w_minus_13, 7));
        result = _mm_xor_si128(result, w_minus_6);
        
        _mm_storeu_si128((__m128i*)(W + j), result);
    }
    
    // 使用SIMD生成W'[0]到W'[63]
    for (int j = 0; j < 64; j += 4) {
        __m128i w_j = _mm_loadu_si128((__m128i*)(W + j));
        __m128i w_j_plus_4 = _mm_loadu_si128((__m128i*)(W + j + 4));
        __m128i w1_j = _mm_xor_si128(w_j, w_j_plus_4);
        _mm_storeu_si128((__m128i*)(W1 + j), w1_j);
    }
    
    // 2. 压缩函数 - 这部分由于数据依赖较强，仍使用标量实现
    A = ctx->state[0];
    B = ctx->state[1];
    C = ctx->state[2];
    D = ctx->state[3];
    E = ctx->state[4];
    F = ctx->state[5];
    G = ctx->state[6];
    H = ctx->state[7];
    
    for (int j = 0; j < 64; j++) {
        // 选择常量T_j
        T = (j < 16) ? SM3_T[0] : SM3_T[1];
        
        SS1 = ROL((ROL(A, 12) + E + ROL(T, j % 32)), 7);
        SS2 = SS1 ^ ROL(A, 12);
        
        TT1 = ((j < 16) ? FF0(A, B, C) : FF1(A, B, C)) + D + SS2 + W1[j];
        TT2 = ((j < 16) ? GG0(E, F, G) : GG1(E, F, G)) + H + SS1 + W[j];
        
        D = C;
        C = ROL(B, 9);
        B = A;
        A = TT1;
        H = G;
        G = ROL(F, 19);
        F = E;
        E = P0(TT2);
    }
    
    // 3. 更新状态
    ctx->state[0] ^= A;
    ctx->state[1] ^= B;
    ctx->state[2] ^= C;
    ctx->state[3] ^= D;
    ctx->state[4] ^= E;
    ctx->state[5] ^= F;
    ctx->state[6] ^= G;
    ctx->state[7] ^= H;
}

// 4块并行处理的SIMD压缩函数
void sm3_simd_compress_4blocks(const uint8_t *blocks[4], uint32_t states[4][8]) {
    uint32_t W[4][68] __attribute__((aligned(32)));  // 4组扩展字
    uint32_t W1[4][64] __attribute__((aligned(32))); // 4组W'
    
    // 1. 消息扩展 - 4块并行处理
    for (int blk = 0; blk < 4; blk++) {
        for (int i = 0; i < 16; i++) {
            W[blk][i] = ((uint32_t)blocks[blk][i * 4 + 0] << 24) |
                        ((uint32_t)blocks[blk][i * 4 + 1] << 16) |
                        ((uint32_t)blocks[blk][i * 4 + 2] << 8) |
                        ((uint32_t)blocks[blk][i * 4 + 3] << 0);
        }
    }
    
    // 使用SIMD扩展生成W[16]到W[67] - 交错处理4块数据
    for (int j = 16; j < 68; j += 4) {
        // 加载4个块的对应数据到SIMD寄存器
        __m128i w0_minus_16 = _mm_set_epi32(W[3][j-16], W[2][j-16], W[1][j-16], W[0][j-16]);
        __m128i w0_minus_9 = _mm_set_epi32(W[3][j-9], W[2][j-9], W[1][j-9], W[0][j-9]);
        __m128i w0_minus_3 = _mm_set_epi32(W[3][j-3], W[2][j-3], W[1][j-3], W[0][j-3]);
        __m128i w0_minus_13 = _mm_set_epi32(W[3][j-13], W[2][j-13], W[1][j-13], W[0][j-13]);
        __m128i w0_minus_6 = _mm_set_epi32(W[3][j-6], W[2][j-6], W[1][j-6], W[0][j-6]);
        
        for (int k = 0; k < 4 && j + k < 68; k++) {
            // 计算当前位置的扩展字
            __m128i temp = _mm_xor_si128(w0_minus_16, w0_minus_9);
            temp = _mm_xor_si128(temp, sm3_mm_rol_epi32(w0_minus_3, 15));
            
            __m128i result = _mm_xor_si128(sm3_mm_P1_epi32(temp), sm3_mm_rol_epi32(w0_minus_13, 7));
            result = _mm_xor_si128(result, w0_minus_6);
            
            // 存储结果到各个块
            uint32_t values[4];
            _mm_storeu_si128((__m128i*)values, result);
            for (int blk = 0; blk < 4; blk++) {
                if (j + k < 68) {
                    W[blk][j + k] = values[blk];
                }
            }
            
            // 更新寄存器以处理下一个位置
            if (k < 3) {
                w0_minus_16 = _mm_set_epi32(W[3][j-16+k+1], W[2][j-16+k+1], W[1][j-16+k+1], W[0][j-16+k+1]);
                w0_minus_9 = _mm_set_epi32(W[3][j-9+k+1], W[2][j-9+k+1], W[1][j-9+k+1], W[0][j-9+k+1]);
                w0_minus_3 = _mm_set_epi32(W[3][j-3+k+1], W[2][j-3+k+1], W[1][j-3+k+1], W[0][j-3+k+1]);
                w0_minus_13 = _mm_set_epi32(W[3][j-13+k+1], W[2][j-13+k+1], W[1][j-13+k+1], W[0][j-13+k+1]);
                w0_minus_6 = _mm_set_epi32(W[3][j-6+k+1], W[2][j-6+k+1], W[1][j-6+k+1], W[0][j-6+k+1]);
            }
        }
    }
    
    // 生成W'数组
    for (int blk = 0; blk < 4; blk++) {
        for (int j = 0; j < 64; j += 4) {
            __m128i w_j = _mm_loadu_si128((__m128i*)(W[blk] + j));
            __m128i w_j_plus_4 = _mm_loadu_si128((__m128i*)(W[blk] + j + 4));
            __m128i w1_j = _mm_xor_si128(w_j, w_j_plus_4);
            _mm_storeu_si128((__m128i*)(W1[blk] + j), w1_j);
        }
    }
    
    // 2. 压缩函数 - 4块并行处理
    uint32_t A[4], B[4], C[4], D[4], E[4], F[4], G[4], H[4];
    
    // 初始化状态
    for (int blk = 0; blk < 4; blk++) {
        A[blk] = states[blk][0];
        B[blk] = states[blk][1];
        C[blk] = states[blk][2];
        D[blk] = states[blk][3];
        E[blk] = states[blk][4];
        F[blk] = states[blk][5];
        G[blk] = states[blk][6];
        H[blk] = states[blk][7];
    }
    
    for (int j = 0; j < 64; j++) {
        uint32_t T = (j < 16) ? SM3_T[0] : SM3_T[1];
        
        for (int blk = 0; blk < 4; blk++) {
            uint32_t SS1 = ROL((ROL(A[blk], 12) + E[blk] + ROL(T, j % 32)), 7);
            uint32_t SS2 = SS1 ^ ROL(A[blk], 12);
            
            uint32_t TT1 = ((j < 16) ? FF0(A[blk], B[blk], C[blk]) : FF1(A[blk], B[blk], C[blk])) + D[blk] + SS2 + W1[blk][j];
            uint32_t TT2 = ((j < 16) ? GG0(E[blk], F[blk], G[blk]) : GG1(E[blk], F[blk], G[blk])) + H[blk] + SS1 + W[blk][j];
            
            D[blk] = C[blk];
            C[blk] = ROL(B[blk], 9);
            B[blk] = A[blk];
            A[blk] = TT1;
            H[blk] = G[blk];
            G[blk] = ROL(F[blk], 19);
            F[blk] = E[blk];
            E[blk] = P0(TT2);
        }
    }
    
    // 3. 更新状态
    for (int blk = 0; blk < 4; blk++) {
        states[blk][0] ^= A[blk];
        states[blk][1] ^= B[blk];
        states[blk][2] ^= C[blk];
        states[blk][3] ^= D[blk];
        states[blk][4] ^= E[blk];
        states[blk][5] ^= F[blk];
        states[blk][6] ^= G[blk];
        states[blk][7] ^= H[blk];
    }
}

// SIMD填充函数
void sm3_simd_padding(sm3_simd_context_t *ctx) {
    uint64_t bit_len = ctx->count * 8;
    uint32_t pad_len;
    
    // 添加0x80
    ctx->buffer[ctx->buffer_len] = 0x80;
    
    // 计算需要填充的长度
    if (ctx->buffer_len < 56) {
        pad_len = 56 - ctx->buffer_len - 1;
    } else {
        pad_len = 120 - ctx->buffer_len - 1;
    }
    
    // 填充0
    memset(ctx->buffer + ctx->buffer_len + 1, 0, pad_len);
    
    // 如果需要额外的块
    if (ctx->buffer_len >= 56) {
        sm3_simd_compress(ctx, ctx->buffer);
        memset(ctx->buffer, 0, 56);
    }
    
    // 添加64位长度（大端序）
    for (int i = 0; i < 8; i++) {
        ctx->buffer[56 + i] = (bit_len >> (56 - i * 8)) & 0xFF;
    }
    
    sm3_simd_compress(ctx, ctx->buffer);
}

// 多块并行处理函数
void sm3_simd_multi_hash(const uint8_t **data, const uint32_t *lens, uint8_t **digests, uint32_t count) {
    // 简化实现：分批处理4块
    for (uint32_t i = 0; i < count; i += 4) {
        uint32_t batch_size = (count - i < 4) ? (count - i) : 4;
        const uint8_t *blocks[4];
        uint32_t states[4][8];
        
        // 初始化状态
        for (uint32_t j = 0; j < batch_size; j++) {
            blocks[j] = data[i + j];
            for (int k = 0; k < 8; k++) {
                states[j][k] = SM3_IV[k];
            }
        }
        
        // 简化处理：只处理完整块
        uint32_t min_blocks = lens[i] / SM3_BLOCK_SIZE;
        for (uint32_t j = 1; j < batch_size; j++) {
            uint32_t blocks_j = lens[i + j] / SM3_BLOCK_SIZE;
            if (blocks_j < min_blocks) {
                min_blocks = blocks_j;
            }
        }
        
        // 处理完整块
        for (uint32_t block = 0; block < min_blocks; block++) {
            const uint8_t *current_blocks[4];
            for (uint32_t j = 0; j < batch_size; j++) {
                current_blocks[j] = blocks[j] + block * SM3_BLOCK_SIZE;
            }
            sm3_simd_compress_4blocks(current_blocks, states);
        }
        
        // 输出结果（简化版本，不包含填充）
        for (uint32_t j = 0; j < batch_size; j++) {
            for (int k = 0; k < 8; k++) {
                digests[i + j][k * 4 + 0] = (states[j][k] >> 24) & 0xFF;
                digests[i + j][k * 4 + 1] = (states[j][k] >> 16) & 0xFF;
                digests[i + j][k * 4 + 2] = (states[j][k] >> 8) & 0xFF;
                digests[i + j][k * 4 + 3] = (states[j][k] >> 0) & 0xFF;
            }
        }
    }
}

// 工具函数
void sm3_simd_print_hex(const uint8_t *data, uint32_t len) {
    for (uint32_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

void sm3_simd_print_state(const uint32_t *state) {
    printf("State: ");
    for (int i = 0; i < 8; i++) {
        printf("%08x ", state[i]);
    }
    printf("\n");
} 