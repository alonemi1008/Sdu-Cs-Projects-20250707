const fs = require("fs");
const snarkjs = require("snarkjs");

async function verifyProof() {
    console.log("开始验证 Poseidon2 哈希零知识证明...\n");
    
    try {
        // Step 1: Load verification key
        console.log("步骤 1: 加载验证密钥");
        
        if (!fs.existsSync("../keys/verification_key.json")) {
            throw new Error("验证密钥文件不存在。请先运行 'npm run setup'");
        }
        
        const vKey = JSON.parse(fs.readFileSync("../keys/verification_key.json"));
        console.log("验证密钥加载成功");
        
        // Step 2: Load proof
        console.log("\n步骤 2: 加载证明数据");
        
        if (!fs.existsSync("../output/proof.json")) {
            throw new Error("证明文件不存在。请先运行 'npm run prove' 生成证明");
        }
        
        const proofData = JSON.parse(fs.readFileSync("../output/proof.json"));
        const proof = proofData.proof;
        const publicSignals = proofData.publicSignals;
        
        console.log("证明数据加载成功");
        console.log(`   公开输出数量: ${publicSignals.length}`);
        console.log(`   计算的哈希值: ${publicSignals[0]}`);
        
        // Step 3: Verify proof
        console.log("\n步骤 3: 验证证明");
        console.log("正在验证... (这通常很快)");
        
        const startTime = Date.now();
        const isValid = await snarkjs.groth16.verify(vKey, publicSignals, proof);
        const verificationTime = Date.now() - startTime;
        
        console.log(`验证完成 (耗时: ${verificationTime}ms)`);
        
        // Step 4: Display results
        console.log("\n验证结果:");
        
        if (isValid) {
            console.log("   证明有效!");
            console.log("   证明者确实知道正确的原象");
            console.log("   证明在密码学上是安全的");
            
            console.log("\n这意味着:");
            console.log("   • 证明者拥有某个秘密值 (原象)");
            console.log("   • 该秘密值通过 Poseidon2 哈希产生了公开的哈希值");
            console.log("   • 验证者无法从证明中获取原象信息");
            console.log("   • 证明无法被伪造");
            
        } else {
            console.log("   证明无效!");
            console.log("   证明者不知道正确的原象，或证明已被篡改");
            
            console.log("\n可能的原因:");
            console.log("   • 使用了错误的原象");
            console.log("   • 证明文件已损坏");
            console.log("   • 验证密钥不匹配");
            console.log("   • 公开输入不正确");
        }
        
        // Step 5: Technical details
        console.log("\n技术详情:");
        console.log(`   验证密钥类型: Groth16`);
        console.log(`   椭圆曲线: BN128`);
        console.log(`   公开输出: ${publicSignals.length} 个字段元素`);
        console.log(`   验证时间: ${verificationTime}ms`);
        
        // Display proof structure
        console.log("\n证明结构:");
        console.log(`   π_a: [${proof.pi_a[0].substring(0, 20)}..., ${proof.pi_a[1].substring(0, 20)}...]`);
        console.log(`   π_b: 2x2 矩阵 (省略显示)`);
        console.log(`   π_c: [${proof.pi_c[0].substring(0, 20)}..., ${proof.pi_c[1].substring(0, 20)}...]`);
        
        if (isValid) {
            console.log("\n验证成功完成!");
            return true;
        } else {
            console.log("\n验证失败!");
            return false;
        }
        
    } catch (error) {
        console.error("验证过程中发生错误:", error.message);
        
        if (error.message.includes("verification_key")) {
            console.error("\n解决方案:");
            console.error("   运行 'npm run setup' 生成验证密钥");
        } else if (error.message.includes("proof.json")) {
            console.error("\n解决方案:");
            console.error("   运行 'npm run prove' 生成证明");
        } else {
            console.error("\n调试提示:");
            console.error("   1. 检查所有依赖文件是否存在");
            console.error("   2. 确保证明和验证密钥版本匹配");
            console.error("   3. 检查输入数据格式");
        }
        
        process.exit(1);
    }
}

// Run verification
if (require.main === module) {
    verifyProof().then(result => {
        process.exit(result ? 0 : 1);
    });
}

module.exports = { verifyProof }; 