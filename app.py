from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import os
from excel_to_meta import process_book_meta
from epub_extractor import process_single_book
from typing import Optional

app = FastAPI(title="图书处理API")

# API Key验证函数
async def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization header")
    
    # 检查Authorization header格式
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header格式错误")
    
    api_key = authorization.split(" ")[1]
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="API Key无效")
    
    return api_key

class ProcessRequest(BaseModel):
    product_code: str
    file_type: str  # "excel" 或 "epub"

@app.post("/process")
async def process_files(
    request: ProcessRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        # 构建完整目录路径
        directory = f"/app/src/{request.product_code}"
        
        if not os.path.exists(directory):
            raise HTTPException(status_code=404, detail=f"目录不存在: {directory}")
        
        if request.file_type == "excel":
            process_book_meta(request.product_code)
        elif request.file_type == "epub":
            process_single_book(request.product_code)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        return {"status": "success", "message": "处理完成", "directory": directory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check(api_key: str = Depends(verify_api_key)):
    return {"status": "healthy"} 