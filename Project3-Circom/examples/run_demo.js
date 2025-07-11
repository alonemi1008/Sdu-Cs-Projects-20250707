const { exec } = require("child_process");
const util = require("util");
const fs = require("fs");

const execAsync = util.promisify(exec);

async function runDemo() {
    console.log("Poseidon2 哈希零知识证明演示");
    console.log("=====================================\n");
    
    try {
        // Check if setup is needed
        const needsSetup = !fs.existsSync("verification_key.json") || 
                          !fs.existsSync("poseidon2_0001.zkey");
        
        if (needsSetup) {
            console.log("检测到需要初始化设置...");
            console.log("正在运行: npm run setup\n");
            
            const { stdout: setupOutput, stderr: setupError } = await execAsync("npm run setup");
            console.log(setupOutput);
            if (setupError) console.log("警告:", setupError);
            
            console.log("设置完成!\n");
        } else {
            console.log("环境已就绪，跳过设置步骤\n");
        }
        
        // Generate proof
        console.log("正在生成零知识证明...");
        console.log("正在运行: npm run prove\n");
        
        const { stdout: proveOutput, stderr: proveError } = await execAsync("npm run prove");
        console.log(proveOutput);
        if (proveError) console.log("警告:", proveError);
        
        console.log("证明生成完成!\n");
        
        // Verify proof
        console.log("正在验证证明...");
        console.log("正在运行: npm run verify\n");
        
        const { stdout: verifyOutput, stderr: verifyError } = await execAsync("npm run verify");
        console.log(verifyOutput);
        if (verifyError) console.log("警告:", verifyError);
        
        console.log("\n演示完成!");
        console.log("=====================================");
        console.log("演示总结:");
        console.log("  Poseidon2 电路编译成功");
        console.log("  Groth16 trusted setup 完成"); 
        console.log("  零知识证明生成成功");
        console.log("  证明验证通过");
        
        console.log("\n这意味着:");
        console.log("  • 证明者成功证明了他们知道秘密原象");
        console.log("  • 该原象的 Poseidon2 哈希等于公开值");
        console.log("  • 验证者无法从证明中获知原象内容");
        console.log("  • 整个过程保护了隐私且可验证");
        
        console.log("\n生成的文件:");
        if (fs.existsSync("proof.json")) {
            console.log("  proof.json - 零知识证明");
        }
        if (fs.existsSync("input.json")) {
            console.log("  input.json - 输入数据");
        }
        if (fs.existsSync("verification_key.json")) {
            console.log("  verification_key.json - 验证密钥");
        }
        
        console.log("\n下一步建议:");
        console.log("  1. 修改 scripts/prove.js 中的原象值");
        console.log("  2. 重新运行 'npm run prove' 和 'npm run verify'");
        console.log("  3. 探索不同的输入组合");
        console.log("  4. 集成到您的应用程序中");
        
    } catch (error) {
        console.error("演示过程中发生错误:", error.message);
        
        console.error("\n故障排除建议:");
        console.error("  1. 确保已安装 Node.js 16+");
        console.error("  2. 运行 'npm install' 安装依赖");
        console.error("  3. 确保已安装 circom 编译器");
        console.error("  4. 检查系统内存是否充足");
        
        process.exit(1);
    }
}

// Run demo
if (require.main === module) {
    runDemo();
}

module.exports = { runDemo }; 