#!/usr/bin/env bash
# 将 /dev/video0 编码为 H.265 并通过 UDP 发送
set -euo pipefail
DEV=${1:-/dev/video0}
DEST=${2:-127.0.0.1:5000}
FPS=${3:-30}
BR=${4:-4M}

ffmpeg -f v4l2 -i "$DEV" -r "$FPS" \
  -vcodec libx265 -preset veryfast -tune zerolatency -x265-params "keyint=1:bframes=0" -b:v "$BR" \
  -an -f mpegts "udp://$DEST?pkt_size=1200"
