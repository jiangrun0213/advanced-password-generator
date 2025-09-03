# 高级密码生成器

一个功能强大的密码生成和文件解密工具，支持多种密码生成模式和文件解密功能。

## 功能特性

### 🔐 密码生成功能
- 支持1-8位数字密码生成
- 支持月日(MMDD)和日月(DDMM)密码格式
- 多前缀和多后缀组合支持
- 数字范围选择（如1980-1999）
- 字符范围选择（A-Z, a-z, 0-9等）
- 哈希算法支持：MD5, SHA1, SHA256, SM3
- 哈希值提取功能（可设置起始位置和长度）

### 🔓 文件解密功能
支持使用密码字典解密以下文件类型：

✅ **ZIP文件** (.zip) - 完全支持密码破解  
✅ **RAR文件** (.rar) - 完全支持密码破解  
✅ **Word文档** (.doc, .docx) - 支持Office文档解密  
✅ **Excel文档** (.xls, .xlsx) - 支持Office文档解密  
✅ **PowerPoint文档** (.ppt, .pptx) - 支持Office文档解密  
❌ **7z文件** (.7z) - 暂不支持（技术限制）

### ⚡ 其他特性
- 图形用户界面（GUI）操作
- 实时进度显示
- GPU加速支持（可选）
- 批量密码生成
- 密码字典管理

## 安装说明

### 方法1：使用可执行文件（推荐）
1. 下载 `dist/高级密码生成器.exe`
2. 双击运行即可

### 方法2：从源代码运行
```bash
# 克隆仓库
git clone https://github.com/your-username/advanced-password-generator.git
cd advanced-password-generator

# 安装依赖
pip install -r requirements.txt

# 运行程序
python advanced_password_generator.py
```

### 依赖库
```bash
pip install tkinter hashlib gmssl itertools threading os re zipfile rarfile msoffcrypto-tool
```

## 使用说明

### 密码生成步骤
1. 在左侧设置密码类型（1-8位数字、月日、日月）
2. 添加前缀和后缀（支持固定字符、数字范围、字符范围）
3. 在中间设置输出选项（原始密码或哈希值）
4. 设置输出文件名
5. 点击"开始生成"

### 文件解密步骤
1. 先生成密码字典或选择已有字典
2. 在右侧选择要解密的加密文件
3. 点击"开始解密"
4. 查看解密结果

## 文件结构
```
advanced-password-generator/
├── advanced_password_generator.py  # 主程序
├── file_decryptor.py               # 文件解密模块
├── gpu_utils.py                    # GPU工具模块
├── 使用说明.txt                    # 详细使用说明
├── requirements.txt                # 依赖库列表
├── README.md                       # 项目说明
└── dist/
    └── 高级密码生成器.exe          # 可执行文件
```

## 技术说明

### 支持的哈希算法
- **MD5**: 128位哈希值
- **SHA1**: 160位哈希值  
- **SHA256**: 256位哈希值
- **SM3**: 国密算法，256位哈希值

### 解密原理
程序使用密码字典暴力破解方式，逐个尝试字典中的密码来解密文件。支持的文件类型使用相应的库进行解密：
- ZIP文件: `zipfile` 库
- RAR文件: `rarfile` 库  
- Office文档: `msoffcrypto-tool` 库

## 注意事项

⚠️ **重要提示**:
- 密码组合数量会指数级增长，请谨慎设置
- 大量组合可能需要较长时间生成
- 解密过程耗时取决于字典大小和文件复杂度
- 建议先测试小范围再生成完整字典
- 仅用于合法用途，请遵守相关法律法规

## 更新日志

### v3.0 (2025-09-03)
- 添加完整的文件类型支持说明
- 更新程序内帮助内容
- 优化界面显示

### v2.0 (2025-09-02)
- 优化界面布局，显示全部选项
- 添加窗口居中功能
- 支持滚动查看所有设置

### v1.0 (2025-09-01)
- 初始版本发布
- 基本密码生成功能
- 支持哈希算法和提取功能

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 技术支持

如果遇到问题，请：
1. 检查Python环境是否正确安装
2. 确保所有依赖库已安装
3. 查看使用说明文档
4. 提交Issue描述具体问题
