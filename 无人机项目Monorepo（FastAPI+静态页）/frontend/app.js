let ws;
const statusEl = () => document.getElementById('status');

document.getElementById('btnConnect').onclick = () => {
  const url = document.getElementById('wsUrl').value;
  ws = new WebSocket(url);
  ws.onopen = () => statusEl().textContent = '已连接';
  ws.onclose = () => statusEl().textContent = '已关闭';
  ws.onerror = (e) => statusEl().textContent = '错误';
  ws.onmessage = (ev) => {
    console.log('WS <-', ev.data);
    try { const obj = JSON.parse(ev.data); statusEl().textContent = JSON.stringify(obj); }
    catch { statusEl().textContent = ev.data; }
  };
};

document.getElementById('btnSend').onclick = () => {
  if (!ws || ws.readyState !== 1) return alert('未连接');
  const payload = {
    type: 'path.update',
    points: [
      [116.39, 39.9, 100, 5],
      [116.40, 39.905, 100, 5],
      [116.41, 39.91, 100, 5]
    ]
  };
  ws.send(JSON.stringify(payload));
};
