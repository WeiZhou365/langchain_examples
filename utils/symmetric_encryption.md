# 对称加密工具使用指南

这个Python脚本提供了一个简单易用的对称加密和解密工具，使用Fernet加密算法来保护敏感数据。

## 功能特性

- **对称加密**: 使用相同的密钥进行加密和解密
- **基于密码的密钥派生**: 使用PBKDF2算法从密码生成安全的加密密钥
- **命令行界面**: 支持通过命令行参数进行操作
- **安全性**: 使用现代加密标准，包含身份验证和完整性验证

## 安装依赖

确保已安装所需的依赖包：

```bash
pip install cryptography
```

## 基本用法

### 1. 加密数据

使用默认密码加密：
```bash
python symmetric_encryption.py encrypt --data "需要加密的敏感信息"
```

使用自定义密码加密：
```bash
python symmetric_encryption.py encrypt --data "xxxxxxxx" --password "我的安全密码123"
```

### 2. 解密数据

使用默认密码解密：
```bash
python symmetric_encryption.py decrypt --data "gAAAAABm..."
```

使用自定义密码解密：
```bash
python symmetric_encryption.py decrypt --data "gAAAAABm..." --password "我的安全密码123"
```

## 命令行参数

| 参数 | 简写 | 说明 | 必需 |
|------|------|------|------|
| `operation` | - | 操作类型：`encrypt` 或 `decrypt` | 是 |
| `--data` | `-d` | 要加密的数据或要解密的加密数据 | 是 |
| `--password` | `-p` | 密钥派生密码（默认：my_secure_password_123） | 否 |

## 使用示例

### 示例1：加密API密钥

```bash
# 加密您的Google API密钥
python symmetric_encryption.py encrypt -d "xxxxxxxx" -p "强密码2024"
```

输出：
```
Original Data: xxxxxxxxx
Encrypted Data: gAAAAABmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 示例2：解密数据

```bash
# 解密上面加密的数据
python symmetric_encryption.py decrypt -d "gAAAAABmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" -p "强密码2024"
```

输出：
```
Encrypted Data: gAAAAABmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Decrypted Data: xxxxxxxxxx
```

## 代码结构

### SymmetricKeyEncryption 类

- `__init__(password=None)`: 初始化加密器，可选择使用密码或随机密钥
- `encrypt_data(data)`: 加密字符串数据
- `decrypt_data(encrypted_data)`: 解密加密数据
- `get_key()`: 获取base64编码的加密密钥

### 主要方法

- `_derive_key_from_password()`: 使用PBKDF2从密码派生密钥
- 使用SHA256哈希算法
- 100,000次迭代增强安全性
- 固定盐值（生产环境建议使用随机盐值）

## 重要注意事项

1. **密码安全性**: 使用强密码，包含大小写字母、数字和特殊字符
2. **密码一致性**: 加密和解密必须使用相同的密码
3. **数据备份**: 请妥善保存加密数据和密码，丢失任一都将无法恢复原始数据
4. **生产环境**: 在生产环境中，建议使用随机生成的盐值而不是固定盐值

## 获取帮助

查看完整的帮助信息：
```bash
python symmetric_encryption.py --help
```

## 安全最佳实践

- 不要在命令行历史中暴露敏感密码
- 考虑使用环境变量存储密码
- 定期更换加密密码
- 在共享环境中使用时要特别小心
- 在生产环境中使用随机盐值

## 技术细节

- **加密算法**: Fernet (基于AES 128 CBC + HMAC SHA256)
- **密钥派生**: PBKDF2 with SHA256
- **编码方式**: Base64 URL-safe编码
- **Python版本**: 需要Python 3.6+

这个工具特别适合加密配置文件中的API密钥、数据库密码等敏感信息。