pragma circom 2.0.0;

include "./poseidon2_hash.circom";

// 简化的 Poseidon2 证明电路
// 证明知道某个原象，并输出其哈希值作为公开输出
template Poseidon2SimpleProof() {
    // 隐私输入：原象
    signal input preimage[2];
    
    // 公开输出：计算得到的哈希值
    signal output hash;
    
    // 计算哈希
    component hasher = Poseidon2();
    hasher.in[0] <== preimage[0];
    hasher.in[1] <== preimage[1];
    
    // 输出哈希值
    hash <== hasher.out;
}

// 主组件
component main {public []} = Poseidon2SimpleProof(); 