import os
import json
import subprocess
import re
import pandas as pd
from datetime import datetime


def extract_dependencies_from_js(js_file):
    """解析 .js 文件中的 require 或 import 语句，提取出外部依赖"""
    dependencies = set()
    with open(js_file, 'r', encoding='utf-8') as file:
        content = file.read()

        # 查找所有 require 语句
        require_pattern = r"require\(['\"](.*?)['\"]\)"
        import_pattern = r"import.*['\"](.*?)['\"]"

        # 查找并提取依赖
        requires = re.findall(require_pattern, content)
        imports = re.findall(import_pattern, content)

        dependencies.update(requires)
        dependencies.update(imports)

    return dependencies


def check_vulnerabilities(dependencies):
    """使用 npm audit 来检查依赖库的漏洞"""
    # 创建一个临时 package.json
    package_json = {
        "name": "temp-project",
        "version": "1.0.0",
        "dependencies": {}
    }

    # 合并所有依赖
    for dep in dependencies:
        package_json['dependencies'][dep] = "*"

    # 写入临时 package.json 文件
    with open('temp-package.json', 'w', encoding='utf-8') as f:
        json.dump(package_json, f, indent=4)

    # 确保 package-lock.json 存在，如果没有，运行 npm install
    if not os.path.exists('package-lock.json'):
        print("No package-lock.json found, running npm install...")
        result = subprocess.run(
            [r"C:\Program Files\nodejs\npm.cmd", "install"],
            capture_output=True, text=True,
            cwd=os.getcwd()  # 设置为当前目录
        )
        if result.returncode != 0:
            print(f"npm install failed: {result.stderr}")
            return

    # 使用 npm audit 检查漏洞
    print("Running npm audit on all dependencies...")

    result = subprocess.run(
        [r"C:\Program Files\nodejs\npm.cmd", "audit", "--json"],
        capture_output=True, text=True,
        cwd=os.getcwd()  # 设置为当前目录
    )

    # 输出调试信息
    print("npm audit stdout:", result.stdout)
    print("npm audit stderr:", result.stderr)

    # 删除临时 package.json 文件
    os.remove('temp-package.json')

    # 解析 npm audit 输出
    if result.returncode != 0:
        print(f"npm audit failed: {result.stderr}")
        return

    audit_result = json.loads(result.stdout)

    # 如果有漏洞，显示表格并保存
    if audit_result.get("advisories"):
        print("Found vulnerabilities!")

        # 解析漏洞信息并创建 DataFrame
        advisories = audit_result["advisories"]
        rows = []

        for advisory_id, advisory in advisories.items():
            module_name = advisory["module_name"]
            severity = advisory["severity"]
            version = advisory["findings"][0]["version"]
            url = advisory.get("url", "N/A")
            description = advisory.get("title", "No description")
            affected_versions = advisory.get("vulnerable_versions", "N/A")
            fixed_versions = advisory.get("patched_versions", "N/A")
            rows.append([module_name, severity, version, affected_versions, fixed_versions, description, url])

        # 创建 DataFrame
        df = pd.DataFrame(rows, columns=["依赖名称", "严重程度", "版本", "受影响版本", "修复版本", "描述", "漏洞详情链接"])

        # 输出表格
        print(df)

        # 确保保存目录存在
        output_dir = r'C:\Users\37958\Desktop\ResearchonOpenSourceSoftwareSupplyChain\paper\code\excel'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 保存为 CSV 或 Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = os.path.join(output_dir, f"vulnerability_report_{timestamp}.csv")
        excel_file = os.path.join(output_dir, f"vulnerability_report_{timestamp}.xlsx")

        # 保存文件
        df.to_csv(csv_file, index=False)
        df.to_excel(excel_file, index=False)

        print(f"报告已保存为 CSV 和 Excel 文件: {csv_file} / {excel_file}")

    else:
        print("所有依赖安全，没有已知漏洞.")


def main():
    # 设置你的目录路径
    js_dir = r'C:\Users\37958\Desktop\ResearchonOpenSourceSoftwareSupplyChain\paper\package'

    # 获取目录及子目录中的所有 .js 文件和 package.json 文件
    js_files = []
    for root, dirs, files in os.walk(js_dir):
        # 检查是否有 package.json 文件，如果有，跳过 js 文件的依赖提取
        if 'package.json' in files:
            print(f"Found package.json in {root}, using it for dependency analysis.")
            with open(os.path.join(root, 'package.json'), 'r', encoding='utf-8') as f:
                package_json = json.load(f)
                js_files.append({'type': 'json', 'file': package_json, 'path': root})
        else:
            for file in files:
                if file.endswith('.js'):
                    js_files.append({'type': 'js', 'file': os.path.join(root, file), 'path': root})

    print(f"Found {len(js_files)} files to analyze.")  # 输出找到的文件数量

    # 如果没有找到 .js 文件，退出脚本
    if not js_files:
        print("No .js files or package.json files found in the specified directory.")
        return

    # 遍历每个文件
    all_dependencies = set()
    for item in js_files:
        if item['type'] == 'js':
            print(f"正在解析文件：{item['file']}")
            dependencies = extract_dependencies_from_js(item['file'])
            print("解析到的依赖：", dependencies)
            all_dependencies.update(dependencies)
        elif item['type'] == 'json':
            # 从 package.json 中提取依赖
            dependencies = item['file'].get('dependencies', {}).keys()
            print(f"从 package.json 提取依赖：{dependencies}")
            all_dependencies.update(dependencies)

    # 检查所有依赖的安全性
    check_vulnerabilities(all_dependencies)

if __name__ == "__main__":
    main()
