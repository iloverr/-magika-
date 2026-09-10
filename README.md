# 🐷 爱吃文件的猪 — 文件类型识别器

一个基于 Google Magika AI 模型的文件类型识别 Web 应用。把任意文件拖进去，小猪会"吃一下"它的字节内容（不看扩展名），告诉你这是什么格式、有什么用。

界面走温馨粉色小猪风格，左侧是会睡觉/思考/摇摆的小猪动画区，右侧展示识别结果。识别不了的文件小猪会摇头（不倒翁动画）。

---

## ✨ 功能特性

- **基于字节内容识别**：不看文件扩展名，直接分析文件字节，比传统 MIME 猜测更准
- **200+ 种文件类型**：覆盖 Magika 模型全部 214 种 label——图片、代码、文档、压缩包、可执行程序、音视频、字体、数据、证书等
- **中文翻译层**：Magika 默认输出英文，后端内置翻译表把格式名和描述转成通俗中文
- **文件夹拦截**：拖入文件夹时前端用 `webkitGetAsEntry` 精准识别并提示"小猪不吃文件夹"
- **空文件检测**：0 字节文件单独处理，提示"文件内容为空"
- **大文件支持**：只读取文件头交给模型，内存占用低，测试过 751MB 的 zip 包正常识别
- **置信度与扩展名**：结果附带 Magika 置信度评分与常见扩展名，前端一并展示
- **动画交互**：
  - 待机：小猪睡觉（帧动画）
  - 识别中：思考图标旋转
  - 不可识别：deco7 图片不倒翁摇摆（±15°）
- **操作日志**：前后端联动记录每次拖入/识别/错误，写入 `logs/app.log`

---

## 🛠 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 前端框架 | React | 19.2 |
| 构建工具 | Vite | 8.2 |
| 样式 | Tailwind CSS | 3.4 |
| 拖拽 | react-dropzone | 20.1 |
| HTTP | axios | 1.19 |
| 后端框架 | Flask | 3.1.0 |
| 跨域 | flask-cors | 5.0.1 |
| 文件识别 | Magika | 1.0.3 |
| Python | CPython | 3.13 |

---

## 📁 项目结构

```
文件解释器/
├── server.py                 # 后端：Flask + Magika 识别 + 翻译层 + 日志
├── start.bat                 # Windows 一键启动前后端（纯 ASCII，自愈式）
├── 打包.bat                  # 一键打包成干净 zip（自动排除 .venv/node_modules 等）
├── requirements.txt          # Python 依赖
├── .gitignore                # 忽略 logs/、.venv/、node_modules/、__pycache__/
├── index.html                # 前端入口 HTML
├── vite.config.js            # Vite 配置
├── tailwind.config.js        # Tailwind 配置
├── postcss.config.js         # PostCSS 配置
├── package.json              # Node 依赖
├── src/
│   ├── main.jsx              # React 挂载入口
│   ├── App.jsx               # 主组件：拖放、动画、状态、日志上报
│   ├── index.css             # Tailwind 指令 + 自定义动画（不倒翁）
│   └── services/
│       └── api.js            # axios 封装，调后端 /api/identify
├── public/                   # 静态资源
│   ├── backgrounds/背景.jpg   # 全屏背景图
│   ├── deco1-6.png            # 装饰图（卡片四角）
│   ├── deco7.png             # 不可识别时显示的图
│   ├── 睡1.png / 睡3.png      # 待机帧动画（跳过睡2）
│   ├── 思考.png              # 识别中旋转图
│   └── favicon.svg
└── logs/
    └── app.log               # 运行日志（自动生成，已 gitignore）
```

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | 18+ | 仅前端需要 |
| Python | **3.13** | 后端 + Magika（3.14 暂缺 magika 预编译包，建议 3.13） |

> 首次运行需联网下载依赖（`pip` / `npm`）。

### 1. 获取代码

```bash
git clone https://github.com/iloverr/-magika-.git
cd -magika-
```

> 仓库不含 `.venv`、`node_modules`、`dist` 等，clone 下来后按下面步骤本地安装依赖即可。

### 2. 安装后端依赖（Python）

```bash
# 创建虚拟环境（Windows 用 py，Linux/macOS 用 python3）
py -3.13 -m venv .venv

# Windows
.venv\Scripts\python.exe -m pip install -r requirements.txt

# Linux / macOS
.venv/bin/python -m pip install -r requirements.txt
```

> Magika 模型随 `magika` 包一起安装，无需额外联网下载。

### 3. 安装前端依赖（Node）

```bash
npm install
```

### 4. 启动

**后端**（一个终端）：

```bash
# Windows
.venv\Scripts\python.exe server.py

# Linux / macOS
.venv/bin/python server.py
```

**前端**（另开一个终端）：

```bash
npm run dev
```

**打开浏览器**，访问 http://localhost:5173

> 💡 后端默认绑定 `127.0.0.1` 且关闭热重载（`use_reloader=False`，避免 Magika 模型重复加载）。改动 `server.py` 后需手动重启后端；前端 Vite 照常热更新。

---

### Windows 一键启动（可选）

如果你在 Windows 上，可以跳过上面手动步骤，直接**双击 [`start.bat`](start.bat)**，它会全自动：

1. 自动查找本机 Python（按 `3.13 → 3.12 → 3.11 → 3.10 → python → py` 顺序）
2. 若 `.venv` 缺失或损坏，自动重建并 `pip install -r requirements.txt`
3. 若 `node_modules` 缺失，自动 `npm install`
4. 开新窗口跑后端 Flask（http://127.0.0.1:5000）
5. 开新窗口跑前端 Vite（http://localhost:5173）
6. 3 秒后自动打开浏览器

> `start.bat` 是纯 ASCII 编码，中文 Windows 下无乱码。若某次运行报错，删除 `.venv` 和 `node_modules` 后重新双击即可自愈。

---

## 📖 使用说明

1. 在左侧卡片区域**拖入文件**或**点击选择文件**
2. 小猪会切换到"思考中"状态（图标旋转）
3. 识别完成后，右侧卡片展示：
   - **文件格式**：中文格式名（如 "PNG 图片"）
   - **用途描述**：通俗说明（如 "网页常用的位图格式，支持透明背景"）
   - **MIME 类型**：技术标识（如 `image/png`）
   - **常见扩展名**：该格式常见的文件后缀（如 `png`）
   - **置信度**：Magika 的识别置信度百分比

### 特殊场景提示

| 拖入内容 | 左侧动画 | 右侧提示 |
|---------|---------|---------|
| 正常文件 | 睡觉帧动画 | 格式 + 描述 + MIME |
| 文件夹 | deco7 不倒翁摇摆 | 🐷 小猪不吃文件夹，只吃文件 |
| 空文件(0字节) | deco7 不倒翁摇摆 | 🐷 文件内容为空（0 字节） |
| 不可识别内容 | deco7 不倒翁摇摆 | 🐷 小猪还不会吃这个，换成其他文件试试 |

---

## 🔧 后端 API

### `POST /api/identify`

上传文件，返回识别结果。

**请求**：`multipart/form-data`，字段 `file`

**响应**（JSON）：

```json
{
  "format": "PNG 图片",
  "description": "网页常用的位图格式，支持透明背景",
  "mime_type": "image/png",
  "group": "image",
  "score": 0.9512,
  "extensions": ["png"],
  "is_text": false,
  "is_empty": false,
  "unrecognized": false,
  "filename": "test.png"
}
```

| 字段 | 说明 |
|------|------|
| `format` | 中文格式名 |
| `description` | 中文通俗描述 |
| `mime_type` | MIME 类型 |
| `group` | 类型分组（image/code/text 等） |
| `score` | 置信度 0-1 |
| `extensions` | 常见扩展名 |
| `is_text` | 是否文本文件 |
| `is_empty` | 是否空文件（0 字节，true 时前端显示"文件内容为空"） |
| `unrecognized` | 是否不可识别（true 时前端显示提示） |
| `filename` | 原始文件名 |

### `POST /api/log`

接收前端上报的用户操作日志，写入 `logs/app.log`。

---

## 📝 日志系统

每次操作都会记录到 `logs/app.log`，格式：

```
[2026-09-10 11:08:01] [frontend] [drop_file] {"name":"server.py","size":11581,"mime_type":"text/x-python"}
[2026-09-10 11:08:01] [backend]  [identify_request] {"filename":"server.py","size":11581,"format":"Python 脚本","unrecognized":false}
[2026-09-10 11:08:01] [frontend] [identify_result] {"name":"server.py","format":"Python 脚本","unrecognized":false}
```

| 事件类型 | 来源 | 说明 |
|---------|------|------|
| `drop_file` | frontend | 用户拖入文件 |
| `drop_directory` | frontend | 用户拖入文件夹（被拦截） |
| `identify_request` | backend | 后端收到识别请求 |
| `identify_result` | frontend | 前端收到识别结果 |
| `identify_error` | frontend | 识别失败 |

---

## 🎨 自定义动画

动画定义在 `src/index.css`：

```css
/* 不倒翁摇摆：以底部中心为支点，±15° 衰减摆动 */
@keyframes roly-poly {
  0%   { transform: rotate(0deg); }
  20%  { transform: rotate(15deg); }
  40%  { transform: rotate(-15deg); }
  60%  { transform: rotate(10deg); }
  80%  { transform: rotate(-10deg); }
  100% { transform: rotate(0deg); }
}
```

待机帧动画序列在 `src/App.jsx` 中可调整：

```jsx
const sleepFrames = [1, 3];  // 睡1 → 睡3（跳过睡2）
```

---

## ⚠️ 已知局限

这些是 Magika 模型本身的限制，非代码 bug：

- **Electron `.asar` 归档**：头部含 JSON + JS，可能被误判为 JavaScript
- **Chromium `.pak` 资源包**：私有格式，模型结果不稳定
- **超短文件**：特征不足时可能误判（如 `.gitignore` 被识别为 Markdown）
- **极新格式**：Magika 训练数据未覆盖的格式会返回 `unknown`

未命中翻译表的类型会走中文兜底：`该文件被 Magika 识别为 XXX 类型，暂未收录通俗释义`。

---

## 📦 发布与打包

### 打包成本地 zip

如果你想打包发给**没有 git / 不会命令行**的朋友，可以双击 [`打包.bat`](打包.bat)，它会生成一个干净 zip（放在项目上一级目录），自动排除：

```
.venv\  node_modules\  __pycache__\  logs\  dist\  .git\
```

对方解压后只需装好 **Python 3.13** 和 **Node.js 18+**，双击 `start.bat` 即可运行。

> ⚠️ 注意：**不要**直接把整个文件夹压缩发人。`.venv\` 写死了你电脑的绝对路径、`node_modules\` 是平台相关二进制，换机器就失效。

### 生产构建

```bash
npm run build   # 产物输出到 dist/
```

## 📄 License

MIT
