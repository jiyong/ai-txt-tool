#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EPUB内容提取器和Excel元数据提取器Web接口
提供RESTful API接口，用于处理EPUB文件的转换请求和Excel元数据的提取请求
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import excel_to_meta
import epub_to_md
import pdf_to_md
import md_to_json_structure
import md_to_json
import text_keywords
from typing import Optional, Dict, Any, Union
import uvicorn
from pathlib import Path
import logging
import tempfile

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EPUB内容提取器和Excel元数据提取器",
    description="提供EPUB文件转换和Excel元数据提取的RESTful API接口",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API密钥验证
async def verify_api_key(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "无效的认证格式",
                "code": "INVALID_AUTH_FORMAT"
            }
        )
    
    api_key = authorization.split(" ")[1]
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "无效的API密钥",
                "code": "INVALID_API_KEY"
            }
        )
    
    return api_key

# 请求模型
class ConversionRequest(BaseModel):
    product_code: str
    src: str
    md_img_dir: Optional[str] = None
    save: Optional[bool] = False

class MarkdownStructureRequest(BaseModel):
    product_code: str
    src: str
    save: Optional[bool] = False

class KeywordsRequest(BaseModel):
    text: str
    topk: Optional[int] = 10

# 文本转JSON请求模型
class TextToJsonRequest(BaseModel):
    text: str

# 统一响应格式
def create_response(
    status: str,
    message: str,
    data: Optional[Union[Dict[str, Any], str]] = None,
    code: Optional[str] = None
) -> Dict[str, Any]:
    response = {
        "status": status,
        "message": message
    }
    if data is not None:
        response["data"] = data
    if code is not None:
        response["code"] = code
    return response

# 健康检查接口
@app.get("/health")
async def health_check():
    return create_response(
        status="success",
        message="服务正常运行",
        data={"version": "1.0.0"}
    )

# EPUB转换接口
@app.post("/epub-to-md")
async def convert_epub(request: ConversionRequest, api_key: str = Depends(verify_api_key)):
    try:
        result = epub_to_md.extract_content_from_epub(
            request.src,
            request.product_code,
            request.md_img_dir,
            request.save
        )
        return create_response(
            status="success",
            message="EPUB转换成功",
            data={
                "product_code": request.product_code,
                "content": result,
                "output_file": f"./data/{request.product_code}/epub/{request.product_code}.epub.md" if request.save else None,
                "img_dir": f"./data/{request.product_code}/images/" if request.save else None
            }
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=create_response(
                status="error",
                message=f"文件不存在: {str(e)}",
                code="FILE_NOT_FOUND"
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_response(
                status="error",
                message=f"处理请求时出错: {str(e)}",
                code="INTERNAL_SERVER_ERROR"
            )
        )

# EPUB文件上传接口
@app.post("/epub-to-md/file")
async def convert_epub_file(
    file: UploadFile = File(...),
    product_code: str = Form(...),
    save: bool = Form(False),
    api_key: str = Depends(verify_api_key)
):
    try:
        # 保存上传的文件
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 处理文件
        result = epub_to_md.extract_content_from_epub(
            temp_file_path,
            product_code,
            None,
            save
        )
        
        # 删除临时文件
        os.remove(temp_file_path)
        
        return create_response(
            status="success",
            message="EPUB转换成功",
            data={
                "product_code": product_code,
                "content": result,
                "output_file": f"./data/{product_code}/epub/{product_code}.epub.md" if save else None,
                "img_dir": f"./data/{product_code}/images/" if save else None
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_response(
                status="error",
                message=f"处理请求时出错: {str(e)}",
                code="INTERNAL_SERVER_ERROR"
            )
        )

# Markdown结构提取接口
@app.post("/md-to-structure")
async def extract_structure(request: MarkdownStructureRequest, api_key: str = Depends(verify_api_key)):
    try:
        result = md_to_json_structure.extract_markdown_structure(
            request.src,
            request.product_code,
            request.save
        )
        return create_response(
            status="success",
            message="Markdown结构提取成功",
            data={
                "product_code": request.product_code,
                "content": result,
                "output_file": f"./data/{request.product_code}/structure/{request.product_code}.structure.json" if request.save else None
            }
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=create_response(
                status="error",
                message=f"文件不存在: {str(e)}",
                code="FILE_NOT_FOUND"
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_response(
                status="error",
                message=f"处理请求时出错: {str(e)}",
                code="INTERNAL_SERVER_ERROR"
            )
        )

# Excel元数据提取接口
@app.post("/excel-to-meta")
async def extract_metadata(
    file: UploadFile = File(...),
    product_code: str = Form(...),
    api_key: str = Depends(verify_api_key)
):
    try:
        # 保存上传的文件
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 处理文件
        result = excel_to_meta.extract_metadata_from_excel(temp_file_path, product_code)
        
        # 删除临时文件
        os.remove(temp_file_path)
        
        return create_response(
            status="success",
            message="Excel元数据提取成功",
            data={
                "product_code": product_code,
                "content": result,
                "output_file": f"./data/{product_code}/meta/{product_code}.meta.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_response(
                status="error",
                message=f"处理请求时出错: {str(e)}",
                code="INTERNAL_SERVER_ERROR"
            )
        )

# 关键词提取接口
@app.post("/extract-keywords", status_code=200)
async def extract_keywords(request: KeywordsRequest, api_key: str = Depends(verify_api_key)):
    """
    从文本中提取关键词
    
    Args:
        request: 包含文本内容和关键词数量的请求对象
        api_key: API密钥
        
    Returns:
        包含关键词列表的响应对象
    """
    try:
        # 提取关键词
        keywords = text_keywords.extract_keywords(request.text, request.topk)
        
        return {
            "status": "success",
            "message": "关键词提取成功",
            "data": {
                "keywords": [
                    {
                        "word": word,
                        "weight": round(weight, 4)  # 保留4位小数
                    } for word, weight in keywords
                ],
                "total": len(keywords),
                "topk": request.topk
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"处理文本时出错: {str(e)}",
                "code": "PROCESSING_ERROR"
            }
        )

# PDF转换接口
@app.post("/pdf-to-md")
async def convert_pdf(request: ConversionRequest, api_key: str = Depends(verify_api_key)):
    try:
        result = pdf_to_md.extract_content_from_pdf(
            request.src,
            request.product_code,
            request.md_img_dir,
            request.save
        )
        return create_response(
            status="success",
            message="PDF转换成功",
            data={
                "product_code": request.product_code,
                "content": result,
                "output_file": f"./data/{request.product_code}/pdf/{request.product_code}.pdf.md" if request.save else None,
                "img_dir": f"./data/{request.product_code}/images/" if request.save else None
            }
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=create_response(
                status="error",
                message=f"文件不存在: {str(e)}",
                code="FILE_NOT_FOUND"
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_response(
                status="error",
                message=f"处理请求时出错: {str(e)}",
                code="INTERNAL_SERVER_ERROR"
            )
        )

# PDF文件上传接口
@app.post("/pdf-to-md/file")
async def convert_pdf_file(
    file: UploadFile = File(...),
    product_code: str = Form(...),
    save: bool = Form(False),
    api_key: str = Depends(verify_api_key)
):
    try:
        # 保存上传的文件
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 处理文件
        result = pdf_to_md.extract_content_from_pdf(
            temp_file_path,
            product_code,
            None,
            save
        )
        
        # 删除临时文件
        os.remove(temp_file_path)
        
        return create_response(
            status="success",
            message="PDF转换成功",
            data={
                "product_code": product_code,
                "content": result,
                "output_file": f"./data/{product_code}/pdf/{product_code}.pdf.md" if save else None,
                "img_dir": f"./data/{product_code}/images/" if save else None
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_response(
                status="error",
                message=f"处理请求时出错: {str(e)}",
                code="INTERNAL_SERVER_ERROR"
            )
        )

# 文本转JSON接口
@app.post("/text-to-json")
async def convert_text_to_json(request: TextToJsonRequest, api_key: str = Depends(verify_api_key)):
    try:
        result = md_to_json.text_to_json(request.text)
        return create_response(
            status="success",
            message="文本转换成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_response(
                status="error",
                message=f"处理请求时出错: {str(e)}",
                code="INTERNAL_SERVER_ERROR"
            )
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 