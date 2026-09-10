import axios from 'axios';

export const API_BASE = 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

export async function identifyFile(formData) {
  // 不手动设置 Content-Type，让 axios/浏览器自动附带 multipart boundary
  return apiClient.post('/api/identify', formData);
}

// 前端操作日志上报：失败不影响主流程
export async function sendLog(eventType, payload) {
  const entry = { ts: new Date().toISOString(), type: eventType, ...payload };
  console.log('[LOG]', entry);
  try {
    await apiClient.post('/api/log', entry);
  } catch {
    // 日志上报失败静默忽略
  }
}
