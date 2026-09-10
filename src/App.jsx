import { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { identifyFile, sendLog } from './services/api';

// 动画帧序列：睡1 → 睡3（跳过睡2）
const sleepFrames = [1, 3];

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sleepFrame, setSleepFrame] = useState(0);
  const [message, setMessage] = useState('');
  const [unrecognized, setUnrecognized] = useState(false);
  const [isDirectory, setIsDirectory] = useState(false);

  // 仅在待机状态推进睡眠帧动画，识别/报错时暂停，避免空转
  const idle = !isLoading && !unrecognized && !isDirectory;

  useEffect(() => {
    if (!idle) return;
    const timer = setInterval(() => {
      setSleepFrame((prev) => (prev + 1) % sleepFrames.length);
    }, 500);
    return () => clearInterval(timer);
  }, [idle]);

  const onDrop = async (acceptedFiles) => {
    // 文件夹已被 onDropCapture 拦截并设置 isDirectory=true，
    // 这里如果再进来说明不是文件夹，继续正常流程
    setMessage('');
    setIsDirectory(false);

    const file = acceptedFiles[0];
    if (!file) return;

    // 所有文件都交给后端 Magika 识别
    const formData = new FormData();
    formData.append('file', file);
    sendLog('drop_file', { name: file.name, size: file.size, mime_type: file.type });

    setIsLoading(true);
    setResult(null);
    setUnrecognized(false);

    try {
      const res = await identifyFile(formData);
      setResult(res.data);
      setUnrecognized(res.data.unrecognized === true);
      sendLog('identify_result', { name: file.name, format: res.data.format, unrecognized: res.data.unrecognized });
    } catch (error) {
      setMessage('识别失败，请确保后端服务已启动 (http://localhost:5000)');
      setTimeout(() => setMessage(''), 5000);
      sendLog('identify_error', { name: file.name, error: String(error) });
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  // 原生 drop 拦截：用 webkitGetAsEntry 精准判断目录
  // 在 react-dropzone 处理之前执行，阻止事件传播
  const handleDropCapture = async (e) => {
    const items = e.dataTransfer?.items;
    if (!items || items.length === 0) return;

    // 用 webkitGetAsEntry 判断是否目录（Chromium/Edge/Firefox 支持）
    for (let i = 0; i < items.length; i++) {
      const entry = items[i].webkitGetAsEntry?.();
      if (entry && entry.isDirectory) {
        e.preventDefault();
        e.stopPropagation();
        sendLog('drop_directory', { name: entry.name });
        setMessage('');
        setResult(null);
        setUnrecognized(false);
        setIsDirectory(true);
        return;
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    noKeyboard: true,
  });

  return (
    // 1. 全屏背景图
    <div
      className="min-h-screen w-full bg-cover bg-center bg-fixed flex items-center justify-center p-6"
      style={{ backgroundImage: "url('/backgrounds/背景.jpg')" }}
    >
      {/* 背景柔光遮罩 */}
      <div className="absolute inset-0 bg-white/20 backdrop-blur-sm -z-0"></div>

      {/* 提示消息 */}
      {message && (
        <div className="fixed top-8 left-1/2 -translate-x-1/2 z-50 bg-pink-500 text-white px-8 py-4 rounded-2xl shadow-2xl text-xl font-bold animate-bounce">
          {message}
        </div>
      )}

      {/* 2. 主容器：宽度更大，比例调整为 2:1 */}
      <div className="relative z-10 w-full max-w-7xl flex flex-col lg:flex-row gap-8 items-stretch">

        {/* ========== 左侧卡片（占比 2/3） ========== */}
        <div
          {...getRootProps()}
          onDropCapture={handleDropCapture}
          className={`
            flex-[2] bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-10
            border-4 border-dashed transition-all duration-300
            ${isDragActive ? 'border-pink-400 bg-pink-50/80' : 'border-pink-200 hover:border-pink-400'}
            flex flex-col items-center justify-center min-h-[420px] cursor-pointer relative
          `}
        >
          <input {...getInputProps()} />

          {/* 装饰图1：左上 */}
          <div className="absolute -top-4 -left-4 w-40 h-40 opacity-100 rotate-12 pointer-events-none">
            <img src="/deco1.png" alt="装饰" className="w-full h-full object-contain" />
          </div>
          {/* 装饰图2：右下 */}
          <div className="absolute -bottom-4 -right-4 w-[67px] h-[67px] opacity-100 -rotate-6 pointer-events-none">
            <img src="/deco2.png" alt="装饰" className="w-full h-full object-contain" />
          </div>

          {isLoading ? (
            // 加载状态（保留在动画预留区的位置）
            <div className="text-center pointer-events-none">
              <img
                src="/思考.png"
                alt="思考中"
                className="w-32 h-32 object-contain mx-auto mb-4 animate-spin"
                style={{ animationDuration: '2s' }}
              />
              <p className="text-pink-500 font-semibold text-lg">正在识别…</p>
            </div>
          ) : (
            // 正常状态：文字 + 中央动画预留位
            <div className="text-center w-full flex flex-col items-center pointer-events-none">
              {/* 上方提示文字 */}
              <p className="text-2xl font-bold text-gray-700">
                {isDragActive ? '📥 松开手指上传' : '📂 拖拽文件到此处'}
              </p>
              
              {/* ===== ★ 中央动画区域 ★ ===== */}
              <div className="w-60 h-60 my-6 flex items-center justify-center pointer-events-none">
                {(unrecognized || isDirectory) ? (
                  <img
                    src="/deco7.png"
                    alt="无法识别"
                    className="w-full h-full object-contain animate-roly-poly"
                  />
                ) : (
                  <img
                    src={`/睡${sleepFrames[sleepFrame]}.png`}
                    alt="动画"
                    className="w-full h-full object-contain"
                  />
                )}
              </div>

              {/* 下方操作提示 */}
              <p className="text-base text-gray-400 mt-2">
                或 <span className="text-pink-400 font-semibold">点击</span> 此区域选择文件
              </p>
              <p className="text-xs text-pink-300 mt-3">✨ 支持任意格式 ✨</p>
            </div>
          )}
        </div>

        {/* ========== 右侧卡片（占比 1/3） ========== */}
        <div className="flex-1 bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-10 relative min-h-[420px] flex flex-col">
          {/* 装饰图3：右上 */}
          <div className="absolute -top-4 -right-4 w-20 h-20 opacity-100 -rotate-6">
            <img src="/deco3.png" alt="装饰" className="w-full h-full object-contain" />
          </div>
          {/* 装饰图4：左下 */}
          <div className="absolute -bottom-4 -left-4 w-14 h-14 opacity-100 rotate-12">
            <img src="/deco4.png" alt="装饰" className="w-full h-full object-contain" />
          </div>

          <h2 className="text-2xl font-bold text-pink-600 mb-5 flex items-center gap-2">
            <span>📋</span> 文件解释
          </h2>

          {isDirectory ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center px-4">
              <div className="text-7xl mb-5">🐷</div>
              <p className="text-2xl font-bold text-pink-500 leading-relaxed">
                小猪不吃文件夹，只吃文件
              </p>
            </div>
          ) : result ? (
            result.unrecognized ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center px-4">
                <div className="text-7xl mb-5">🐷</div>
                {result.is_empty ? (
                  <>
                    <p className="text-2xl font-bold text-pink-500 leading-relaxed">
                      文件内容为空
                    </p>
                    <p className="text-base text-gray-400 mt-3">
                      0 字节，没有可以识别的内容
                    </p>
                  </>
                ) : (
                  <p className="text-2xl font-bold text-pink-500 leading-relaxed">
                    小猪还不会吃这个，换成其他文件试试
                  </p>
                )}
              </div>
            ) : (
            <div className="space-y-4 text-gray-700 flex-1 overflow-y-auto">
              <div className="bg-pink-50/80 rounded-xl p-4">
                <p className="text-sm text-pink-400 font-medium">文件格式</p>
                <p className="text-lg font-bold text-gray-800 break-all">
                  {result.format || result.mime_type || '未知'}
                </p>
              </div>
              <div className="bg-pink-50/80 rounded-xl p-4">
                <p className="text-sm text-pink-400 font-medium">用途描述</p>
                <p className="text-base text-gray-700 leading-relaxed">
                  {result.description || '暂无描述信息'}
                </p>
              </div>
              {result.mime_type && (
                <div className="bg-pink-50/80 rounded-xl p-4">
                  <p className="text-sm text-pink-400 font-medium">MIME 类型</p>
                  <p className="text-sm text-gray-600 break-all">{result.mime_type}</p>
                </div>
              )}
              {result.extensions && result.extensions.length > 0 && (
                <div className="bg-pink-50/80 rounded-xl p-4">
                  <p className="text-sm text-pink-400 font-medium">常见扩展名</p>
                  <p className="text-sm text-gray-600 break-all">{result.extensions.join(' / ')}</p>
                </div>
              )}
              {typeof result.score === 'number' && result.score > 0 && (
                <div className="bg-pink-50/80 rounded-xl p-4">
                  <p className="text-sm text-pink-400 font-medium">置信度</p>
                  <p className="text-sm text-gray-600">{(result.score * 100).toFixed(1)}%</p>
                </div>
              )}
            </div>
            )
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-300">
              <div className="text-7xl mb-4">🔍</div>
              <p className="text-xl font-medium">等待上传</p>
              <p className="text-sm text-center">左侧拖入文件<br />立即解析用途</p>
            </div>
          )}
        </div>
      </div>

      {/* ========== 5、6 两处额外装饰（画面四角） ========== */}
      <img
        src="/deco5.png"
        alt="装饰"
        className="fixed top-6 left-6 w-40 h-40 opacity-100 hidden sm:block"
      />
      <span
        className="fixed top-16 left-[240px] text-7xl font-extrabold text-blue-300 drop-shadow-lg hidden sm:block select-none"
      >
        爱吃文件的猪
      </span>
      <img
        src="/deco6.png"
        alt="装饰"
        className="fixed bottom-6 right-6 w-[120px] h-[120px] opacity-100 -rotate-6 hidden sm:block"
      />
    </div>
  );
}

export default App;