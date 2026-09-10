import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from magika import Magika

app = Flask(__name__)
CORS(app)

# 模型在进程启动时加载一次，避免每次请求重复加载
magika = Magika()

# 文件类型中文翻译表：{ label: (格式中文名, 通俗中文描述) }
# 键为 Magika 模型实际输出的 label（共 214 个），未命中时回退到英文 label 大写 + 中文兜底。
FILE_TRANSLATIONS = {
    # ---------- 图片 ----------
    'png': ('PNG 图片', '网页常用的位图格式，支持透明背景'),
    'jpeg': ('JPEG 图片', '最常见的照片格式，体积小但不支持透明'),
    'gif': ('GIF 动图', '支持动画的图片格式，常用于表情包'),
    'bmp': ('BMP 位图', 'Windows 标准位图格式，不压缩体积大'),
    'webp': ('WebP 图片', 'Google 推出的现代图片格式，体积更小'),
    'ico': ('ICO 图标', 'Windows 程序图标格式'),
    'icns': ('ICNS 图标', 'macOS 程序图标格式'),
    'tiff': ('TIFF 图片', '高质量印刷用图片格式'),
    'svg': ('SVG 矢量图', '可缩放矢量图形，放大不失真'),
    'psd': ('PSD 文件', 'Photoshop 分层设计源文件'),
    'ai': ('AI 矢量图', 'Adobe Illustrator 矢量设计文件'),
    'tga': ('TGA 图片', 'Truevision TGA 位图格式，游戏贴图常用'),
    'jp2': ('JPEG 2000 图片', '小波压缩的图像格式，画质高'),
    'dicom': ('DICOM 医学影像', '医疗影像标准格式，CT/MRI 常用'),
    'emf': ('EMF 图片', 'Windows 增强型图元文件，矢量图'),
    'wmf': ('WMF 图片', 'Windows 图元文件，矢量图'),

    # ---------- 代码 ----------
    'python': ('Python 脚本', 'Python 编程语言源代码文件'),
    'pythonbytecode': ('Python 字节码', 'Python 编译后的 .pyc 字节码文件'),
    'javascript': ('JavaScript 脚本', '网页交互最常用的脚本语言'),
    'typescript': ('TypeScript 脚本', 'JavaScript 的增强版，带类型系统'),
    'java': ('Java 源码', 'Java 编程语言源代码文件'),
    'javabytecode': ('Java 类文件', 'Java 编译后的 .class 字节码'),
    'c': ('C 源码', 'C 编程语言源代码文件'),
    'cpp': ('C++ 源码', 'C++ 编程语言源代码文件'),
    'cs': ('C# 源码', 'C# 编程语言源代码文件'),
    'go': ('Go 源码', 'Go 编程语言源代码文件'),
    'rust': ('Rust 源码', 'Rust 编程语言源代码文件'),
    'ruby': ('Ruby 源码', 'Ruby 编程语言源代码文件'),
    'php': ('PHP 脚本', '服务端网页编程语言'),
    'swift': ('Swift 源码', '苹果平台开发语言'),
    'kotlin': ('Kotlin 源码', 'JVM 上的现代语言，安卓开发常用'),
    'scala': ('Scala 源码', '运行在 JVM 上的函数式编程语言'),
    'perl': ('Perl 脚本', '文本处理能力强的脚本语言'),
    'lua': ('Lua 脚本', '轻量级嵌入式脚本语言'),
    'r': ('R 脚本', '统计分析专用编程语言'),
    'haskell': ('Haskell 源码', '纯函数式编程语言'),
    'dart': ('Dart 源码', 'Flutter 跨端开发使用的语言'),
    'html': ('HTML 网页', '网页的结构标记语言'),
    'css': ('CSS 样式', '网页的样式表语言'),
    'scss': ('SCSS 样式', 'CSS 预处理器，支持变量和嵌套'),
    'json': ('JSON 数据', '轻量级数据交换格式，配置文件常用'),
    'jsonl': ('JSONL 数据', '每行一条 JSON 的数据格式'),
    'xml': ('XML 文档', '可扩展标记语言，用于结构化数据'),
    'yaml': ('YAML 配置', '易读的缩进式配置文件格式'),
    'toml': ('TOML 配置', '简洁的配置文件格式'),
    'ini': ('INI 配置', 'Windows 常见的初始化配置文件'),
    'shell': ('Shell 脚本', 'Linux/Unix 命令行脚本'),
    'batch': ('批处理脚本', 'Windows 命令行批处理脚本'),
    'powershell': ('PowerShell 脚本', 'Windows 系统管理脚本'),
    'sql': ('SQL 脚本', '数据库操作语言脚本'),
    'dockerfile': ('Dockerfile', 'Docker 容器构建文件'),
    'makefile': ('Makefile', '程序编译构建脚本'),
    'csv': ('CSV 表格', '逗号分隔的表格数据文件'),
    'tsv': ('TSV 表格', '制表符分隔的表格数据文件'),
    'asm': ('汇编源码', '底层汇编语言源代码'),
    'awk': ('AWK 脚本', 'Unix 文本处理脚本语言'),
    'clojure': ('Clojure 源码', '运行在 JVM 上的 Lisp 方言'),
    'coffeescript': ('CoffeeScript 源码', '编译为 JS 的脚本语言'),
    'elixir': ('Elixir 源码', '运行在 Erlang 虚拟机上的语言'),
    'erlang': ('Erlang 源码', '高并发容错的函数式语言'),
    'fortran': ('Fortran 源码', '科学计算领域的老牌语言'),
    'groovy': ('Groovy 源码', 'JVM 上的动态语言'),
    'julia': ('Julia 源码', '高性能科学计算语言'),
    'lisp': ('Lisp 源码', '历史悠久的函数式语言'),
    'matlab': ('MATLAB 脚本', '数值计算与工程分析工具'),
    'objectivec': ('Objective-C 源码', '苹果平台早期开发语言'),
    'ocaml': ('OCaml 源码', '函数式编程语言'),
    'pascal': ('Pascal 源码', '经典教学编程语言'),
    'prolog': ('Prolog 源码', '逻辑编程语言'),
    'tcl': ('Tcl 脚本', '工具命令语言'),
    'verilog': ('Verilog 源码', '硬件描述语言'),
    'vhdl': ('VHDL 源码', '硬件描述语言'),
    'vue': ('Vue 组件', 'Vue 前端框架单文件组件'),
    'jinja': ('Jinja 模板', 'Python 模板引擎文件'),
    'twig': ('Twig 模板', 'PHP 模板引擎文件'),
    'erb': ('ERB 模板', 'Ruby 模板文件'),
    'handlebars': ('Handlebars 模板', 'JavaScript 模板引擎文件'),
    'csproj': ('C# 项目文件', '.NET 项目配置文件'),
    'vcxproj': ('VC++ 项目文件', 'Visual C++ 工程文件'),
    'gradle': ('Gradle 构建脚本', 'JVM 项目构建工具'),
    'cmake': ('CMake 脚本', '跨平台构建配置'),
    'bazel': ('Bazel 构建脚本', 'Google 的构建工具'),
    'gemfile': ('Gemfile', 'Ruby 依赖管理文件'),
    'gemspec': ('Gemspec 文件', 'Ruby gem 包定义文件'),
    'zig': ('Zig 源码', '现代系统编程语言'),
    'solidity': ('Solidity 合约', '以太坊智能合约语言'),
    'smali': ('Smali 字节码', 'Android Dalvik 反汇编代码'),
    'proto': ('Proto 定义', 'Protocol Buffers 接口定义'),
    'textproto': ('TextProto 文件', '文本格式的 protobuf 数据'),
    'asp': ('ASP 脚本', '经典 ASP 服务端脚本'),
    'autohotkey': ('AutoHotkey 脚本', 'Windows 自动化脚本'),
    'autoit': ('AutoIt 脚本', 'Windows 自动化脚本'),
    'vba': ('VBA 宏', 'Office 文档内嵌宏代码'),
    'diff': ('Diff 补丁', '文件差异对比补丁'),
    'po': ('PO 翻译文件', 'gettext 多语言翻译文件'),
    'yara': ('YARA 规则', '恶意软件检测规则文件'),
    'latex': ('LaTeX 文档', '学术论文排版源文件'),
    'rst': ('reStructuredText', 'Python 文档常用的标记文本'),
    'cobol': ('COBOL 源码', '商业数据处理领域的老牌语言'),
    'dm': ('DM 源码', 'DreamMaker 游戏开发语言'),

    # ---------- 文档 ----------
    'pdf': ('PDF 文档', '便携式文档格式，跨平台查看打印'),
    'docx': ('Word 文档', 'Microsoft Word 新版文档'),
    'doc': ('Word 文档', 'Microsoft Word 旧版文档'),
    'xlsx': ('Excel 表格', 'Microsoft Excel 新版表格'),
    'xls': ('Excel 表格', 'Microsoft Excel 旧版表格'),
    'xlsb': ('Excel 二进制表格', 'Excel 二进制格式表格'),
    'pptx': ('PPT 演示', 'Microsoft PowerPoint 新版演示文稿'),
    'ppt': ('PPT 演示', 'Microsoft PowerPoint 旧版演示文稿'),
    'odt': ('ODT 文档', 'OpenDocument 文字文档'),
    'ods': ('ODS 表格', 'OpenDocument 电子表格'),
    'odp': ('ODP 演示', 'OpenDocument 演示文稿'),
    'rtf': ('RTF 文档', '富文本格式文档，跨编辑器通用'),
    'epub': ('EPUB 电子书', '电子书阅读器常用格式'),
    'ipynb': ('Jupyter 笔记本', '交互式数据分析/代码笔记本'),
    'one': ('OneNote 笔记', '微软 OneNote 笔记本文件'),
    'outlook': ('Outlook 邮件', '微软 Outlook 数据文件'),
    'mht': ('MHT 网页存档', '网页完整存档文件'),
    'sgml': ('SGML 文档', '通用标记语言文档'),

    # ---------- 文本 ----------
    'txt': ('纯文本', '最基础的文本文件'),
    'markdown': ('Markdown 文档', '用简单标记排版的文本文档'),

    # ---------- 归档/压缩 ----------
    'zip': ('ZIP 压缩包', '最常见的压缩归档格式'),
    'rar': ('RAR 压缩包', '压缩率高的专利压缩格式'),
    'sevenzip': ('7Z 压缩包', '开源高压缩率归档格式'),
    'tar': ('TAR 归档', 'Unix 标准打包格式（未压缩）'),
    'gzip': ('GZIP 压缩', 'GNU gzip 单文件压缩格式'),
    'bzip': ('BZIP2 压缩', '高压缩率单文件压缩格式'),
    'xz': ('XZ 压缩', 'LZMA2 高压缩率格式'),
    'ace': ('ACE 压缩包', '较老的压缩归档格式'),
    'cab': ('CAB 压缩包', 'Windows 安装包常用压缩格式'),
    'lha': ('LHA 压缩包', '早期 Amiga/PC 的压缩格式'),
    'mscompress': ('MS 压缩', '微软早期压缩格式'),
    'xar': ('XAR 归档', 'macOS 安装包使用的归档格式'),
    'zlibstream': ('Zlib 数据流', 'zlib 压缩的数据流'),
    'iso': ('ISO 光盘镜像', '光盘映像文件'),
    'dmg': ('DMG 镜像', 'macOS 磁盘映像安装包'),
    'squashfs': ('SquashFS 镜像', '只读压缩文件系统镜像'),

    # ---------- 可执行/二进制 ----------
    'pebin': ('PE 二进制', 'Windows PE 格式的可执行文件或动态库（exe/dll）'),
    'elf': ('ELF 程序', 'Linux/Unix 可执行程序'),
    'macho': ('Mach-O 程序', 'macOS 可执行程序'),
    'jar': ('JAR 包', 'Java 程序归档包'),
    'deb': ('DEB 包', 'Debian/Ubuntu 软件安装包'),
    'rpm': ('RPM 包', 'RedHat 系软件安装包'),
    'msi': ('MSI 安装包', 'Windows 安装程序包'),
    'apk': ('APK 安装包', 'Android 应用安装包'),
    'dex': ('DEX 文件', 'Android Dalvik 可执行文件'),
    'coff': ('COFF 目标文件', 'Windows 通用对象文件格式，编译器/链接器中间产物'),
    'wasm': ('WebAssembly 模块', '浏览器可运行的二进制模块'),
    'snap': ('Snap 应用包', 'Linux 通用应用打包格式'),
    'nupkg': ('NuGet 包', '.NET 依赖包'),
    'xpi': ('XPI 扩展包', 'Firefox 浏览器扩展'),
    'crx': ('CRX 扩展包', 'Chrome 浏览器扩展'),

    # ---------- 数据 ----------
    'sqlite': ('SQLite 数据库', '轻量级嵌入式数据库'),
    'npy': ('NumPy 数组', 'NumPy 二进制数组文件'),
    'npz': ('NumPy 压缩数组', 'NumPy 压缩归档数组'),
    'h5': ('HDF5 数据', '科学数据分层存储格式'),
    'parquet': ('Parquet 数据', '列式存储的数据格式'),
    'pickle': ('Pickle 对象', 'Python 序列化对象文件'),
    'onnx': ('ONNX 模型', '跨框架机器学习模型格式'),
    'pytorch': ('PyTorch 模型', 'PyTorch 训练模型权重'),
    'proteindb': ('蛋白质数据库', '生物信息学数据文件'),
    'rdf': ('RDF 数据', '资源描述框架数据'),
    'stlbinary': ('STL 3D 模型', '3D 打印二进制模型'),
    'stltext': ('STL 3D 模型', '3D 打印文本模型'),
    'sum': ('SUM 校验文件', '文件校验和清单'),

    # ---------- 音频 ----------
    'mp3': ('MP3 音频', '最常见的音乐音频格式'),
    'wav': ('WAV 音频', '未压缩的波形音频'),
    'flac': ('FLAC 音频', '无损压缩的高保真音频'),
    'ogg': ('OGG 音频', '开源免专利的音频格式'),
    'm4': ('M4A 音频', '苹果常用的音频格式'),
    'midi': ('MIDI 音频', '乐器数字接口音乐，记录音符信息'),
    'm3u': ('M3U 播放列表', '音视频播放列表文件'),

    # ---------- 视频 ----------
    'mp4': ('MP4 视频', '最常见的视频格式'),
    'mkv': ('MKV 视频', '开源容器格式，支持多音轨字幕'),
    'webm': ('WebM 视频', 'Google 推出的网络视频格式'),
    'flv': ('FLV 视频', '早期 Flash 视频格式'),
    '3gp': ('3GP 视频', '早期手机视频格式'),
    'swf': ('SWF 动画', 'Adobe Flash 动画文件'),

    # ---------- 字体 ----------
    'ttf': ('TTF 字体', 'TrueType 字体文件'),
    'otf': ('OTF 字体', 'OpenType 字体文件'),
    'woff': ('WOFF 字体', '网页用字体格式'),
    'woff2': ('WOFF2 字体', '新一代网页字体格式'),

    # ---------- 抓包/网络 ----------
    'pcap': ('PCAP 抓包文件', '网络数据包捕获格式，Wireshark 等抓包工具使用'),

    # ---------- 证书/密钥 ----------
    'pem': ('PEM 证书', 'Base64 编码的证书/密钥文件'),
    'crt': ('CRT 证书', 'SSL/TLS 证书文件'),

    # ---------- 配置/特殊 ----------
    'gitattributes': ('Git 属性文件', 'Git 仓库属性配置'),
    'gitmodules': ('Git 子模块文件', 'Git 子模块配置'),
    'ignorefile': ('忽略规则文件', '版本控制忽略规则'),
    'htaccess': ('Apache 配置', 'Apache 服务器配置文件'),
    'hcl': ('HCL 配置', 'Terraform 等工具使用的配置语言'),
    'applebplist': ('Apple 二进制属性列表', 'macOS/iOS 二进制 plist 配置'),
    'appleplist': ('Apple 属性列表', 'macOS/iOS 的 plist 配置文件'),
    'aidl': ('AIDL 接口', 'Android 接口定义语言文件'),
    'bib': ('BibTeX 文献', '参考文献条目文件'),
    'lnk': ('快捷方式', 'Windows 快捷方式文件'),
    'internetshortcut': ('网络快捷方式', '指向网址的快捷方式'),
    'torrent': ('BT 种子', 'BitTorrent 下载种子'),
    'ics': ('ICS 日历', '日历事件交换格式'),
    'vtt': ('VTT 字幕', '网页视频字幕格式'),
    'srt': ('SRT 字幕', '视频字幕文件'),
    'eml': ('EML 邮件', '单封电子邮件文件'),
    'chm': ('CHM 帮助文档', 'Windows 帮助文件'),
    'hlp': ('HLP 帮助文件', '旧版 Windows 帮助文件'),
    'winregistry': ('Windows 注册表', '注册表导出文件'),
    'dsstore': ('.DS_Store', 'macOS 文件夹元数据文件'),
    'thumbsdb': ('缩略图缓存', 'Windows 缩略图缓存'),
    'cat': ('CAT 目录文件', 'Windows 安全目录文件'),
    'mum': ('MUM 文件', 'Windows 更新清单文件'),
    'dwg': ('DWG 图纸', 'AutoCAD 原生图纸格式'),
    'dxf': ('DXF 图纸', 'AutoCAD 交换格式'),
    'qt': ('Qt 界面文件', 'Qt 框架界面定义文件'),
    'postscript': ('PostScript 文件', '打印排版描述文件'),
    'pdb': ('PDB 调试符号', '程序调试符号文件'),
    'randombytes': ('随机字节', '无结构的随机二进制数据'),
    'randomtxt': ('随机文本', '无规律的随机文本'),

    # ---------- 特殊 ----------
    'unknown': ('未知格式', '无法识别该文件的类型'),
    'empty': ('空文件', '文件内容为空'),
}


def translate(label):
    """把 Magika 的英文 label 翻译成通俗中文，未命中也回退为中文兜底。"""
    key = (label or 'unknown').lower()
    if key in FILE_TRANSLATIONS:
        format_zh, desc_zh = FILE_TRANSLATIONS[key]
        return format_zh, desc_zh
    # 未命中翻译表：格式名用大写 label（保留技术标识），描述用中文兜底
    fallback_format = (label or 'unknown').upper()
    fallback_desc = f'该文件被 Magika 识别为 {fallback_format} 类型，暂未收录通俗释义'
    return fallback_format, fallback_desc


def get_file_info(content):
    """基于文件字节内容识别类型（不依赖扩展名，更可靠）。"""
    if not content:
        format_zh, desc_zh = translate('empty')
        return {
            'format': format_zh,
            'mime_type': 'application/octet-stream',
            'description': desc_zh,
            'group': None,
            'score': 0,
            'extensions': [],
            'is_text': False,
            'overwrite_reason': None,
            'is_empty': True,
            'unrecognized': True,
        }

    result = magika.identify_bytes(content)
    info = result.output

    label = info.label or 'unknown'

    # Magika 对无法识别的内容会返回 unknown（低置信度被降级），视为"非可识别文件"
    unrecognized = label in ('unknown', 'empty')

    # 翻译层：把 Magika 的英文 label/描述转为通俗中文
    format_zh, desc_zh = translate(label)

    return {
        'format': format_zh,
        'mime_type': info.mime_type or 'application/octet-stream',
        'description': desc_zh,
        'group': info.group,
        'score': round(result.score, 4),
        'extensions': info.extensions or [],
        'is_text': info.is_text,
        'overwrite_reason': (
            result.prediction.overwrite_reason.value
            if result.prediction and result.prediction.overwrite_reason is not None
            else None
        ),
        'is_empty': False,
        'unrecognized': unrecognized,
    }


# Magika 只分析文件开头字节，读 1MB 足够，避免大文件占满内存
MAX_READ_SIZE = 1024 * 1024


@app.route('/api/identify', methods=['POST'])
def identify():
    if 'file' not in request.files:
        return jsonify({'error': '没有收到文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    # 先拿到完整文件大小（seek 到末尾再回退，不依赖 Content-Length 头）
    file.stream.seek(0, os.SEEK_END)
    full_size = file.stream.tell()
    file.stream.seek(0)

    # 只读取文件开头一部分字节交给 Magika 识别
    content = file.read(MAX_READ_SIZE)

    try:
        result = get_file_info(content)
    except Exception as exc:
        app.logger.error('识别失败: %s', exc)
        return jsonify({'error': f'识别失败: {exc}'}), 500

    result['filename'] = file.filename

    # 后端日志：记录识别请求
    write_log('identify_request', {
        'filename': file.filename,
        'size': full_size,
        'format': result['format'],
        'unrecognized': result['unrecognized'],
    })

    return jsonify(result)


@app.route('/api/log', methods=['POST'])
def receive_log():
    """接收前端上报的用户操作日志，追加写入 logs/app.log。"""
    data = request.get_json(silent=True) or {}
    event_type = data.get('type', '')
    # 只保留业务字段（去掉 ts/type 元字段），与后端日志格式保持一致
    detail = {k: v for k, v in data.items() if k not in ('ts', 'type')}
    write_log(event_type, detail, side='frontend')
    return jsonify({'ok': True})


def write_log(event_type, payload, side='backend'):
    """把日志条目追加写入 logs/app.log（自动创建目录）。"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'app.log')
    from datetime import datetime
    line = '[{}] [{}] [{}] {}'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        side,
        event_type,
        json.dumps(payload, ensure_ascii=False),
    )
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


if __name__ == '__main__':
    # 本机开发：绑定 127.0.0.1 不暴露到局域网；
    # 关闭 reloader 避免 Magika 模型被加载两次（前端由 Vite 单独热更新）
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
