# 1. 先创建 README.md 文件
echo "# 软件开发学习仓库" >> README.md

# 2. 初始化 Git 仓库
git init

# 3. 把 README.md 加入暂存区
git add README.md

# 4. 提交到本地仓库
git commit -m "first commit: add README.md"

# 5. 切换到 main 分支
git branch -M main

# 6. 关联你的 GitHub 仓库（复制你页面里的地址）
git remote add origin https://github.com/dave66688/software-engeneering.git

# 7. 推送到 GitHub
git push -u origin main
