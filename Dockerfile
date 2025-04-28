# 使用Python 3.12 slim版本作为基础镜像
FROM registry.cn-beijing.aliyuncs.com/wenquan/python:3.12-slim-bookworm
# FROM python:3.12-slim-bookworm

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制Python脚本文件
COPY excel_to_meta.py .
COPY epub_to_md.py .
COPY md_to_json_structure.py .
COPY text_keywords.py .
COPY oss_uploader.py .
COPY task_manager.py .
COPY app.py .

# 创建必要的目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]