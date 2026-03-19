"""
打包脚本 - 将 XianyuAutoAgent 打包成可分发的 zip 包
使用方法: python build_release.py
"""
import os
import sys
import shutil
import zipfile
from datetime import datetime

# 修复 Windows 终端编码
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def build_release():
    """构建发布包"""
    version = datetime.now().strftime("%Y%m%d")
    release_name = f"XianyuAutoAgent-v{version}"
    dist_dir = os.path.join("dist", release_name)

    # 清理旧的构建
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    os.makedirs(dist_dir)

    # 需要打包的文件
    files_to_copy = [
        "main.py",
        "XianyuAgent.py",
        "XianyuApis.py",
        "context_manager.py",
        "qclaw_llm.py",
        "notifier.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "LICENSE",
    ]

    # 复制文件
    for f in files_to_copy:
        if os.path.exists(f):
            shutil.copy2(f, dist_dir)
            print(f"  ✅ {f}")
        else:
            print(f"  ⚠️ 跳过（不存在）: {f}")

    # 复制目录
    dirs_to_copy = ["prompts", "utils"]
    for d in dirs_to_copy:
        if os.path.exists(d):
            shutil.copytree(d, os.path.join(dist_dir, d))
            print(f"  ✅ {d}/")

    # 创建 data 目录（空的，程序运行时会自动创建数据库）
    os.makedirs(os.path.join(dist_dir, "data"), exist_ok=True)

    # 创建启动脚本 (Windows)
    with open(os.path.join(dist_dir, "start.bat"), "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("chcp 65001 >nul\n")
        f.write('echo ========================================\n')
        f.write('echo   XianyuAutoAgent - 闲鱼自动回复机器人\n')
        f.write('echo ========================================\n')
        f.write("echo.\n")
        f.write('if not exist ".env" (\n')
        f.write('    echo [提示] 首次运行，正在从模板创建 .env 配置文件...\n')
        f.write('    copy .env.example .env >nul\n')
        f.write('    echo [提示] 请先编辑 .env 文件，填写你的配置信息！\n')
        f.write("    notepad .env\n")
        f.write("    pause\n")
        f.write("    exit\n")
        f.write(")\n")
        f.write("echo.\n")
        f.write('echo [启动] 正在启动机器人...\n')
        f.write("echo.\n")
        f.write("pip install -r requirements.txt -q 2>nul\n")
        f.write("python main.py\n")
        f.write("pause\n")
    print("  ✅ start.bat")

    # 创建启动脚本 (Linux/Mac)
    with open(os.path.join(dist_dir, "start.sh"), "w", encoding="utf-8", newline="\n") as f:
        f.write("#!/bin/bash\n")
        f.write('echo "========================================"\n')
        f.write('echo "  XianyuAutoAgent - 闲鱼自动回复机器人"\n')
        f.write('echo "========================================"\n')
        f.write('if [ ! -f ".env" ]; then\n')
        f.write('    echo "[提示] 首次运行，正在从模板创建 .env 配置文件..."\n')
        f.write("    cp .env.example .env\n")
        f.write('    echo "[提示] 请先编辑 .env 文件，填写你的配置信息！"\n')
        f.write('    echo "  nano .env  或  vim .env"\n')
        f.write("    exit 1\n")
        f.write("fi\n")
        f.write("pip install -r requirements.txt -q 2>/dev/null\n")
        f.write("python main.py\n")
    print("  ✅ start.sh")

    # 打包成 zip
    zip_path = os.path.join("dist", f"{release_name}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, "dist")
                zf.write(file_path, arc_name)

    print(f"\n🎉 打包完成！")
    print(f"   📦 {zip_path}")
    print(f"   📂 {dist_dir}")
    print(f"\n上传到 GitHub Releases 时，上传 {zip_path} 即可。")


if __name__ == "__main__":
    build_release()
