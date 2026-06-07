# 简易密码管理器

一个极简的本地密码管理工具，支持命令行和图形界面两种模式。

---

## 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [环境配置](#环境配置)
- [快速开始](#快速开始)
- [代码详解](#代码详解)
- [数据库设计](#数据库设计)
- [技术栈](#技术栈)

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 🔐 生成密码 | 可配置长度和字符集（大小写、数字、符号） |
| ✏️ 输入密码 | 手动输入密码并保存 |
| 🔄 修改密码 | 5种模式：手动/随机/纯数字/纯字母/数字+字母 |
| 💾 保存记录 | 使用 SQLite 存储密码信息 |
| 📋 查看列表 | 查看密码详情及历史修改记录 |
| 📋 复制密码 | 一键复制密码到剪贴板 |
| 🗑️ 删除记录 | 选择指定凭据删除（级联删除所有密码记录） |
| 💪 强度检测 | 实时显示密码强度和熵值 |
| 🖼️ 图形界面 | 使用 easygui 弹窗交互 |

---

## 项目结构

```
easy_psw_manager/
├── main.py          # 主程序（easygui 图形界面）
├── database.py      # SQLite 数据库操作（双表结构）
├── password_gen.py  # 密码生成逻辑
├── strength.py      # 密码强度检测
├── passwords.db     # SQLite 数据库（运行时生成）
└── README.md        # 项目说明文档
```

---

## 环境配置

### 方式一：使用 conda（推荐）

```bash
# 1. 创建虚拟环境
conda create -n pwdenv python=3.9

# 2. 激活环境
conda activate pwdenv

# 3. 安装依赖
pip install easygui pyperclip
```

### 方式二：使用系统 Python

```bash
# 1. 检查 Python 版本
python --version  # 需要 Python 3.6+

# 2. 安装依赖
pip install easygui pyperclip
```

> **注意**：本项目仅使用 Python 标准库（sqlite3、secrets、re、math），easygui 为图形界面库，pyperclip 用于剪贴板复制。

---

## 快速开始

### 运行程序

```bash
# 激活 conda 环境（如果使用 conda）
conda activate pwdenv

# 运行程序
python main.py
```

### 界面说明

程序启动后会显示主菜单：

```
┌─────────────────────────────┐
│   🔐 简易密码管理器          │
├─────────────────────────────┤
│   [生成密码]                 │
│   [查看密码列表]             │
│   [删除密码]                 │
│   [退出]                     │
└─────────────────────────────┘
```

### 操作流程

**1. 生成密码**
- 输入密码长度（4-64 位）
- 选择字符类型（大写/小写/数字/符号）
- 查看生成的密码和强度
- 输入服务名称和用户名保存

**2. 输入密码**
- 输入服务名称、用户名、密码
- 自动检测密码强度并保存

**3. 修改密码**
- 选择已有凭据
- 选择生成模式（手动/随机/纯数字/纯字母/数字+字母）
- 确认后保存新密码，旧密码保留为历史记录

**4. 查看密码列表**
- 显示当前密码及历史修改记录
- 可选择复制密码到剪贴板

**5. 删除密码**
- 选择凭据后确认删除，级联删除所有关联密码记录

---

## 代码详解

### database.py - 数据库操作模块

| 函数 | 功能 | 说明 |
|------|------|------|
| `init_db()` | 初始化数据库 | 创建 `credentials` 和 `password_analysis` 表 |
| `add_credential(name, username)` | 创建凭据 | 插入新凭据，返回凭据 ID |
| `add_password_analysis(...)` | 保存密码分析 | 插入密码及特征分析记录 |
| `get_all_credentials()` | 获取所有凭据 | 联表查询最新密码，按创建时间倒序 |
| `get_password_history(cred_id)` | 获取密码历史 | 查询指定凭据的所有密码修改记录 |
| `delete_credential(cred_id)` | 删除凭据 | 根据 ID 删除凭据及所有关联密码记录 |

**关键技术点：**
- 使用 `sqlite3` 标准库，无需额外安装
- 参数化查询 (`?` 占位符) 防止 SQL 注入
- 外键约束 + 级联删除，1 对多关系
- 自动创建数据库文件（首次运行时）

---

### password_gen.py - 密码生成模块

| 函数 | 功能 | 说明 |
|------|------|------|
| `generate_password(...)` | 生成随机密码 | 根据配置的长度和字符集生成加密安全的密码 |

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `length` | 16 | 密码长度 |
| `use_upper` | True | 包含大写字母 (A-Z) |
| `use_lower` | True | 包含小写字母 (a-z) |
| `use_nums` | True | 包含数字 (0-9) |
| `use_syms` | False | 包含特殊符号 (!@#$...) |

**关键技术点：**
- 使用 `secrets` 模块（而非 `random`），提供加密安全的随机数生成
- 字符池动态构建，根据用户选择组合字符类型
- 边界保护：如果用户全不选，默认使用小写字母

---

### strength.py - 密码强度检测模块

| 函数 | 功能 | 说明 |
|------|------|------|
| `check_strength(password)` | 检测密码强度 | 返回分数、等级、熵值 |

**评分规则（满分 100）：**

| 条件 | 得分 |
|------|------|
| 长度 ≥ 8 | +10 分 |
| 长度 ≥ 12 | +20 分（额外） |
| 含大写字母 | +15 分 |
| 含小写字母 | +5 分 |
| 含数字 | +15 分 |
| 含特殊符号 | +10 分 |
| 熵值 > 60 bits | +25 分 |

**熵值计算：**
```
熵值 = 密码长度 × log₂(字符池大小)
```

字符池大小根据包含的字符类型计算：
- 小写字母：26 个字符
- 大写字母：26 个字符
- 数字：10 个字符
- 符号：32 个字符

**等级划分：**

| 分数 | 等级 |
|------|------|
| ≥ 80 | 强 |
| 60-79 | 中 |
| < 60 | 弱 |

---

### main.py - 主程序入口（easygui 图形界面）

**主要函数说明：**

| 函数 | 功能 |
|------|------|
| `init()` | 初始化数据库连接 |
| `input_password()` | 手动输入密码并保存 |
| `generate_password()` | 随机生成密码并保存 |
| `change_password()` | 修改密码，支持5种生成模式 |
| `list_passwords()` | 显示密码列表及历史记录，支持复制 |
| `delete_password()` | 删除凭据及所有关联密码记录 |
| `main()` | 主循环，显示主菜单 |

**easygui 组件使用：**

| 组件 | 用途 |
|------|------|
| `eg.integerbox()` | 密码长度数字输入（4-64） |
| `eg.multchoicebox()` | 字符类型多选（大写/小写/数字/符号） |
| `eg.msgbox()` | 显示密码结果和提示信息 |
| `eg.multenterbox()` | 输入服务名称和用户名 |
| `eg.choicebox()` | 密码列表选择查看 |
| `eg.ccbox()` | 确认对话框（保存/复制/删除） |

---

## 数据库设计

### E-R 图（实体-关系图）

```
┌─────────────────────┐         ┌─────────────────────────┐
│     credentials     │         │    password_analysis    │
├─────────────────────┤         ├─────────────────────────┤
│ PK id               │───┐     │ PK id                   │
│    name             │   │     │ FK credential_id        │
│    username         │   ├────>│    password             │
│    created_at       │ 1   n   │    length               │
└─────────────────────┘         │    has_uppercase        │
                                │    has_lowercase        │
                                │    has_numbers          │
                                │    has_symbols          │
                                │    strength_score       │
                                │    created_at           │
                                └─────────────────────────┘

关系说明：
- credentials (1) ──── (n) password_analysis
- 一条凭据可对应多条密码记录（密码修改历史）
- 删除凭据时，关联的所有密码记录级联删除
```

### 逻辑模型

**实体：credentials（凭据）**

| 属性 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| name | TEXT | NOT NULL | 服务名称（如 "Google"） |
| username | TEXT | - | 用户名（可选） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**实体：password_analysis（密码分析）**

| 属性 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| credential_id | INTEGER | FK → credentials.id | 关联凭据 |
| password | TEXT | NOT NULL | 密码 |
| length | INTEGER | - | 密码长度 |
| has_uppercase | INTEGER | - | 是否含大写字母（0/1） |
| has_lowercase | INTEGER | - | 是否含小写字母（0/1） |
| has_numbers | INTEGER | - | 是否含数字（0/1） |
| has_symbols | INTEGER | - | 是否含符号（0/1） |
| strength_score | INTEGER | - | 强度评分（0-100） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**关系：credentials (1) → (n) password_analysis**
- 一条凭据可对应多条密码记录，支持密码修改历史

### 物理模型（SQLite 实现）

**credentials 表**

```sql
CREATE TABLE credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**password_analysis 表**

```sql
CREATE TABLE password_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credential_id INTEGER NOT NULL,
    password TEXT NOT NULL,
    length INTEGER,
    has_uppercase INTEGER,
    has_lowercase INTEGER,
    has_numbers INTEGER,
    has_symbols INTEGER,
    strength_score INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE CASCADE
);
```

**外键约束**

```sql
PRAGMA foreign_keys = ON;  -- 启用外键支持
```

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 编程语言 | Python 3.6+ | 标准库支持 |
| 虚拟环境 | conda | 可选，推荐管理依赖 |
| 图形界面 | easygui | 弹窗式 GUI 库 |
| 数据库 | SQLite3 | Python 标准库内置 |
| 加密随机数 | `secrets` | Python 3.6+ 标准库 |
| 正则表达式 | `re` | 标准库，用于强度检测 |
| 数学计算 | `math` | 标准库，熵值计算 |
| 剪贴板 | `pyperclip` | 用于复制密码到剪贴板 |

---

