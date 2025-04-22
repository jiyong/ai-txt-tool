# EPUB内容提取器

这是一个用于提取EPUB电子书内容并转换为Markdown格式的工具。支持命令行使用和Web API接口。

## 功能特点

- 提取EPUB文件中的文本内容并转换为Markdown格式
- 自动提取和保存EPUB中的图片
- 支持命令行操作和Web API接口
- 自动创建输出目录结构
- 支持批量处理

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
python epub_extractor.py --src <源目录> --output <输出目录> --product_code <产品编号>
```

### 参数说明

- `--src`: 源目录根路径，默认为 'src'
- `--output`: 输出目录根路径，默认为 'output'
- `--product_code`: 产品编号（必需），例如：'100227-01'

### 示例

```bash
# 使用完整路径
python epub_extractor.py --src /books/src --output /books/output --product_code 100227-01

# 使用相对路径
python epub_extractor.py --src ./src --output ./output --product_code 100227-01
```

## Web API 使用

### 启动服务

```bash
python app.py
```

服务将在 `http://localhost:8000` 启动。

### API 端点

#### 转换EPUB文件

**POST** `/convert`

请求体：
```json
{
    "product_code": "100227-01",
    "src_base": "/books/src",     // 可选，默认为 "/books/src"
    "output_base": "/books/output" // 可选，默认为 "/books/output"
}
```

响应示例：
```json
{
    "status": "success",
    "product_code": "100227-01",
    "message": "转换成功",
    "output_dir": "/books/output/100227-01",
    "details": {
        "stdout": "处理日志输出...",
        "stderr": ""
    }
}
```

### 使用curl测试API

```bash
curl -X POST http://localhost:8000/convert \
     -H "Content-Type: application/json" \
     -d '{"product_code": "100227-01"}'
```

## 注意事项

1. 确保源目录中包含要处理的EPUB文件
2. 程序会自动创建必要的输出目录结构
3. 输出的Markdown文件将保存在 `output/产品编号/markdown` 目录下
4. 提取的图片将保存在 `output/产品编号/images` 目录下
5. 图片在Markdown中的引用路径格式为 `/books/产品编号/images/图片名称`

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

