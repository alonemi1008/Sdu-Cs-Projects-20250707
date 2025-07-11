const fs = require("fs");
const snarkjs = require("snarkjs");
const { computeHash } = require("./compute_hash.js");

async function generateProof() {
    console.log("开始生成 Poseidon2 哈希零知识证明...\n");
    
    try {
        // Example input data
        const preimage = [
            "1234567890123456789",  // First element of preimage
            "9876543210987654321"   // Second element of preimage
        ];
        
        console.log("输入数据:");
        console.log(`   原象 (preimage): [${preimage[0]}, ${preimage[1]}]`);
        
        // Step 1: Prepare input
        console.log("\n步骤 1: 准备输入数据");
        
        const input = {
            preimage: preimage
        };
        
        console.log("   输入数据准备完成");
        
        // Save input to file
        fs.writeFileSync("../input/input.json", JSON.stringify(input, null, 2));
        console.log("输入文件已保存到 input/input.json");
        
        // Step 2: Generate witness using WASM
        console.log("\n步骤 2: 生成见证文件...");
        const { exec } = require("child_process");
        const util = require("util");
        const execAsync = util.promisify(exec);
        
        await execAsync("node ../build/poseidon2_proof_fixed_js/generate_witness.js ../build/poseidon2_proof_fixed_js/poseidon2_proof_fixed.wasm ../input/input.json ../output/witness.wtns");
        console.log("见证文件生成完成");
        
        // Step 3: Generate proof
        console.log("\n步骤 3: 生成 Groth16 证明");
        console.log("正在计算证明... (这可能需要一些时间)");
        
        const { proof, publicSignals } = await snarkjs.groth16.prove("../keys/poseidon2_0001.zkey", "../output/witness.wtns");
        
        console.log("证明生成完成!");
        
        // Step 4: Save proof and public signals
        console.log("\n步骤 4: 保存证明文件");
        
        const proofData = {
            proof: proof,
            publicSignals: publicSignals
        };
        
        fs.writeFileSync("../output/proof.json", JSON.stringify(proofData, null, 2));
        console.log("证明已保存到 output/proof.json");
        
        // Display proof information
        console.log("\n证明信息:");
        console.log("   公开输出 (计算的哈希值):");
        publicSignals.forEach((signal, index) => {
            console.log(`      [${index}]: ${signal}`);
        });
        
        console.log("\n   证明数据:");
        console.log(`      π_a: [${proof.pi_a[0]}, ${proof.pi_a[1]}]`);
        console.log(`      π_b: [[${proof.pi_b[0][0]}, ${proof.pi_b[0][1]}], [${proof.pi_b[1][0]}, ${proof.pi_b[1][1]}]]`);
        console.log(`      π_c: [${proof.pi_c[0]}, ${proof.pi_c[1]}]`);
        
        console.log("\n证明生成完成!");
        console.log("\n下一步:");
        console.log("   运行 'npm run verify' 验证此证明");
        console.log("   或使用 'node scripts/verify.js' 验证");
        
        console.log("\n说明:");
        console.log("   此证明表明你知道某个秘密原象，能够产生公开的 Poseidon2 哈希值");
        console.log("   验证者可以验证证明的有效性，但无法获知具体的原象值");
        
    } catch (error) {
        console.error("证明生成失败:", error.message);
        
        if (error.message.includes("witness")) {
            console.error("\n可能的解决方案:");
            console.error("   1. 检查输入数据格式是否正确");
            console.error("   2. 确保电路已正确编译");
            console.error("   3. 运行 'npm run setup' 重新设置电路");
        } else if (error.message.includes("zkey")) {
            console.error("\n可能的解决方案:");
            console.error("   1. 确保 trusted setup 已完成");
            console.error("   2. 运行 'npm run setup' 生成密钥文件");
        }
        
        process.exit(1);
    }
}

// Run proof generation
if (require.main === module) {
    generateProof();
}

module.exports = { generateProof }; 