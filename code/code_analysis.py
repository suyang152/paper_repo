import os
import re
import tarfile
import gzip
import shutil
import subprocess
from openpyxl import Workbook
import json


# 用于分析 JavaScript 文件的函数
def analyze_js(file_path):
    try:
        lines_of_code = 0
        complexity = 1  # 初始复杂度为 1（最小值）

        # 使用 ESLint 执行复杂度分析
        eslint_result = run_eslint(file_path)
        if eslint_result:
            complexity = eslint_result.get("complexity", 1)

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                lines_of_code += 1
                line = line.strip()

                # 基于关键词简单估算圈复杂度（如 if, for, while 等）
                if re.match(r"(if|for|while|case|catch|switch|else if|function)\b", line):
                    complexity += 1

        return lines_of_code, complexity

    except Exception as e:
        print(f"读取 JavaScript 文件时出错: {e}")
        return 0, 0


# 调用 ESLint 来获取圈复杂度
def run_eslint(file_path):
    try:
        print(f"Running ESLint on {file_path}")
        result = subprocess.run(
            ['npx', 'eslint', '--format', 'json', file_path],
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.DEVNULL,  # 将错误输出丢弃
            text=True,  # 返回文本类型输出
            check=True  # 如果 ESLint 检查失败，则引发异常
        )

        # 解析 ESLint 输出（忽略错误输出）
        eslint_output = json.loads(result.stdout)
        for file_result in eslint_output:
            if file_result['filePath'] == file_path:
                return file_result['messages'][0]

    except Exception as e:
        # 发生错误时不输出任何信息
        pass
    return None


# 用于提取 .gz 文件并返回解压后的文件路径列表
def extract_gz(file_path):
    try:
        # 获取 .gz 文件所在的目录
        dir_path = os.path.dirname(file_path)

        if file_path.endswith('.gz'):
            tar_file = file_path.rstrip('.gz')  # 移除 .gz 后缀以创建 .taz 文件
            tar_file_path = os.path.join(dir_path, os.path.basename(tar_file))

            # 解压 .gz 文件为 .taz 文件
            with gzip.open(file_path, 'rb') as f_in:
                with open(tar_file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 解压 .taz 文件
            return extract_taz(tar_file_path, dir_path)
        else:
            print(f"文件 {file_path} 不是有效的 .gz 格式。")
            return []

    except Exception as e:
        print(f"解压 {file_path} 时出错: {e}")
        return []


# 用于提取 .taz 文件并返回解压后的文件路径列表
def extract_taz(file_path, extract_to):
    try:
        # 解压 tar 包到原文件目录
        with tarfile.open(file_path, "r:") as tar:
            tar.extractall(path=extract_to)
            print(f"成功解压 {file_path} 到 {extract_to}")

        # 返回解压后所有 .js 文件的路径
        return [os.path.join(extract_to, f) for f in os.listdir(extract_to) if f.endswith('.js')]

    except Exception as e:
        print(f"解压 {file_path} 时出错: {e}")
        return []


# 判断是否为 trivial package
def is_trivial_package(lines_of_code, complexity):
    return 1 if lines_of_code < 35 and complexity < 10 else 0


# 用于将数据写入 Excel（文件汇总）
def write_file_summary_to_excel(data_list, output_file=r"excel\file_summary.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.append(["Package Name", "Lines of Code", "Cyclomatic Complexity", "Trivial Package"])

    for entry in data_list:
        package_name = entry.get('file_name', '')
        lines_of_code = entry.get('lines_of_code', 0)
        complexity = entry.get('complexity', 0)
        trivial_package = is_trivial_package(lines_of_code, complexity)  # 判断是否为 trivial package

        ws.append([package_name, lines_of_code, complexity, trivial_package])

    wb.save(output_file)
    print(f"\n文件汇总已完成，结果保存在 {output_file} 中。\n")


# 用于扫描目录并分析 .gz, .taz 和 .js 文件
def scan_and_analyze_js(directory_to_monitor):
    data_list = []
    analyzed_files = set()  # 用于存储已分析的文件

    for root, _, files in os.walk(directory_to_monitor):
        for file in files:
            file_path = os.path.join(root, file)

            # 只分析未处理过的文件
            if file_path not in analyzed_files:
                analyzed_files.add(file_path)

                # 处理 .js 文件
                if file_path.endswith('.js'):
                    lines_of_code, complexity = analyze_js(file_path)
                    print(f"分析 {file}: {lines_of_code} 行，复杂度 {complexity}")

                    rel_file_path = os.path.relpath(file_path, directory_to_monitor)
                    data_list.append({
                        'file_name': rel_file_path,
                        'lines_of_code': lines_of_code,
                        'complexity': complexity
                    })

                # 处理 .gz 文件
                elif file_path.endswith('.gz'):
                    # 解压 .gz 文件并分析解压后的 .js 文件
                    extracted_files = extract_gz(file_path)
                    for extracted_file in extracted_files:
                        if extracted_file not in analyzed_files:
                            analyzed_files.add(extracted_file)
                            lines_of_code, complexity = analyze_js(extracted_file)
                            print(f"分析解压后的 {extracted_file}: {lines_of_code} 行，复杂度 {complexity}")

                            rel_file_path = os.path.relpath(extracted_file, directory_to_monitor)
                            data_list.append({
                                'file_name': rel_file_path,
                                'lines_of_code': lines_of_code,
                                'complexity': complexity
                            })

                # 处理 .taz 文件
                elif file_path.endswith('.taz'):
                    # 解压 .taz 文件并分析解压后的 .js 文件
                    extracted_files = extract_taz(file_path, root)
                    for extracted_file in extracted_files:
                        if extracted_file not in analyzed_files:
                            analyzed_files.add(extracted_file)
                            lines_of_code, complexity = analyze_js(extracted_file)
                            print(f"分析解压后的 {extracted_file}: {lines_of_code} 行，复杂度 {complexity}")

                            rel_file_path = os.path.relpath(extracted_file, directory_to_monitor)
                            data_list.append({
                                'file_name': rel_file_path,
                                'lines_of_code': lines_of_code,
                                'complexity': complexity
                            })

    return data_list


# 主程序
if __name__ == "__main__":
    directory_to_monitor = r"C:\Users\37958\Desktop\ResearchonOpenSourceSoftwareSupplyChain\paper\package"
    file_summary_output_file = r"excel\file_summary.xlsx"

    # 扫描并分析文件
    data_list = scan_and_analyze_js(directory_to_monitor)

    # 将文件汇总信息保存到文件
    write_file_summary_to_excel(data_list, file_summary_output_file)

