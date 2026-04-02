# CodeDesign Icon Unicode Dedupe Tool

这是一个基于 Playwright 和 Python 编写的自动化检查工具。它能够自动登录 [腾讯 Codesign](https://codesign.qq.com/) 资源库，逐个进入并扫描所有的图标文件，提取图标名称与对应的 Unicode 编码，最后在本地生成一份跨文件夹的「重复 Unicode 查重报告」。

## ✨ 核心特性

- **完全自动化**：启动后一键直达图标库，自动规避动态懒加载与单页应用（SPA）特性的干扰。
- **免密记忆**：第一轮运行扫码登录后，缓存数据会自动保存在本地，之后所有运行均无需再次人工介入。
- **精准狙击**：精确追踪页面 URL 变动与内容局部渲染，从根本上防止图标库的 Unicode 数据误读。

---

## 🛠 开发环境安装与配置

本项目依赖于 Python 3，并使用 Playwright 驱动浏览器。

### 1. 检出与创建虚拟环境（推荐）
在项目目录下打开终端，执行以下命令隔离依赖：
```bash
python3 -m venv venv
source venv/bin/activate  # (Windows 环境请使用: venv\Scripts\activate)
```

### 2. 安装 Python 依赖库
一键安装必需的第三方依赖包：
```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器内核 (⚡核心步骤)
仅仅安装 Python 库不够，必须让系统下载 Chromium 对应的浏览器驱动引擎：
```bash
playwright install chromium
```

---

## 🚀 启动与使用说明

### 1. 配置项目专属入口
在使用脚本之前，你需要使用代码编辑器打开自动抓取脚本：
```
skills/codesign_dedupe/scripts/dedupe.py
```
在代码的最上端（约 23 行处），找到 `TARGET_URL` 变量，将它替换为你们团队真实的设计库 Icon 页面的绝对链接。例如：
`TARGET_URL = "https://codesign.qq.com/app/icon/YOUR_PROJECT_ID/detail"`

### 2. 执行自动化查重
在保证激活虚拟环境的前提下，执行以下指令：
```bash
python skills/codesign_dedupe/scripts/dedupe.py
```

### 3. 运行指导

**关于首次运行 (First Run)**:
如果这是一个刚拉下来的本地环境，浏览器弹出后会发现你是未登录的状态。它可能会提醒你：
`Icon cards not detected. You might need to log in.`
此时，你只需在自动弹出的浏览器视窗中直接扫码登录 Codesign 即可。当你扫码登录成功，卡片成功渲染的第一秒钟，脚本就会被瞬间激活并自动接管后续的所有页面跳转和 Unicode 扫描校验，你**不需要**在终端里按任何回车！

**关于后续运行 (Subsequent Runs)**:
再次敲击执行指令时，你可以完全放开鼠标和键盘，脚本会自动穿越并高速生成重复的 Unicode 资产报表。

---

## 📄 报告生成

当所有的图标被遍历和比对完毕后，项目根目录会自动生成或刷新一份纯文本的 Unicode 冲突分析结果：  
👉 **`duplicate_report.txt`**

你可以在这里直观地看到所有在整个 CodeDesign 系统里被跨文件夹重复指派的无效或冲突的 Unicode 编码。由于项目加了安全设定，`user_data`（即你的登录 session 数据文件）、截图残留和调试文本已被加入 `.gitignore`，请安心向内部代码仓提交你的修复。
