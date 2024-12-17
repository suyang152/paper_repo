import os
import json
from openpyxl import Workbook


def extract_dependencies(project_path):
    """
    从项目目录中提取 package.json 文件的 devDependencies 或 dependencies 属性值。
    :param project_path: 项目目录的路径
    :return: (项目名, 合并后的依赖字典 或 错误信息)
    """
    project_name = os.path.basename(project_path)
    package_json_path = os.path.join(project_path, 'package.json')

    if not os.path.exists(package_json_path):
        print(f"[WARN] {project_path}: package.json 文件不存在")
        return project_name, None, "package.json 文件不存在"

    try:
        with open(package_json_path, 'r', encoding='utf-8') as file:
            package_data = json.load(file)

            # 打印读取到的 package.json 内容
            print(f"[DEBUG] {project_name} - package.json 内容: {package_data}")

            # 提取 dependencies 和 devDependencies
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})

            # 合并依赖项：如果两个都有，合并成一个字典
            merged_dependencies = dependencies.copy()
            merged_dependencies.update(dev_dependencies)

            if merged_dependencies:
                print(f"[INFO] {project_name} - 找到的合并后的依赖项：")
                print(f"  生产依赖：{dependencies}")
                print(f"  开发依赖：{dev_dependencies}")
            else:
                print(f"[INFO] {project_name} - 未找到依赖项")

            return project_name, merged_dependencies, None
    except Exception as e:
        print(f"[ERROR] {project_name}: 读取 package.json 时出错 - {e}")
        return project_name, None, f"读取 package.json 时出错: {e}"


def scan_projects(directory):
    """
    扫描目录中的所有项目，提取 devDependencies 或 dependencies。
    :param directory: 要扫描的目录
    :return: 包含项目名、合并后的 dependencies 和备注信息的列表
    """
    results = []

    if not os.path.exists(directory):
        print(f"[ERROR] 指定目录不存在: {directory}")
        return results

    print(f"[INFO] 开始扫描目录: {directory}")

    for item in os.listdir(directory):
        project_path = os.path.join(directory, item)
        if os.path.isdir(project_path):
            print(f"[INFO] 正在扫描项目: {project_path}")
            project_name, dependencies, error = extract_dependencies(project_path)
            results.append({
                'project_name': project_name,
                'dependencies': dependencies,
                'remark': error if error else "正常"
            })

    return results


def write_to_excel(results, output_file):
    """
    将结果写入 Excel 文件，包括依赖项名称和版本号。
    :param results: 包含项目名、合并后的 dependencies 和备注信息的列表
    :param output_file: 输出的 Excel 文件路径
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Dependencies"

    # 写入表头
    ws.append(["项目名称", "依赖项 (名称@版本)", "备注"])

    # 写入每个项目的信息
    for result in results:
        project_name = result['project_name']

        # 处理合并后的依赖项
        dependencies = (
            ', '.join([f"{name}@{version}" for name, version in result['dependencies'].items()])
            if result['dependencies'] else "N/A"
        )

        remark = result['remark']
        ws.append([project_name, dependencies, remark])

    # 保存文件
    wb.save(output_file)
    print(f"[INFO] 结果已保存到 {output_file}")


if __name__ == "__main__":
    # 要扫描的目录路径
    directory_to_scan = r"C:\\Users\\37958\\Desktop\\ResearchonOpenSourceSoftwareSupplyChain\\paper\\gitbase\\temp"
    output_excel_file = r"excel\project_dependencies_with_versions.xlsx"

    # 扫描目录并提取信息
    project_results = scan_projects(directory_to_scan)

    # 写入 Excel 文件
    write_to_excel(project_results, output_excel_file)
