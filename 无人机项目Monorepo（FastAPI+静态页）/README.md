# 无人机项目 Monorepo

本仓库对应《项目总方案与实施手册》，包含以下模块：
- rc-bridge-mcu: MCU固件（占位）
- onboard: 机载ROS2节点（占位）
- backend: FastAPI服务（规划、WS、MQTT桥接）
- frontend: 前端静态页面（Mapbox+WS）
- video: 视频链路脚本（ffmpeg 示例）
- ops: 运维编排（Docker Compose/EMQX）
- docs: 文档

快速开始：请先进入 backend/ 按 README 启动后端，再打开 frontend/index.html 进行基础联通验证。