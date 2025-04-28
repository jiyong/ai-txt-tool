#!/bin/bash

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "错误: 未找到.env文件，请先复制.env.example为.env并配置环境变量"
    exit 1
fi

# 检查必要的环境变量
if [ -z "$CONTAINER_NAME" ] || [ -z "$IMAGE_NAME" ] || [ -z "$API_KEY" ] || [ -z "$HOST_PORT" ] || [ -z "$DATA_DIR" ] || \
   [ -z "$ALIYUN_OSS_ACCESS_KEY" ] || [ -z "$ALIYUN_OSS_SECRET_KEY" ] || [ -z "$ALIYUN_OSS_ENDPOINT" ] || \
   [ -z "$ALIYUN_OSS_BUCKET_NAME" ] || [ -z "$REDIS_HOST" ] || [ -z "$REDIS_PASSWORD" ]; then
    echo "错误: 环境变量配置不完整，请检查.env文件"
    exit 1
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker服务"
    exit 1
fi

# 检查目录是否存在
if [ ! -d "$DATA_DIR" ]; then
    echo "创建目录: $DATA_DIR"
    mkdir -p "$DATA_DIR"
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
    -v ${DATA_DIR}:/app/data \
    -e API_KEY=${API_KEY} \
    -e ALIYUN_OSS_ACCESS_KEY=${ALIYUN_OSS_ACCESS_KEY} \
    -e ALIYUN_OSS_SECRET_KEY=${ALIYUN_OSS_SECRET_KEY} \
    -e ALIYUN_OSS_ENDPOINT=${ALIYUN_OSS_ENDPOINT} \
    -e ALIYUN_OSS_REGION=${ALIYUN_OSS_REGION} \
    -e ALIYUN_OSS_BUCKET_NAME=${ALIYUN_OSS_BUCKET_NAME} \
    -e ALIYUN_OSS_AUTH_VERSION=${ALIYUN_OSS_AUTH_VERSION} \
    -e ALIYUN_OSS_PATH=${ALIYUN_OSS_PATH} \
    -e REDIS_HOST=${REDIS_HOST} \
    -e REDIS_PORT=${REDIS_PORT} \
    -e REDIS_DB=${REDIS_DB} \
    -e REDIS_PASSWORD=${REDIS_PASSWORD} \
    ${IMAGE_NAME}

# 检查容器是否成功启动
if [ $? -eq 0 ]; then
    echo "容器启动成功！"
    echo "容器名称: ${CONTAINER_NAME}"
    echo "API地址: http://localhost:${HOST_PORT}"
    echo "API密钥: ${API_KEY}"
    echo "数据目录: ${DATA_DIR}"
    echo "Redis主机: ${REDIS_HOST}:${REDIS_PORT}"
    echo "OSS存储桶: ${ALIYUN_OSS_BUCKET_NAME}"
    echo ""
    echo "使用示例:"
    echo ""
    echo "1. 转换EPUB文件:"
    echo "curl -X POST http://localhost:${HOST_PORT}/epub-to-md \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -H \"Authorization: Bearer ${API_KEY}\" \\"
    echo "  -d '{"
    echo "    \"product_code\": \"100227-01\","
    echo "    \"src\": \"/app/data/100227-01/100227-01工程材料及检测-数字教材.epub\","
    echo "    \"md_img_dir\": \"/books/100227-01/images\","
    echo "    \"save\": true"
    echo "  }'"
    echo ""
    echo "2. 上传EPUB文件:"
    echo "curl -X POST http://localhost:${HOST_PORT}/epub-to-md/file \\"
    echo "  -H \"Authorization: Bearer ${API_KEY}\" \\"
    echo "  -F \"file=@/path/to/book.epub\" \\"
    echo "  -F \"product_code=100227-01\" \\"
    echo "  -F \"save=true\""
    echo ""
    echo "3. 提取Markdown结构:"
    echo "curl -X POST http://localhost:${HOST_PORT}/md-to-structure \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -H \"Authorization: Bearer ${API_KEY}\" \\"
    echo "  -d '{"
    echo "    \"product_code\": \"100227-01\","
    echo "    \"src\": \"/app/data/100227-01/epub/100227-01.epub.md\","
    echo "    \"save\": true"
    echo "  }'"
    echo ""
    echo "4. 提取关键词:"
    echo "curl -X POST http://localhost:${HOST_PORT}/extract-keywords \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -H \"Authorization: Bearer ${API_KEY}\" \\"
    echo "  -d '{"
    echo "    \"text\": \"这是一段需要提取关键词的文本内容\","
    echo "    \"topk\": 10"
    echo "  }'"
else
    echo "容器启动失败，请检查错误信息"
    exit 1
fi 