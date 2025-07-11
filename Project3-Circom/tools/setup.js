const fs = require("fs");
const snarkjs = require("snarkjs");
const circomlib = require("circomlib");
const { exec } = require("child_process");
const util = require("util");

const execAsync = util.promisify(exec);

async function setup() {
    console.log("开始 Poseidon2 电路设置过程...\n");
    
    try {
        // Step 1: Compile circuit
        console.log("步骤 1: 编译 Circom 电路");
        console.log("编译 poseidon2_proof.circom...");
        
        const compileCmd = "..\\bin\\circom.exe ../circuits/poseidon2_proof_fixed.circom --r1cs --wasm --sym --c -o ../build/";
        await execAsync(compileCmd);
        console.log("电路编译完成\n");
        
        // Step 2: Check circuit info
        console.log("步骤 2: 获取电路信息");
        const { stdout: infoOutput } = await execAsync("snarkjs r1cs info ../build/poseidon2_proof_fixed.r1cs");
        console.log(infoOutput);
        
        // Step 3: Generate powers of tau (ceremony phase 1)
        console.log("步骤 3: 生成 Powers of Tau (通用设置)");
        console.log("这可能需要几分钟时间...");
        
        const potFile = "../keys/powersOfTau28_hez_final_16.ptau";
        
        // Check if powers of tau file exists, if not create one
        if (!fs.existsSync(potFile)) {
            console.log("创建新的 Powers of Tau 文件...");
            await execAsync("snarkjs powersoftau new bn128 16 pot16_0000.ptau -v");
            await execAsync("snarkjs powersoftau contribute pot16_0000.ptau pot16_0001.ptau --name=\"First contribution\" -v -e=\"random text\"");
            await execAsync("snarkjs powersoftau beacon pot16_0001.ptau pot16_beacon.ptau 0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f 10 -n=\"Final Beacon\"");
            await execAsync("snarkjs powersoftau prepare phase2 pot16_beacon.ptau ../keys/powersOfTau28_hez_final_16.ptau -v");
            
            // Cleanup intermediate files
            fs.unlinkSync("pot16_0000.ptau");
            fs.unlinkSync("pot16_0001.ptau");
            fs.unlinkSync("pot16_beacon.ptau");
        } else {
            console.log("Powers of Tau 文件已存在");
        }
        
        // Step 4: Generate zkey (circuit specific setup)
        console.log("\n步骤 4: 生成电路特定密钥");
        await execAsync(`snarkjs groth16 setup ../build/poseidon2_proof_fixed.r1cs ${potFile} ../keys/poseidon2_0000.zkey`);
        console.log("初始密钥生成完成");
        
        // Step 5: Contribute to ceremony (phase 2)
        console.log("\n步骤 5: 参与可信设置仪式");
        await execAsync("snarkjs zkey contribute ../keys/poseidon2_0000.zkey ../keys/poseidon2_0001.zkey --name=\"1st Contributor\" -v -e=\"Another random text\"");
        console.log("贡献完成");
        
        // Step 6: Export verification key
        console.log("\n步骤 6: 导出验证密钥");
        await execAsync("snarkjs zkey export verificationkey ../keys/poseidon2_0001.zkey ../keys/verification_key.json");
        console.log("验证密钥已导出");
        
        // Clean up intermediate files
        fs.unlinkSync("../keys/poseidon2_0000.zkey");
        
        console.log("\n设置完成! 生成的文件:");
        console.log("   poseidon2_proof.r1cs - 约束系统");
        console.log("   poseidon2_proof_js/ - WASM 见证生成器");
        console.log("   poseidon2_0001.zkey - 证明密钥");
        console.log("   verification_key.json - 验证密钥");
        
        console.log("\n下一步:");
        console.log("   运行 'npm run prove' 生成证明");
        console.log("   运行 'npm run verify' 验证证明");
        
    } catch (error) {
        console.error("设置过程中发生错误:", error.message);
        console.error("\n调试提示:");
        console.error("   1. 确保已安装 circom 编译器");
        console.error("   2. 确保已安装 snarkjs 工具");
        console.error("   3. 检查电路语法是否正确");
        process.exit(1);
    }
}

// Run setup
if (require.main === module) {
    setup();
}

module.exports = { setup }; 