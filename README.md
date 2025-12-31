# drone-system-fullstack

本仓库汇总了无人机相关的多个子项目（可视化大屏、端云定位/检测、FastAPI+静态页、路线规划与 AI 交互等），便于统一归档与演示。

## 项目结构

- [项目总览](项目总览.md)
- [面向低空作业的无人设备安全系统](面向低空作业的无人设备安全系统/)
  - 路线规划（待优化）：[面向低空作业的无人设备安全系统/无人机线路规划（待优化）](面向低空作业的无人设备安全系统/无人机线路规划（待优化）/)
  - 已完成网页与 AI：[面向低空作业的无人设备安全系统/已完成网页与ai](面向低空作业的无人设备安全系统/已完成网页与ai/)
  - 未添加 AI 的 HTML：[面向低空作业的无人设备安全系统/未添加AI的html](面向低空作业的无人设备安全系统/未添加AI的html/)
- 可视化大屏（Vite+React）：[无人机可视化大屏（Vite+React）](无人机可视化大屏（Vite+React）/)
- 物体箱定位系统（Flask 端云）：[无人机物体箱定位系统（Flask端云）](无人机物体箱定位系统（Flask端云）/)
- Monorepo（FastAPI+静态页）：[无人机项目Monorepo（FastAPI+静态页）](无人机项目Monorepo（FastAPI+静态页）/)

## 快速开始（按子项目）

### 1) 可视化大屏（Vite+React）

在 [无人机可视化大屏（Vite+React）](无人机可视化大屏（Vite+React）/) 目录：

- 安装依赖：`pnpm install`
- 启动开发：`pnpm dev`

### 2) 物体箱定位系统（Flask 端云）

在 [无人机物体箱定位系统（Flask端云）](无人机物体箱定位系统（Flask端云）/) 目录查看：

- [无人机物体箱定位系统（Flask端云）/README.md](无人机物体箱定位系统（Flask端云）/README.md)
- Windows 测试指南：[无人机物体箱定位系统（Flask端云）/docs/README_Windows测试指南.md](无人机物体箱定位系统（Flask端云）/docs/README_Windows测试指南.md)

### 3) Monorepo（FastAPI + 静态页）

在 [无人机项目Monorepo（FastAPI+静态页）](无人机项目Monorepo（FastAPI+静态页）/) 目录查看：

- 运行说明：[无人机项目Monorepo（FastAPI+静态页）/README-RUN.md](无人机项目Monorepo（FastAPI+静态页）/README-RUN.md)

### 4) 路线规划与 AI 交互（POE）

在 [面向低空作业的无人设备安全系统](面向低空作业的无人设备安全系统/) 目录查看：

- 项目说明：[面向低空作业的无人设备安全系统/项目说明.md](面向低空作业的无人设备安全系统/项目说明.md)

提示：AI 密钥通过环境变量提供（示例脚本见 `set_env.example.ps1/.cmd`）。请不要把真实密钥写入仓库。

## 许可证

本仓库使用 MIT License，详见 [LICENSE](LICENSE)。
