pragma circom 2.0.0;

include "./poseidon2_hash.circom";

// 修复版 Poseidon2 证明电路
// 证明知道某个原象，输出其 Poseidon2 哈希值
template Poseidon2ProofFixed() {
    // 隐私输入：原象
    signal input preimage[2];
    
    // 公开输出：计算得到的哈希值
    signal output computedHash;
    
    // 计算 Poseidon2 哈希
    component hasher = Poseidon2();
    hasher.in[0] <== preimage[0];
    hasher.in[1] <== preimage[1];
    
    // 输出计算的哈希值
    computedHash <== hasher.out;
}

// 主组件 - 没有公开输入，只有公开输出
component main = Poseidon2ProofFixed(); 