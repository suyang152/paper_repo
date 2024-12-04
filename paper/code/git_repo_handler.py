import git
import os
import time
import shutil


def clone_repo_to_gitbase(repo_url):
    """
    克隆Git仓库到相对路径下的指定目录（paper/gitbase）
    repo_url: Git仓库URL
    """
    # 获取当前脚本文件的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 目标路径（paper/gitbase）
    target_dir = os.path.join(current_dir, "gitbase")

    # 检查目标目录是否存在，存在则提示
    if os.path.exists(target_dir):
        print(f"目录 '{target_dir}' 已存在，跳过克隆操作。")
    else:
        # 克隆仓库到目标目录
        print(f"正在将仓库克隆到 '{target_dir}'...")
        git.Repo.clone_from(repo_url, target_dir)
        print("克隆完成！")
    return target_dir


def get_all_files(directory):
    """
    获取目录及子目录中所有文件路径
    directory: 要扫描的目录路径
    返回：包含所有文件路径的集合
    """
    file_paths = set()
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.add(os.path.join(root, file))
    return file_paths


def monitor_repo(repo_dir, target_dir, interval=10):
    """
    监控Git仓库目录中的变化，并将新增文件复制到目标目录
    repo_dir: Git仓库的本地路径
    target_dir: 要同步到的目标目录
    interval: 检查间隔时间（秒）
    """
    print("开始监控 Git 仓库中的文件变化...")
    previous_files = get_all_files(repo_dir)

    while True:
        # 拉取最新更改
        print("正在拉取最新更新...")
        repo = git.Repo(repo_dir)
        repo.remote().pull()

        # 获取当前文件列表
        current_files = get_all_files(repo_dir)
        new_files = current_files - previous_files

        # 如果有新文件，复制到目标目录
        if new_files:
            print("发现新文件，开始复制...")
            for file in new_files:
                # 计算相对路径
                relative_path = os.path.relpath(file, repo_dir)
                destination = os.path.join(target_dir, relative_path)

                # 创建目标目录（如果不存在）
                os.makedirs(os.path.dirname(destination), exist_ok=True)

                # 复制文件
                shutil.copy2(file, destination)
                print(f"已复制：{file} -> {destination}")
            print("所有新文件复制完成。")
        else:
            print("没有发现新文件。")

        # 更新文件列表
        previous_files = current_files

        # 等待一段时间
        time.sleep(interval)


if __name__ == "__main__":
    # 示例：替换为你的Git仓库URL
    repo_url = "https://github.com/your_repo.git"

    # 克隆仓库到指定目录（paper/gitbase）
    repo_dir = clone_repo_to_gitbase(repo_url)

    # 设置目标目录为Git仓库中的某个具体文件夹（例如my_folder）
    target_dir = os.path.join(repo_dir, "my_folder")  # 目标文件夹在Git仓库中的路径

    # 监控Git仓库文件的变化
    monitor_repo(repo_dir, target_dir, interval=30)  # 每30秒检查一次
