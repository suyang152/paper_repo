import git
import os
import time
import shutil
import hashlib
import logging

# 设置编码为 UTF-8，确保支持中文路径等
os.environ['PYTHONIOENCODING'] = 'utf-8'


def clone_repo_to_gitbase(repo_url):
    """
    克隆Git仓库到相对路径下的指定目录（gitbase）
    repo_url: Git仓库URL
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 当前脚本所在目录
    target_dir = os.path.join(os.path.abspath(os.path.join(current_dir, "..")), "gitbase")  # 直接跳转到父级目录

    print(f"当前脚本路径: {current_dir}")
    print(f"目标路径: {target_dir}")

    if os.path.exists(target_dir):
        print(f"目录 '{target_dir}' 已存在，跳过克隆操作。")
    else:
        try:
            print(f"正在将仓库克隆到 '{target_dir}'...")
            repo = git.Repo.clone_from(repo_url, target_dir)
            # 确保远程仓库的拉取配置正确
            repo.git.config('--add', 'remote.origin.fetch', '+refs/heads/*:refs/heads/*')
            print("克隆完成！")
        except Exception as e:
            print(f"克隆仓库失败：{e}")
            return None
    return target_dir


def get_all_files(directory, file_extensions=None):
    """
    获取目录及子目录中所有文件路径，排除 .git 目录中的文件
    directory: 要扫描的目录路径
    file_extensions: 过滤的文件扩展名（例如：['.py', '.java']）
    返回：包含所有文件路径的集合
    """
    file_paths = set()
    for root, _, files in os.walk(directory):
        if '.git' in root:
            continue
        for file in files:
            if file_extensions:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_paths.add(os.path.join(root, file))
            else:
                file_paths.add(os.path.join(root, file))
    return file_paths


def file_hash(filepath):
    """
    计算文件的MD5值，确保文件是否有变更
    filepath: 文件路径
    返回：文件的MD5哈希值
    """
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"计算文件哈希值失败：{e}")
        return None


def monitor_repo(repo_dir, target_dir, interval=10, file_extensions=None):
    """
    监控Git仓库目录中的变化，并将新增文件复制到目标目录
    repo_dir: Git仓库的本地路径
    target_dir: 要同步到的目标目录
    interval: 检查间隔时间（秒）
    file_extensions: 过滤的文件扩展名（例如：['.py', '.java']）
    """
    logging.basicConfig(filename='repo_monitor.log', level=logging.INFO)
    logging.info("开始监控 Git 仓库中的文件变化...")

    if not os.path.exists(repo_dir):
        print(f"Git 仓库目录 '{repo_dir}' 不存在！")
        logging.error(f"Git 仓库目录 '{repo_dir}' 不存在！")
        return

    try:
        repo = git.Repo(repo_dir)
        previous_files = get_all_files(repo_dir, file_extensions)
        previous_hashes = {file: file_hash(file) for file in previous_files}

        while True:
            try:
                # 拉取最新更新
                print("正在拉取最新更新...")
                repo.remote().pull()

                current_files = get_all_files(repo_dir, file_extensions)
                current_hashes = {file: file_hash(file) for file in current_files}

                new_files = current_files - previous_files
                modified_files = [file for file in current_files if
                                  current_hashes.get(file) != previous_hashes.get(file)]

                if new_files or modified_files:
                    print("发现新文件或修改，开始复制...")
                    for file in list(new_files) + modified_files:
                        relative_path = os.path.relpath(file, repo_dir)
                        destination = os.path.join(target_dir, relative_path)

                        if os.path.exists(destination):
                            if os.path.samefile(file, destination):
                                print(f"文件 {file} 和目标文件 {destination} 是相同的，跳过复制。")
                                continue

                        os.makedirs(os.path.dirname(destination), exist_ok=True)
                        shutil.copy2(file, destination)
                        print(f"已复制：{file} -> {destination}")
                    print("所有新文件复制完成。")
                else:
                    print("没有发现新文件或修改。")

                previous_files = current_files
                previous_hashes = current_hashes

            except Exception as e:
                print(f"监控过程中发生错误：{e}")
                logging.error(f"监控过程中发生错误：{e}")

            time.sleep(interval)
    except git.exc.InvalidGitRepositoryError as e:
        print(f"无效的 Git 仓库：{repo_dir}")
        logging.error(f"无效的 Git 仓库：{repo_dir}")
    except Exception as e:
        print(f"无法访问 Git 仓库：{e}")
        logging.error(f"无法访问 Git 仓库：{e}")


if __name__ == "__main__":
    # 示例：替换为你的Git仓库URL
    repo_url = "git@github.com:suyang152/paper_repo.git"

    # 克隆仓库到指定目录（gitbase）
    repo_dir = clone_repo_to_gitbase(repo_url)

    if repo_dir:
        # 将目标目录设置为 "paper/gitbase" 文件夹（与当前代码文件夹同级）
        target_dir = r"C:\Users\37958\Desktop\ResearchonOpenSourceSoftwareSupplyChain\paper\gitbase"
        # 指定需要监控的文件类型（例如 .py, .java, .js）
        file_extensions = ['.json', '.py', '.java', 'js']

        monitor_repo(repo_dir, target_dir, interval=30, file_extensions=file_extensions)
