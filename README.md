# epub-extractor

## 主要功能
- 根据epub文件为markdown文件
- 图片单独文件存储
- 生成dify用的DSL模版
- 根据excel文件生成图书元数据

## 目录映射
- /app/src 原始文件存放目录，根据产品编号/ISBN分目录存放
- /app/books 处理后的文件
  - /app/books/images/ 按产品编号/ISBN分目录存放图片
  - /app/books/md/ 按产品编号/ISBN分目录存放markdown文件
  - /app/books/meta/ 按产品编号/ISBN目录存放元数据的markdown文件

## 接口
post /process {product_code, file_type}

