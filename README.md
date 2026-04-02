🚀 CodeDesign 图标库查重助手 (Icon Dedupe Tool)
📖 项目背景
在 B 端复杂系统中，图标 Unicode 冲突会导致线上图标显示异常。本项目利用 Playwright 自动化技术，一键遍历 CodeDesign 资源库中的所有文件夹，精准找出重复的 Unicode 定义，告别人肉排查。

✨ 核心功能
全自动巡检：自动空降图标库，无需手动翻页。

精准匹配：支持文件夹名称精确匹配

智能等待：自动处理页面懒加载与 DOM 刷新，确保数据 100% 准确。

审计报告：运行结束后自动导出 duplicate_report.txt 审计清单。

🛠 环境准备
本项目推荐在 Antigravity 环境下运行：

安装依赖：
在终端运行以下命令安装自动化引擎：

Bash
pip install -r requirements.txt
playwright install chromium
配置地址：
打开 skills/codesign_dedupe/scripts/dedupe.py，确认 TARGET_URL 为你们团队的图标库地址。

🖱 使用指南
启动脚本：
在终端执行：

Bash
python skills/codesign_dedupe/scripts/dedupe.py
登录认证：

浏览器弹出后，若提示未登录，请完成扫码。

脚本会自动保存登录状态（存储在本地 user_data 文件夹），下次运行无需再次扫码。

全自动扫描：

脚本会自动跳转至图标页并开始遍历。

请勿在扫描期间关闭或操作弹出的浏览器窗口。

查看结果：
扫描完成后，在项目根目录找到 duplicate_report.txt，里面详细列出了所有重复的 Unicode 及其所在的图标文件夹。

⚠️ 注意事项
隐私安全：请勿将本地生成的 user_data/ 文件夹上传至 GitHub，以免泄露个人登录凭证。

网络环境：若公司内网有代理，请确保 Clash 或其他代理工具开启了 TUN 模式。

👨‍💻 Maintainer: @mawangxizi@gmail.com (UX Designer)

📅 Last Updated: 2026-04-02
