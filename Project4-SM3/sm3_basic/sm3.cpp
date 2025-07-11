#include "sm3.h"

// 初始化SM3上下文
void sm3_init(sm3_context_t *ctx) {
    ctx->count = 0;
    ctx->buffer_len = 0;
    memset(ctx->buffer, 0, SM3_BLOCK_SIZE);
    
    // 设置初始状态
    for (int i = 0; i < 8; i++) {
        ctx->state[i] = SM3_IV[i];
    }
}

// 更新SM3状态
void sm3_update(sm3_context_t *ctx, const uint8_t *data, uint32_t len) {
    uint32_t left = ctx->buffer_len;
    uint32_t fill = SM3_BLOCK_SIZE - left;
    
    ctx->count += len;
    
    // 如果缓冲区加上新数据够一个块
    if (left && len >= fill) {
        memcpy(ctx->buffer + left, data, fill);
        sm3_compress(ctx, ctx->buffer);
        data += fill;
        len -= fill;
        left = 0;
    }
    
    // 处理完整的块
    while (len >= SM3_BLOCK_SIZE) {
        sm3_compress(ctx, data);
        data += SM3_BLOCK_SIZE;
        len -= SM3_BLOCK_SIZE;
    }
    
    // 剩余数据放入缓冲区
    if (len > 0) {
        memcpy(ctx->buffer + left, data, len);
    }
    ctx->buffer_len = left + len;
}

// 完成SM3计算并输出摘要
void sm3_final(sm3_context_t *ctx, uint8_t *digest) {
    sm3_padding(ctx);
    
    // 输出最终的哈希值（大端序）
    for (int i = 0; i < 8; i++) {
        digest[i * 4 + 0] = (ctx->state[i] >> 24) & 0xFF;
        digest[i * 4 + 1] = (ctx->state[i] >> 16) & 0xFF;
        digest[i * 4 + 2] = (ctx->state[i] >> 8) & 0xFF;
        digest[i * 4 + 3] = (ctx->state[i] >> 0) & 0xFF;
    }
}

// 一次性计算SM3哈希
void sm3_hash(const uint8_t *data, uint32_t len, uint8_t *digest) {
    sm3_context_t ctx;
    sm3_init(&ctx);
    sm3_update(&ctx, data, len);
    sm3_final(&ctx, digest);
}

// SM3压缩函数 - 核心算法实现
void sm3_compress(sm3_context_t *ctx, const uint8_t *block) {
    uint32_t W[68];  // 扩展字
    uint32_t W1[64]; // W'
    uint32_t A, B, C, D, E, F, G, H;
    uint32_t SS1, SS2, TT1, TT2;
    uint32_t T;
    
    // 1. 消息扩展
    // 将512位消息分组划分为16个32位字
    for (int i = 0; i < 16; i++) {
        W[i] = ((uint32_t)block[i * 4 + 0] << 24) |
               ((uint32_t)block[i * 4 + 1] << 16) |
               ((uint32_t)block[i * 4 + 2] << 8) |
               ((uint32_t)block[i * 4 + 3] << 0);
    }
    
    // 扩展生成W[16]到W[67]
    for (int j = 16; j < 68; j++) {
        uint32_t temp = W[j-16] ^ W[j-9] ^ ROL(W[j-3], 15);
        W[j] = P1(temp) ^ ROL(W[j-13], 7) ^ W[j-6];
    }
    
    // 生成W'[0]到W'[63]
    for (int j = 0; j < 64; j++) {
        W1[j] = W[j] ^ W[j+4];
    }
    
    // 2. 压缩函数
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

// SM3填充函数
void sm3_padding(sm3_context_t *ctx) {
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
        sm3_compress(ctx, ctx->buffer);
        memset(ctx->buffer, 0, 56);
    }
    
    // 添加64位长度（大端序）
    for (int i = 0; i < 8; i++) {
        ctx->buffer[56 + i] = (bit_len >> (56 - i * 8)) & 0xFF;
    }
    
    sm3_compress(ctx, ctx->buffer);
}

// 工具函数：打印十六进制
void sm3_print_hex(const uint8_t *data, uint32_t len) {
    for (uint32_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

// 工具函数：打印状态
void sm3_print_state(const uint32_t *state) {
    printf("State: ");
    for (int i = 0; i < 8; i++) {
        printf("%08x ", state[i]);
    }
    printf("\n");
} 