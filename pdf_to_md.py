#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF内容提取器
此脚本用于提取PDF文件中的内容并转换为Markdown格式
"""

import sys
import os
import argparse
import re
import shutil
import uuid
import tempfile
from pathlib import Path
import logging
import asyncio
import fitz  # PyMuPDF
from PIL import Image
import io

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 本地模式标志
LOCAL_MODE = False

def get_product_id(filename):
    """
    从文件名中提取产品编号
    
    Args:
        filename: 文件名
        
    Returns:
        产品编号
    """
    match = re.match(r'(\d{6}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

async def upload_to_oss(product_code: str, data_dir: str) -> bool:
    """
    异步上传文件到OSS
    
    Args:
        product_code: 产品代码
        data_dir: 数据目录
        
    Returns:
        bool: 上传是否成功
    """
    # 本地模式下不执行上传
    if LOCAL_MODE:
        logger.info("本地模式：跳过OSS上传")
        return True
        
    try:
        # 导入任务管理器和OSS上传器
        from oss_uploader import OSSUploader
        from task_manager import task_manager, TaskStatus
        
        # 更新任务状态为进行中
        await task_manager.update_task_status(product_code, "pdf-to-md", TaskStatus.DOING, "正在上传文件到OSS")
        
        uploader = OSSUploader()
        product_dir = os.path.join(data_dir, product_code)
        
        if not os.path.exists(product_dir):
            logging.error(f"产品目录不存在: {product_dir}")
            await task_manager.update_task_status(product_code, "pdf-to-md", TaskStatus.FAIL, "产品目录不存在")
            return False
            
        # 获取文件锁
        if not await task_manager.acquire_file_lock(product_code):
            logging.info(f"等待其他任务完成: {product_code}")
            # 等待所有相关任务完成
            if not await task_manager.wait_for_tasks_completion(product_code, ["pdf-to-md", "md-to-json-structure"]):
                await task_manager.update_task_status(product_code, "pdf-to-md", TaskStatus.FAIL, "等待任务超时")
                return False
                
        try:
            # 上传整个产品目录
            success = uploader.upload_directory(product_dir)
            
            if success:
                # 上传成功后删除本地文件
                uploader.delete_local_files(product_dir)
                await task_manager.update_task_status(product_code, "pdf-to-md", TaskStatus.SUCCESS, "文件上传成功")
            else:
                await task_manager.update_task_status(product_code, "pdf-to-md", TaskStatus.FAIL, "文件上传失败")
                
            return success
            
        finally:
            # 释放文件锁
            await task_manager.release_file_lock(product_code)
            
    except Exception as e:
        logging.error(f"上传到OSS失败: {str(e)}")
        if not LOCAL_MODE:
            await task_manager.update_task_status(product_code, "pdf-to-md", TaskStatus.FAIL, f"上传失败: {str(e)}")
        return False

def extract_content_from_pdf(pdf_path, product_code, md_img_dir=None, save=False):
    """
    从PDF文件中提取内容并转换为Markdown格式
    
    Args:
        pdf_path: PDF文件的路径
        product_code: 产品编号
        md_img_dir: Markdown文件中图片引用的基础路径
        save: 是否保存文件
    
    Returns:
        提取的Markdown文本内容
    """
    # 转换为Path对象
    pdf_path = Path(pdf_path)
    
    # 设置输出路径和图片目录
    if save:
        output_path = Path(f"./data/{product_code}/pdf/{product_code}.pdf.md")
        image_dir = Path(f"./data/{product_code}/images/")
    else:
        # 如果不保存，则使用临时目录
        temp_dir = Path(tempfile.mkdtemp())
        output_path = temp_dir / f"{product_code}.pdf.md"
        image_dir = temp_dir / "images"
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # 如果没有指定md_img_dir，则使用默认值
    if not md_img_dir:
        md_img_dir = f"/books/{product_code}/images"
    
    print(f"extract_content_from_pdf 输入参数:")
    print(f"  pdf_path: {pdf_path}")
    print(f"  output_path: {output_path}")
    print(f"  image_dir: {image_dir}")
    print(f"  md_img_dir: {md_img_dir}")
    print(f"  product_code: {product_code}")
    
    if not pdf_path.exists():
        print(f"错误: 文件 '{pdf_path}' 不存在")
        return None
    
    try:
        # 打开PDF文件
        doc = fitz.open(pdf_path)
        
        # 提取元数据
        metadata = doc.metadata
        title = metadata.get('title', '')
        author = metadata.get('author', '')
        
        # 开始创建Markdown文件内容
        markdown_content = []
        
        # 添加书籍标题和作者信息
        if title:
            markdown_content.append(f"# {title}\n")
        if author:
            markdown_content.append(f"**作者：{author}**\n")
        
        # 处理每一页
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 提取文本
            text = page.get_text()
            
            # 提取图片
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # 生成唯一的图片文件名
                    image_ext = base_image["ext"]
                    # 确保扩展名前有点号
                    if not image_ext.startswith('.'):
                        image_ext = '.' + image_ext
                    image_name = f"page_{page_num + 1}_img_{img_index + 1}{image_ext}"
                    image_path = image_dir / image_name
                    
                    # 保存图片
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_bytes)
                    
                    # 在文本中插入图片引用
                    md_image_path = f"{md_img_dir}/{image_name}"
                    text += f"\n\n![图片]({md_image_path})\n\n"
                    
                except Exception as e:
                    print(f"处理图片时出错: {str(e)}")
            
            # 添加到Markdown内容
            markdown_content.append(text)
        
        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        
        print(f"内容已成功提取到Markdown文件: {output_path}")
        print(f"图片已保存到目录: {image_dir}")
        print(f"Markdown中的图片引用路径: {md_img_dir}")
        
        # 读取生成的Markdown内容
        with open(output_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        
        # 如果不保存，则删除临时文件
        if not save:
            shutil.rmtree(temp_dir)
        
        # 在保存文件后，启动异步上传任务
        if save and not LOCAL_MODE:
            asyncio.create_task(upload_to_oss(product_code, os.path.join(os.getcwd(), "data")))
        
        return markdown_text
        
    except Exception as e:
        print(f"提取过程中出错: {str(e)}")
        return None

def process_pdf_file(file_content, product_code, md_img_dir=None, save=False):
    """
    处理上传的PDF文件内容
    
    Args:
        file_content: 上传的PDF文件内容
        product_code: 产品编号
        md_img_dir: Markdown文件中图片引用的基础路径
        save: 是否保存文件
    
    Returns:
        提取的内容写入Markdown文件，图片保存到指定目录，并返回输出文件的路径
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    
    try:
        # 处理PDF文件
        result = extract_content_from_pdf(temp_file_path, product_code, md_img_dir, save)
        return result
    finally:
        # 删除临时文件
        os.unlink(temp_file_path)

def process_pdf_url(url, product_code, md_img_dir=None, save=False):
    """
    处理网络上的PDF文件
    
    Args:
        url: PDF文件的URL
        product_code: 产品编号
        md_img_dir: Markdown文件中图片引用的基础路径
        save: 是否保存文件
    
    Returns:
        提取的内容写入Markdown文件，图片保存到指定目录，并返回输出文件的路径
    """
    try:
        # 导入requests
        import requests
        
        # 下载PDF文件
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # 处理PDF文件
            result = extract_content_from_pdf(temp_file_path, product_code, md_img_dir, save)
            return result
        finally:
            # 删除临时文件
            os.unlink(temp_file_path)
    except Exception as e:
        print(f"下载或处理URL时出错: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='提取PDF文件中的内容并转换为Markdown格式')
    parser.add_argument('--src', help='输入的PDF文件路径或URL')
    parser.add_argument('--file', help='上传的PDF文件')
    parser.add_argument('--product_code', required=True, help='产品编号（例如：100227-01）')
    parser.add_argument('--md_img_dir', help='Markdown文件中图片引用的基础路径')
    parser.add_argument('--save', action='store_true', help='是否保存文件')
    parser.add_argument('--local', action='store_true', help='本地模式，禁用任务管理器和OSS上传')
    
    args = parser.parse_args()
    
    # 设置本地模式
    global LOCAL_MODE
    LOCAL_MODE = args.local
    
    print(f"处理参数:")
    print(f"  产品编号: {args.product_code}")
    print(f"  输入文件: {args.src}")
    print(f"  上传文件: {args.file}")
    print(f"  Markdown图片引用路径: {args.md_img_dir}")
    print(f"  保存文件: {args.save}")
    print(f"  本地模式: {LOCAL_MODE}")
    
    # 检查输入参数
    if not args.src and not args.file:
        print("错误: 必须提供--src或--file参数")
        sys.exit(1)
    
    # 处理PDF文件
    if args.src:
        # 检查是否为URL
        if args.src.startswith('http://') or args.src.startswith('https://'):
            result = process_pdf_url(args.src, args.product_code, args.md_img_dir, args.save)
        else:
            # 检查输入文件是否存在
            if not os.path.exists(args.src):
                print(f"错误: 输入文件不存在: {args.src}")
                sys.exit(1)
            
            # 处理本地文件
            result = extract_content_from_pdf(args.src, args.product_code, args.md_img_dir, args.save)
    elif args.file:
        # 处理上传的文件
        with open(args.file, 'rb') as f:
            file_content = f.read()
        
        result = process_pdf_file(file_content, args.product_code, args.md_img_dir, args.save)
    
    if result:
        print(f"成功处理文件")
        print("\n提取的Markdown内容:")
        print(result)
    else:
        print(f"处理文件失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 