#!/bin/bash

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "错误: 未找到.env文件，请先复制.env.example为.env并配置环境变量"
    exit 1
fi

# 检查必要的环境变量
if [ -z "$CONTAINER_NAME" ] || [ -z "$IMAGE_NAME" ] || [ -z "$API_KEY" ] || [ -z "$HOST_PORT" ] || [ -z "$BOOKS_SRC_DIR" ] || [ -z "$BOOKS_OUTPUT_DIR" ] || [ -z "$BOOKS_DATA_DIR" ]; then
    echo "错误: 环境变量配置不完整，请检查.env文件"
    exit 1
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker服务"
    exit 1
fi

# 检查目录是否存在
for dir in "$BOOKS_SRC_DIR" "$BOOKS_OUTPUT_DIR" "$BOOKS_DATA_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "创建目录: $dir"
        mkdir -p "$dir"
    fi
done

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
    -v ${BOOKS_DATA_DIR}:/app/data \
    -e API_KEY=${API_KEY} \
    ${IMAGE_NAME}

# 检查容器是否成功启动
if [ $? -eq 0 ]; then
    echo "容器启动成功！"
    echo "容器名称: ${CONTAINER_NAME}"
    echo "API地址: http://localhost:${HOST_PORT}"
    echo "API密钥: ${API_KEY}"
    echo "图书源目录: ${BOOKS_SRC_DIR}"
    echo "图书输出目录: ${BOOKS_OUTPUT_DIR}"
    echo "图书数据目录: ${BOOKS_DATA_DIR}"
    echo ""
    echo "使用示例:"
    echo ""
    echo "1. 转换EPUB文件:"
    echo "curl -X POST http://localhost:${HOST_PORT}/epub-to-md \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -H \"Authorization: Bearer ${API_KEY}\" \\"
    echo "  -d '{"
    echo "    \"product_code\": \"100227-01\","
    echo "    \"src\": \"/app/src/100227-01/100227-01工程材料及检测-数字教材.epub\","
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
    echo "    \"src\": \"/app/output/100227-01/epub/100227-01.epub.md\","
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