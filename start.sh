#!/bin/bash

# 设置变量
CONTAINER_NAME="book-processor"
IMAGE_NAME="book-processor"
API_KEY="your_secret_key_here"  # 请修改为你的实际API密钥
HOST_PORT=8000
BOOKS_SRC_DIR="/Users/qu/books/src"
BOOKS_OUTPUT_DIR="/Users/qu/books/output"  # 请修改为你的实际图书目录路径

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker服务"
    exit 1
fi

# 检查图书目录是否存在
if [ ! -d "$BOOKS_SRC_DIR" ]; then
    echo "错误: 图书目录不存在: $BOOKS_SRC_DIR"
    echo "请修改脚本中的BOOKS_SRC_DIR变量为正确的目录路径"
    exit 1
fi

# 检查是否已经存在同名容器
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "停止并删除已存在的容器..."
    docker stop ${CONTAINER_NAME} > /dev/null 2>&1
    docker rm ${CONTAINER_NAME} > /dev/null 2>&1
fi

# 构建镜像
echo "构建Docker镜像..."
docker build -t ${IMAGE_NAME} .

# 运行容器
echo "启动容器..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${HOST_PORT}:8000 \
    -v ${BOOKS_SRC_DIR}:/app/src \
    -v ${BOOKS_OUTPUT_DIR}:/app/output \
    -e API_KEY=${API_KEY} \
    ${IMAGE_NAME}

# 检查容器是否成功启动
if [ $? -eq 0 ]; then
    echo "容器启动成功！"
    echo "容器名称: ${CONTAINER_NAME}"
    echo "API地址: http://localhost:${HOST_PORT}"
    echo "API密钥: ${API_KEY}"
    echo "图书目录: ${BOOKS_SRC_DIR}"
    echo "图书输出目录: ${BOOKS_OUTPUT_DIR}"
    echo ""
    echo "使用示例:"
    echo "curl -X GET http://localhost:${HOST_PORT}/health \\"
    echo "  -H \"Authorization: Bearer ${API_KEY}\""
else
    echo "容器启动失败，请检查错误信息"
    exit 1
fi 