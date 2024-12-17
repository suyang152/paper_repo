const escomplex = require('escomplex');
const fs = require('fs');
const path = require('path');

const filePath = process.argv[2];

try {
    // 检查文件是否为空
    const stats = fs.statSync(filePath);
    if (stats.size === 0) {
        console.error(`Skipping empty file: ${filePath}`);
        process.exit(0);
    }

    // 检查文件是否为特殊文件（例如 .min.js 压缩文件）
    if (path.extname(filePath) === '.js' && filePath.includes('.min')) {
        console.error(`Skipping minified file: ${filePath}`);
        process.exit(0);
    }

    // 读取文件内容
    const content = fs.readFileSync(filePath, 'utf8');

    // 分析文件复杂度
    const complexity = escomplex.analyse(content);
    console.log(JSON.stringify(complexity, null, 2));
} catch (error) {
    // 捕获解析错误并记录日志
    console.error(`Error analyzing file: ${filePath}. Skipping...`);
    console.error(error.message);
    process.exit(1);
}
