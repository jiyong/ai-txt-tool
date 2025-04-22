#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EPUB内容提取器和Excel元数据提取器Web接口
提供RESTful API接口，用于处理EPUB文件的转换请求和Excel元数据的提取请求
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import excel_to_meta
import uvicorn
from pathlib import Path
import logging

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

class ConversionRequest(BaseModel):
    product_code: str
    src_base: str = "/books/src"
    output_base: str = "/books/output"

class MetadataRequest(BaseModel):
    product_code: str
    src_base: Optional[str] = "/Users/qu/books/src"
    output_base: Optional[str] = "/Users/qu/books/output"

@app.post("/convert")
async def convert_epub(request: ConversionRequest):
    """
    转换指定产品编号的EPUB文件
    
    Args:
        request: 包含产品编号和可选的源目录、输出目录的请求对象
        
    Returns:
        转换结果
    """
    try:
        # 构建命令
        cmd = [
            "python3",
            "epub_extractor.py",
            "--src", request.src_base,
            "--output", request.output_base,
            "--product_code", request.product_code
        ]
        
        logger.info(f"开始处理产品: {request.product_code}")
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 检查源目录是否存在
        src_dir = os.path.join(request.src_base, request.product_code)
        if not os.path.exists(src_dir):
            raise HTTPException(
                status_code=404,
                detail=f"源目录不存在: {src_dir}"
            )
        
        # 执行转换命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # 检查输出目录
        output_dir = os.path.join(request.output_base, request.product_code)
        epub_dir = os.path.join(output_dir, "epub")
        images_dir = os.path.join(output_dir, "images")
        
        # 检查输出文件
        if not (os.path.exists(epub_dir) and os.path.exists(images_dir)):
            raise HTTPException(
                status_code=500,
                detail="转换过程完成，但未生成预期的输出文件"
            )
            
        return {
            "status": "success",
            "product_code": request.product_code,
            "message": "转换成功",
            "output_dir": output_dir,
            "details": {
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"转换失败: {e.stderr}")
        raise HTTPException(
            status_code=500,
            detail=f"转换过程失败: {e.stderr}"
        )
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时出错: {str(e)}"
        )

@app.post("/process_metadata")
async def process_metadata(request: MetadataRequest):
    """
    处理指定产品的Excel元数据
    
    参数:
    - product_code: 产品编号
    - src_base: 源目录根路径（可选）
    - output_base: 输出目录根路径（可选）
    
    返回:
    - 处理结果信息
    """
    try:
        # 调用excel_to_meta.py中的处理函数
        excel_to_meta.process_excel_file(
            src_path=request.src_base,
            output_path=request.output_base,
            product_code=request.product_code
        )
        
        # 构建输出文件路径
        output_file = Path(request.output_base) / request.product_code / "meta" / f"{request.product_code}.meta.xlsx"
        
        return {
            "status": "success",
            "message": "元数据处理成功",
            "product_code": request.product_code,
            "output_file": str(output_file)
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 