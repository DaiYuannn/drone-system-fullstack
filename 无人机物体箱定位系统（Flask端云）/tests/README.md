# 测试文件组织说明

本目录包含无人机定位系统的所有测试文件，按功能和平台进行分类组织。

## 目录结构

### windows/ - Windows平台专用测试
```
windows/
├── run_test.bat                    # Windows快速测试脚本
├── run_windows_test.bat           # Windows完整测试脚本  
└── setup_windows_test_env.bat     # Windows测试环境设置
```

**用途**: Windows平台下的系统测试，包括环境设置、依赖安装和功能验证。

**运行方式**:
```bash
cd tests/windows
setup_windows_test_env.bat    # 设置环境（首次运行）
run_windows_test.bat          # 运行完整测试
```

### simulation/ - 模拟测试工具
```
simulation/
├── create_test_images.py      # 生成测试用QR码图片
├── flight_controller_test.py  # 飞控系统模拟测试
└── gps_simulator.py          # GPS数据模拟器
```

**用途**: 在没有真实硬件的情况下进行功能测试和开发验证。

**运行方式**:
```bash
cd tests/simulation
python create_test_images.py      # 生成测试图片
python gps_simulator.py          # 模拟GPS数据
python flight_controller_test.py # 模拟飞控操作
```

### integration/ - 集成测试
```
integration/
├── data_transmission_tester.py   # 数据传输功能测试
├── test_upload.py                # 文件上传功能测试  
├── crypto_roundtrip_test.py      # 本地加解密回环测试
└── vision_encrypt_upload.py      # 读取图片识别并加密上传的测试
```

**用途**: 测试各模块间的集成功能，验证端到端的数据流。

**运行方式**:
```bash
cd tests/integration
python data_transmission_tester.py  # 测试数据传输
python test_upload.py              # 测试文件上传
python crypto_roundtrip_test.py    # 本地加密解密回环
python vision_encrypt_upload.py --image ../test_image.jpg  # 视觉识别并加密上传
```

## 测试依赖

所有测试共享的依赖包列在 `requirements_test.txt` 中：

```bash
pip install -r requirements_test.txt
```

主要测试依赖：
- `requests` - HTTP客户端测试
- `python-socketio[client]` - WebSocket测试
- `pillow` - 图像处理测试
- `qrcode[pil]` - QR码生成测试
- `numpy` - 数值计算支持
- `pycryptodome` - AES-GCM 加解密支持

启用加密测试：
- 设置环境变量 TEST_ENCRYPT=1；可选设置 DRONE_AES_KEY_B64/SERVER_AES_KEY_B64 以匹配密钥。

## 测试策略

1. **单元测试**: 各simulation模块独立测试单个功能
2. **集成测试**: integration模块测试模块间协作
3. **平台测试**: windows模块验证特定平台兼容性
4. **端到端测试**: 完整的无人机→服务器数据流测试

## 测试数据

测试过程中生成的数据：
- 测试图片: `simulation/` 模块生成
- 日志文件: 各测试模块在运行目录生成
- 临时文件: 测试完成后自动清理

## 注意事项

1. **网络依赖**: 集成测试需要网络连接到服务器
2. **权限要求**: Windows测试可能需要管理员权限
3. **环境隔离**: 建议使用虚拟环境运行测试
4. **资源清理**: 测试完成后注意清理临时文件

## 添加新测试

添加新测试文件时，请按照以下原则：
- Windows专用功能 → `windows/`
- 硬件模拟功能 → `simulation/`  
- 系统集成功能 → `integration/`
- 更新本README说明新增的测试内容