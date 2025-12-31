# 以 PowerShell 运行，将本机摄像头流推送为 H.265 到 UDP 端口
# 需要安装 ffmpeg，并在 PATH 中可用

param(
  [string]$DeviceIndex = "0",
  [string]$Dest = "127.0.0.1:5000",
  [int]$Fps = 30,
  [string]$Bitrate = "4M"
)

# Windows dshow 示例；若使用其他采集方式请调整
ffmpeg -f dshow -i video="video=$DeviceIndex" -r $Fps `
  -vcodec libx265 -preset veryfast -tune zerolatency -x265-params "keyint=1:bframes=0" -b:v $Bitrate `
  -an -f mpegts udp://$Dest?pkt_size=1200
