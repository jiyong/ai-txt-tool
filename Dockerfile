# 使用Python 3.12-slim-bookworm作为基础镜像
FROM registry.cn-beijing.aliyuncs.com/wenquan/python:3.12-slim-bookworm

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序文件
COPY excel_to_meta.py .
COPY epub_extractor.py .
COPY app.py .
COPY template/ ./template/

# 创建src目录用于挂载
RUN mkdir -p /app/src
RUN mkdir -p /app/output

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV API_KEY=your_default_api_key_here

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 