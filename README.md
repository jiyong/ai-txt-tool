# 图书EPUB内容提取和处理程序

这是一个完整的EPUB处理系统，提供了文件转换、元数据提取、结构分析等功能，并支持文件存储和任务管理。
定制化比较强

## 项目结构

- `app.py`: FastAPI应用主文件，提供RESTful API接口
- `epub_to_md.py`: EPUB文件转换工具
- `excel_to_meta.py`: Excel元数据提取工具
- `md_to_json_structure.py`: Markdown结构提取工具
- `text_keywords.py`: 文本关键词提取工具
- `oss_uploader.py`: 阿里云OSS上传工具
- `task_manager.py`: 任务管理系统
- `start.sh`: 容器启动脚本
- `Dockerfile`: Docker镜像构建文件
- `requirements.txt`: Python依赖列表

## 主要功能

- EPUB文件转换为Markdown
- Excel元数据提取
- Markdown结构提取
- 文本关键词提取
- 文件上传到OSS
- 任务状态管理

## 环境变量配置

需要配置以下环境变量：

### Docker配置
- `CONTAINER_NAME`: 容器名称
- `IMAGE_NAME`: 镜像名称
- `HOST_PORT`: 主机端口
- `API_KEY`: API密钥

### 数据目录配置
- `DATA_DIR`: 数据目录路径

### 阿里云OSS配置
- `ALIYUN_OSS_ACCESS_KEY`: 访问密钥
- `ALIYUN_OSS_SECRET_KEY`: 密钥
- `ALIYUN_OSS_ENDPOINT`: OSS端点
- `ALIYUN_OSS_REGION`: 区域
- `ALIYUN_OSS_BUCKET_NAME`: 存储桶名称
- `ALIYUN_OSS_AUTH_VERSION`: 认证版本
- `ALIYUN_OSS_PATH`: OSS路径

### Redis配置
- `REDIS_HOST`: Redis主机
- `REDIS_PORT`: Redis端口
- `REDIS_DB`: Redis数据库
- `REDIS_PASSWORD`: Redis密码

## API接口

### EPUB转换
```bash
# 转换EPUB文件
curl -X POST http://localhost:${HOST_PORT}/epub-to-md \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "product_code": "100227-01",
    "src": "/app/data/100227-01/100227-01工程材料及检测-数字教材.epub",
    "md_img_dir": "/books/100227-01/images",
    "save": true
  }'

# 上传EPUB文件
curl -X POST http://localhost:${HOST_PORT}/epub-to-md/file \
  -H "Authorization: Bearer ${API_KEY}" \
  -F "file=@/path/to/book.epub" \
  -F "product_code=100227-01" \
  -F "save=true"
```

### Markdown结构提取
```bash
curl -X POST http://localhost:${HOST_PORT}/md-to-structure \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "product_code": "100227-01",
    "src": "/app/data/100227-01/epub/100227-01.epub.md",
    "save": true
  }'
```

### 关键词提取
```bash
curl -X POST http://localhost:${HOST_PORT}/extract-keywords \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "text": "这是一段需要提取关键词的文本内容",
    "topk": 10
  }'
```

## 依赖管理

- Python 3.12
- FastAPI, uvicorn
- beautifulsoup4, html2text
- requests, python-multipart
- pydantic, openpyxl, pandas
- jieba, oss2, redis

## 部署要求

- Docker环境
- Redis服务
- 阿里云OSS账号
- 必要的环境变量配置

## 快速开始

1. 复制环境变量配置文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置必要的环境变量

3. 启动服务：
```bash
./start.sh
```

4. 访问API文档：
```
http://localhost:${HOST_PORT}/docs
```

## 目录结构

```
/books
  /src
    /100227-01
      - book1.epub
      - book2.epub
  /output
    /100227-01
      /markdown
        - book1.md
        - book2.md
      /images
        - img1.jpg
        - img2.png
```

## 命令行使用

### 基本用法

```bash
python epub_to_md.py --src <EPUB文件路径或URL> --product_code <产品编号> --md_img_dir <图片引用路径> [--save]
```

### 参数说明

- `--src`: EPUB文件路径或URL
- `--file`: 上传的EPUB文件
- `--product_code`: 产品编号（必需），例如：'100227-01'
- `--md_img_dir`: Markdown文件中图片引用的基础路径
- `--save`: 是否保存文件（默认为false）

### 示例

```bash
# 使用完整路径，保存文件
python epub_to_md.py --src /books/src/100227-01/book1.epub --product_code 100227-01 --md_img_dir /books/100227-01/images --save

# 使用URL，不保存文件
python epub_to_md.py --src https://example.com/book.epub --product_code 100227-01 --md_img_dir /books/100227-01/images

# 不保存文件，直接返回Markdown内容
python epub_to_md.py --src /books/src/100227-01/book1.epub --product_code 100227-01 --md_img_dir /books/100227-01/images
```

## Web API 使用

### 启动服务

```bash
python app.py
```

服务将在 `http://localhost:8000` 启动。

### API 端点

#### 转换EPUB文件

**POST** `/epub-to-md`

请求体：
```json
{
    "product_code": "100227-01",
    "src": "/path/to/book.epub",
    "md_img_dir": "/books/100227-01/images",
    "save": true
}
```

响应示例：
```json
{
    "status": "success",
    "product_code": "100227-01",
    "message": "转换成功",
    "content": "# 书籍标题\n\n**作者：作者名**\n\n...",
    "output_file": "./data/100227-01/epub/100227-01.epub.md",
    "img_dir": "./data/100227-01/images/",
    "md_img_dir": "/books/100227-01/images"
}
```

#### 转换EPUB文件（文件上传）

**POST** `/epub-to-md/file`

请求体（表单数据）：
- `file`: EPUB文件
- `product_code`: 产品编号
- `md_img_dir`: Markdown图片引用路径（可选）
- `save`: 是否保存到文件（默认为false）

响应示例：
```json
{
    "status": "success",
    "product_code": "100227-01",
    "message": "转换成功",
    "content": "# 书籍标题\n\n**作者：作者名**\n\n...",
    "output_file": "./data/100227-01/epub/100227-01.epub.md",
    "img_dir": "./data/100227-01/images/",
    "md_img_dir": "/books/100227-01/images"
}
```

### 使用curl测试API

```bash
# 使用文件路径
curl -X POST "http://localhost:8000/epub-to-md" \
     -H "Content-Type: application/json" \
     -d '{
         "product_code": "100227-01",
         "src": "/path/to/book.epub",
         "save": true
     }'

# 使用文件上传
curl -X POST "http://localhost:8000/epub-to-md/file" \
     -F "file=@/path/to/book.epub" \
     -F "product_code=100227-01" \
     -F "save=true"
```

## 注意事项

1. 确保源目录中包含要处理的EPUB文件
2. 程序会自动创建必要的输出目录结构
3. 当`save`为`true`时，输出的Markdown文件将保存在 `./data/${product_code}/epub/${product_code}.epub.md`
4. 当`save`为`true`时，提取的图片将保存在 `./data/${product_code}/images/`
5. 图片在Markdown中的引用路径格式为 `/books/${product_code}/images/图片名称`
6. 无论是否设置`save`参数，程序都会返回转换后的Markdown内容
7. 当`save`为`true`时，响应中会额外包含文件路径信息

## 依赖项

- Python 3.6+
- FastAPI
- uvicorn
- beautifulsoup4
- html2text
- requests

## 安装依赖

```bash
pip install -r requirements.txt
```

# Excel元数据提取功能

除了EPUB内容提取功能外，本工具还提供了Excel元数据提取和清理功能。

## Excel元数据提取功能特点

- 支持多种Excel格式：
  - 简单格式（2行数据）：第一行是属性，第二行是值
  - 带标题的简单格式（3行数据）：第一行是标题，第二行是属性，第三行是值
  - 新格式（4行数据）：第1行是属性，第4行是值
  - 旧格式（4行数据）：第3行是属性，第4行是值
  - 带示例的新格式（5行数据）：第1行是属性，第2行是示例，第3行是提示，第4行是空行，第5行是值

- 自动清理属性名：
  - 移除括号及其内容
  - 移除括号后的说明文字
  - 处理半个括号的情况
  - 移除"另附"等额外说明
  - 处理带冒号的说明文字

- 保留值的原始内容：
  - 不处理值的内容
  - 保持长文本的完整性
  - 只进行基本的空值处理

## Excel元数据提取使用方法

### 命令行方式

```bash
python excel_to_meta.py --src <源目录> --output <输出目录> --product_code <产品编号>
```

参数说明：
- `--src`：源Excel文件所在的基础目录
- `--output`：输出目录
- `--product_code`：图书产品编号

示例：
```bash
python excel_to_meta.py --src /Users/qu/books/src --output /Users/qu/books/output --product_code 109707-01
```

### API接口方式

通过 `app.py` 提供的API接口调用：

```python
from app import process_metadata

# 处理单个产品的元数据
result = process_metadata(
    src_path="/Users/qu/books/src",
    output_path="/Users/qu/books/output",
    product_code="109707-01"
)
```

## Excel元数据提取输出结果

程序会在指定的输出目录下创建对应的元数据文件：
- 输出路径：`<output_path>/<product_code>/meta/<product_code>.meta.xlsx`
- 文件格式：Excel文件，包含清理后的属性名和原始值

## Excel元数据提取注意事项

1. 确保源目录中存在对应的Excel文件
2. 确保有足够的权限访问源目录和输出目录
3. 输出目录会自动创建（如果不存在）
4. 如果输出文件已存在，会被覆盖

## 依赖项

- Python 3.6+
- FastAPI
- uvicorn
- beautifulsoup4
- html2text

## 安装依赖

```bash
pip install -r requirements.txt
```

# EPUB 内容提取器和 Excel 元数据提取器

这是一个基于 FastAPI 的 Web 服务，提供 EPUB 文件转换和 Excel 元数据提取功能。

## 功能特点

1. EPUB 转 Markdown
   - 将 EPUB 文件转换为 Markdown 格式
   - 支持图片提取和引用路径配置
   - 保持文档结构和格式
   - 支持多种输入方式：本地文件、网络URL、文件上传

2. Markdown 结构提取
   - 从 Markdown 文件中提取层级结构
   - 将 Markdown 转换为树状 JSON 数据
   - 每个节点包含 title/content/children/level 属性
   - 支持多种输入方式：文件路径、文本内容、上传文件

3. Excel 元数据提取
   - 从 Excel 文件中提取元数据信息
   - 支持自定义输入输出路径

## Docker部署

### 1. 环境配置

1. 复制环境变量配置文件：
```bash
cp .env.example .env
```

2. 修改`.env`文件中的配置：
```bash
# Docker容器配置
CONTAINER_NAME=book-processor    # 容器名称
IMAGE_NAME=book-processor       # 镜像名称
API_KEY=epub_extractor_key_2024 # API密钥
HOST_PORT=8000                 # 主机端口

# 目录配置
BOOKS_SRC_DIR=/path/to/books/src    # 源文件目录
BOOKS_OUTPUT_DIR=/path/to/books/output  # 输出目录
BOOKS_DATA_DIR=/path/to/books/data   # 数据目录
```

### 2. 目录结构

```
/books
  /src          # 源文件目录
    /100227-01
      - book1.epub
      - book2.epub
  /output       # 输出目录
    /100227-01
      /markdown
        - book1.md
        - book2.md
      /images
        - img1.jpg
        - img2.png
  /data         # 数据目录
    /100227-01
      /epub
        - 100227-01.epub.md
      /images
        - image1.jpg
        - image2.png
      /structure
        - 100227-01.structure.json
```

### 3. 启动服务

1. 确保Docker已安装并运行
2. 确保目录结构正确
3. 运行启动脚本：
```bash
./start.sh
```

### 4. 验证服务

1. 检查容器状态：
```bash
docker ps
```

2. 查看容器日志：
```bash
docker logs book-processor
```

3. 测试健康检查接口：
```bash
curl -X GET http://localhost:8000/health
```

### 5. 停止服务

```bash
docker stop book-processor
docker rm book-processor
```

## API 接口

### 1. EPUB 转 Markdown（旧方法）

```http
POST /epub-to-md
```

请求体：
```json
{
    "product_code": "产品编号",
    "src_file": "源文件路径",
    "output_file": "输出文件路径",
    "img_dir": "图片存储路径",
    "md_img_dir": "Markdown图片引用路径"
}
```

### 2. EPUB 转 Markdown（新方法）

```http
POST /epub-to-md-new
```

请求体：
```json
{
    "product_code": "产品编号",
    "src": "源EPUB文件路径或URL",
    "md_img_dir": "Markdown图片引用路径",
    "save": true
}
```

### 3. EPUB 转 Markdown（文件上传）

```http
POST /epub-to-md/file
```

请求体（表单数据）：
- `file`: EPUB文件
- `product_code`: 产品编号
- `md_img_dir`: Markdown图片引用路径（可选）
- `save`: 是否保存到文件（默认为false）

### 4. Markdown 结构提取

```http
POST /md-to-structure
```

请求体：
```json
{
    "product_code": "产品编号",
    "src": "源 Markdown 文件路径",
    "text": "Markdown 文本内容",
    "save": true
}
```

注意：`src` 和 `text` 参数只需提供其中一个，优先级为 `text` > `src`。

响应示例：
```json
{
    "status": "success",
    "message": "层级结构数据提取成功",
    "data": {
        "structure": [
            {
                "title": "标题1",
                "content": "内容1",
                "children": [
                    {
                        "title": "子标题1",
                        "content": "子内容1",
                        "children": [],
                        "level": 2
                    }
                ],
                "level": 1
            }
        ]
    },
    "product_code": "100227-01"
}
```

### 5. Markdown 结构提取（文件上传）

```http
POST /md-to-structure/file
```

请求体（表单数据）：
- `file`: Markdown 文件
- `product_code`: 产品编号
- `save`: 是否保存到文件（布尔值）

### 6. Excel 元数据提取

```http
POST /process_metadata
```

请求体：
```json
{
    "product_code": "产品编号",
    "src_base": "源目录根路径",
    "output_base": "输出目录根路径"
}
```

## 命令行使用

### EPUB 转 Markdown

```bash
python epub_to_md.py --src /path/to/book.epub --product_code 100227-01 --save
```

参数说明：
- `--src`: EPUB文件路径或URL
- `--file`: 上传的EPUB文件
- `--product_code`: 产品编号（必需）
- `--md_img_dir`: Markdown图片引用路径
- `--save`: 是否保存到文件（默认为false）

### Markdown 结构提取

```bash
python md_to_json_structure.py --src /path/to/document.md --product_code 100227-01 --save true
```

参数说明：
- `--src`: 源 Markdown 文件路径
- `--text`: Markdown 文本内容
- `--file`: MultipartFile 文件
- `--product_code`: 产品编号（必需）
- `--save`: 是否保存到文件（默认为 false）

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行服务：
```bash
python app.py
```

服务将在 http://localhost:8000 启动

## 使用示例

1. EPUB 转 Markdown（新方法）：
```bash
curl -X POST "http://localhost:8000/epub-to-md-new" \
     -H "Content-Type: application/json" \
     -d '{
         "product_code": "BOOK001",
         "src": "/path/to/book.epub",
         "save": true
     }'
```

2. EPUB 转 Markdown（文件上传）：
```bash
curl -X POST "http://localhost:8000/epub-to-md/file" \
     -F "file=@/path/to/book.epub" \
     -F "product_code=BOOK001" \
     -F "save=true"
```

3. Markdown 结构提取：
```bash
curl -X POST "http://localhost:8000/md-to-structure" \
     -H "Content-Type: application/json" \
     -d '{
         "product_code": "BOOK001",
         "src": "/path/to/document.md",
         "save": true
     }'
```

4. Markdown 结构提取（文件上传）：
```bash
curl -X POST "http://localhost:8000/md-to-structure/file" \
     -F "file=@/path/to/document.md" \
     -F "product_code=BOOK001" \
     -F "save=true"
```

5. Excel 元数据提取：
```bash
curl -X POST "http://localhost:8000/process_metadata" \
     -H "Content-Type: application/json" \
     -d '{
         "product_code": "BOOK001",
         "src_base": "/path/to/source",
         "output_base": "/path/to/output"
     }'
```

## 注意事项

1. 确保所有路径都是有效的且具有适当的访问权限
2. 图片目录会自动创建（如果不存在）
3. 所有 API 都返回 JSON 格式的响应
4. 错误响应会包含详细的错误信息
5. 当 `save` 设置为 `true` 时：
   - EPUB转换结果将保存到 `./data/${product_code}/epub/${product_code}.epub.md`
   - Markdown结构提取结果将保存到 `./data/${product_code}/json/${product_code}.structure.json`
   - 图片将保存到 `./data/${product_code}/images/`

## 开发说明

- 使用 FastAPI 框架构建
- 支持异步处理
- 包含完整的错误处理
- 提供详细的日志记录

### 健康检查

```bash
# 检查服务状态
curl -X GET http://localhost:8000/health
```

响应示例：
```json
{
    "status": "success",
    "message": "服务正常运行",
    "data": {
        "version": "1.0.0"
    }
}
```

# EPUB内容提取器和Excel元数据提取器

这是一个用于提取EPUB文件内容和Excel元数据的RESTful API服务。

## 功能特点

- EPUB文件转换为Markdown格式
- Markdown文件结构提取
- Excel元数据提取
- 文本关键词提取
- 支持文件上传和URL链接
- 支持保存处理结果到本地文件

## Docker部署

### 1. 环境配置

1. 复制环境变量配置文件：
```bash
cp .env.example .env
```

2. 修改`.env`文件中的配置：
```bash
# Docker容器配置
CONTAINER_NAME=book-processor    # 容器名称
IMAGE_NAME=book-processor       # 镜像名称
API_KEY=epub_extractor_key_2024 # API密钥
HOST_PORT=8000                 # 主机端口

# 目录配置
DATA_DIR=/path/to/data   # 数据目录
```

### 2. 目录结构

```
/books
  /src          # 源文件目录
    /100227-01
      - book1.epub
      - book2.epub
  /output       # 输出目录
    /100227-01
      /markdown
        - book1.md
        - book2.md
      /images
        - img1.jpg
        - img2.png
  /data         # 数据目录
    /100227-01
      /epub
        - 100227-01.epub.md
      /images
        - image1.jpg
        - image2.png
      /structure
        - 100227-01.structure.json
```

### 3. 启动服务

1. 确保Docker已安装并运行
2. 确保目录结构正确
3. 运行启动脚本：
```bash
./start.sh
```

### 4. 验证服务

1. 检查容器状态：
```bash
docker ps
```

2. 查看容器日志：
```bash
docker logs book-processor
```

3. 测试健康检查接口：
```bash
curl -X GET http://localhost:8000/health
```

### 5. 停止服务

```bash
docker stop book-processor
docker rm book-processor
```

## API接口

### 健康检查

```bash
curl -X GET http://localhost:8000/health
```

示例响应：
```json
{
    "status": "success",
    "message": "服务正常运行",
    "data": {
        "version": "1.0.0"
    }
}
```

### EPUB转换

```bash
curl -X POST http://localhost:8000/epub-to-md \
  -H "Authorization: Bearer epub_extractor_key_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "100227-01",
    "src": "/app/src/100227-01/100227-01工程材料及检测-数字教材.epub",
    "md_img_dir": "/app/books/100227-01/images",
    "save": true
  }'
```

### EPUB文件上传

```bash
curl -X POST http://localhost:8000/epub-to-md/file \
  -H "Authorization: Bearer epub_extractor_key_2024" \
  -F "file=@/path/to/your/file.epub" \
  -F "product_code=100227-01" \
  -F "save=true"
```

### Markdown结构提取

```bash
curl -X POST http://localhost:8000/md-to-structure \
  -H "Authorization: Bearer epub_extractor_key_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "100227-01",
    "src": "/app/data/100227-01/epub/100227-01.epub.md",
    "save": true
  }'
```

### Excel元数据提取

```bash
curl -X POST http://localhost:8000/excel-to-meta \
  -H "Authorization: Bearer epub_extractor_key_2024" \
  -F "file=@/path/to/your/file.xlsx" \
  -F "product_code=100227-01"
```

### 关键词提取

```bash
curl -X POST http://localhost:8000/extract-keywords \
  -H "Authorization: Bearer epub_extractor_key_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一段需要提取关键词的文本内容",
    "topk": 10
  }'
```

示例响应：
```json
{
    "status": "success",
    "message": "关键词提取成功",
    "data": {
        "keywords": [
            {"word": "关键词1", "weight": 0.8},
            {"word": "关键词2", "weight": 0.6},
            {"word": "关键词3", "weight": 0.4}
        ]
    }
}
```

## 环境要求

- Python 3.8+
- Docker

## 安装和运行

1. 克隆仓库：
```bash
git clone <repository_url>
cd epub-extractor
```

2. 使用Docker运行：
```bash
./start.sh
```

## 目录结构

```
.
├── app.py                 # FastAPI应用主文件
├── epub_to_md.py         # EPUB转换模块
├── md_to_json_structure.py # Markdown结构提取模块
├── excel_to_meta.py      # Excel元数据提取模块
├── text_keywords.py      # 关键词提取模块
├── oss_uploader.py       # 阿里云OSS上传工具
├── task_manager.py       # 任务管理系统
├── start.sh            # 启动脚本
├── Dockerfile           # Docker构建文件
└── README.md           # 项目文档
```

## 注意事项

1. 所有API请求都需要在Header中包含有效的API密钥：
   ```
   Authorization: Bearer epub_extractor_key_2024
   ```

2. 文件路径在容器内部使用，请确保使用正确的容器内路径：
   - 源文件路径：`/app/src/...`
   - 输出文件路径：`/app/output/...`
   - 数据文件路径：`/app/data/...`

3. 使用`save=true`参数可以将处理结果保存到本地文件。

4. 关键词提取支持自定义返回的关键词数量（topk参数）。

5. 确保目录具有正确的读写权限。

6. 首次运行时，Docker会自动创建必要的目录结构。

