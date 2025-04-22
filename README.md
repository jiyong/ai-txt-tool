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

