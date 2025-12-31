# Python环境配置信息

## 基本信息

- Python版本: 3.12.9
- 环境管理工具: Mini Conda

## 已安装的Python库

| 包名 | 版本 |
|------|------|
| anaconda-anon-usage | 0.5.0 |
| annotated-types | 0.6.0 |
| archspec | 0.2.3 |
| boltons | 24.1.0 |
| Brotli | 1.0.9 |
| certifi | 2025.1.31 |
| cffi | 1.17.1 |
| charset-normalizer | 3.3.2 |
| colorama | 0.4.6 |
| conda | 25.1.1 |
| conda-anaconda-telemetry | 0.1.2 |
| conda-anaconda-tos | 0.1.2 |
| conda-content-trust | 0.2.0 |
| conda-libmamba-solver | 25.1.1 |
| conda-package-handling | 2.4.0 |
| conda_package_streaming | 0.11.0 |
| cryptography | 43.0.3 |
| distro | 1.9.0 |
| frozendict | 2.4.2 |
| idna | 3.7 |
| jsonpatch | 1.33 |
| jsonpointer | 2.1 |
| libmambapy | 2.0.5 |
| markdown-it-py | 2.2.0 |
| mdurl | 0.1.0 |
| menuinst | 2.2.0 |
| packaging | 24.2 |
| pip | 25.0 |
| platformdirs | 3.10.0 |
| pluggy | 1.5.0 |
| pycosat | 0.6.6 |
| pycparser | 2.21 |
| pydantic | 2.10.3 |
| pydantic_core | 2.27.1 |
| Pygments | 2.15.1 |
| PySocks | 1.7.1 |
| requests | 2.32.3 |
| rich | 13.9.4 |
| ruamel.yaml | 0.18.6 |
| ruamel.yaml.clib | 0.2.8 |
| setuptools | 75.8.0 |
| tqdm | 4.67.1 |
| truststore | 0.10.0 |
| typing_extensions | 4.12.2 |
| urllib3 | 2.3.0 |
| wheel | 0.45.1 |
| win-inet-pton | 1.1.0 |
| zstandard | 0.23.0 |

## 项目结构

```
PoeAPI.py
requirements.txt
未添加AI的html/
    高德.html
    leaflet.html
    readme.md
无人机线路规划（待优化）/
    index.html
    main.py
    run.bat
    styles.css
    __pycache__/
        main.cpython-312.pyc
已完成网页与ai/
    index.html
    main.py
    response.txt
    run.bat
    styles.css
```

## 环境说明

此环境通过Mini Conda进行管理，使用Python 3.12.9版本。主要包含了数据处理、Web请求、加密等常用Python库。该环境配置支持当前工作区中的无人机线路规划及网页交互功能。

## 如何使用

1. **查看环境信息**：
   ```bash
   conda info
   ```

2. **查看安装的包**：
   ```bash
   pip list
   ```

3. **安装新包**：
   ```bash
   conda install 包名
   # 或者
   pip install 包名
   ```

4. **更新环境文件**：
   ```bash
   pip freeze > requirements.txt
   ```