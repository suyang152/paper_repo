import os
import requests
import pandas as pd
import time


def download_from_github(dep, folder_path):
    """处理 GitHub 链接的下载逻辑"""
    dep_parts = dep.split('@')
    if len(dep_parts) == 2:
        project_and_repo = dep_parts[0]
        version_or_url = dep_parts[1]

        # 如果@后面的部分是GitHub链接
        if 'github.com' in version_or_url:
            download_url = version_or_url  # 使用@后的GitHub链接
            print(f"尝试下载 GitHub 链接: {download_url}")
        else:
            # 否则拼接tarball下载链接
            download_url = f"https://github.com/{project_and_repo}/tarball/{version_or_url}"
            print(f"尝试下载: {download_url}")
    else:
        project_and_repo = dep
        version = 'master'  # 默认下载 master 分支
        download_url = f"https://github.com/{project_and_repo}/tarball/{version}"
        print(f"尝试下载: {download_url}")

    # 发起下载请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/vnd.github.v3+json"  # GitHub API 需要的 Header
    }

    try:
        response = requests.get(download_url, headers=headers, stream=True)

        # 输出错误详细信息
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"返回内容: {response.text}")  # 打印返回的错误信息
            return  # 退出当前下载尝试

        # 正常下载
        # 处理文件名中的非法字符
        file_name = f"{project_and_repo.replace('/', '_')}_{version_or_url.replace('https://', '').replace('/', '_')}.tar.gz"
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"下载成功: {file_path}")
    except Exception as e:
        print(f"下载过程中出错: {e}")


def download_from_cdn(package, version, folder_path):
    """处理普通的 npm 包下载"""
    if version:
        download_url = f"https://cdn.jsdelivr.net/npm/{package}@{version}"
    else:
        download_url = f"https://cdn.jsdelivr.net/npm/{package}"

    print(f"下载链接: {download_url}")

    try:
        response = requests.get(download_url, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
        if response.status_code == 200:
            file_name = f"{package}.min.js"
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"下载成功: {package}")
        else:
            print(f"下载失败: {package}, 状态码: {response.status_code}")
    except Exception as e:
        print(f"下载过程中出错: {e}")


def main():
    file_path = r'C:\Users\37958\Desktop\ResearchonOpenSourceSoftwareSupplyChain\paper\code\project_dependencies_with_versions.xlsx'  # Excel文件路径
    df = pd.read_excel(file_path)

    download_dir = r'C:\Users\37958\Desktop\ResearchonOpenSourceSoftwareSupplyChain\paper\package'

    for index, row in df.iterrows():
        project_name = row['项目名称']
        dependency = row.get('依赖项 (名称@版本)', None)

        if pd.notna(dependency):
            dependencies = dependency.split(',')
            folder_path = os.path.join(download_dir, project_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"创建文件夹: {folder_path}")

            for dep in dependencies:
                dep = dep.strip()

                # 判断是否是 GitHub 链接
                if 'github.com' in dep:
                    download_from_github(dep, folder_path)
                else:
                    # 处理普通的 npm 包
                    if '@' in dep:
                        dep = dep.replace('=', '')  # 去掉多余的等号
                        package, version = dep.split('@')
                        version = version.lstrip('^~')  # 去除 ^ 和 ~ 符号，保留精确版本
                    else:
                        package = dep
                        version = ''  # 如果没有版本号，使用空字符串
                    download_from_cdn(package, version, folder_path)

                time.sleep(2)  # 为避免过于频繁的请求，加入延迟

        else:
            folder_path = os.path.join(download_dir, project_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"创建空文件夹: {folder_path}")


if __name__ == "__main__":
    main()
