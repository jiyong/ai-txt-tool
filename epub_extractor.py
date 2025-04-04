#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EPUB内容提取器
此脚本用于提取EPUB电子书中的内容并转换为Markdown格式
"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET
import html2text
from bs4 import BeautifulSoup
import argparse
import re
import shutil
import uuid
from pathlib import Path

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

def process_epub_file(epub_path, output_dir, image_dir):
    """
    处理单个EPUB文件
    
    Args:
        epub_path: EPUB文件路径
        output_dir: 输出目录
        image_dir: 图片目录
        
    Returns:
        是否处理成功
    """
    try:
        print(f"process_epub_file 输入参数:")
        print(f"  epub_path: {epub_path}")
        print(f"  output_dir: {output_dir}")
        print(f"  image_dir: {image_dir}")
        
        # 转换为Path对象
        epub_path = Path(epub_path)
        output_dir = Path(output_dir)
        image_dir = Path(image_dir)
        
        print(f"process_epub_file 转换后的Path对象:")
        print(f"  epub_path: {epub_path}")
        print(f"  output_dir: {output_dir}")
        print(f"  image_dir: {image_dir}")
        
        # 获取文件名（不含扩展名）
        filename = epub_path.stem
        print(f"  filename: {filename}")
        
        # 提取产品编号
        product_id = get_product_id(filename)
        if not product_id:
            print(f"警告: 无法从文件名 {filename} 中提取产品编号")
            return False
            
        # 生成输出文件名（去除产品编号后的空格）
        output_filename = re.sub(r'(\d{6}-\d{2})\s+', r'\1', filename) + '.md'
        output_path = output_dir / output_filename
        
        print(f"process_epub_file 处理结果:")
        print(f"  output_filename: {output_filename}")
        print(f"  output_path: {output_path}")
        
        # 提取内容
        result = extract_content_from_epub(str(epub_path), str(output_path), str(image_dir)) is not None
        print(f"  extract_content_from_epub 结果: {result}")
        return result
        
    except Exception as e:
        print(f"处理文件 {epub_path} 时出错: {str(e)}")
        return False

def process_single_book(product_code):
    """
    处理单个产品编号对应的EPUB文件
    
    Args:
        product_code: 产品编号（如：123456-01）
        
    Returns:
        是否处理成功
    """
    try:
        print(f"当前产品编号: {product_code}")
        # 获取当前工作目录
        current_dir = Path.cwd()
        
        # 构建源目录路径
        src_dir = current_dir / 'src' / product_code
        
        if not src_dir.exists():
            print(f"错误: 目录 {src_dir} 不存在")
            return False
            
        # 构建输出目录路径
        markdown_dir = current_dir / 'output' / 'markdown' / product_code
        
        image_dir = current_dir / 'output' / 'images' / product_code

        # 确保输出目录存在
        markdown_dir.mkdir(parents=True, exist_ok=True)
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # 扫描目录下的EPUB文件
        epub_files = [f for f in src_dir.glob('*.epub')]
        if not epub_files:
            print(f"警告: 在目录 {src_dir} 中没有找到EPUB文件")
            return False
            
        success = True
        for epub_file in epub_files:
            print(f"\n处理文件: {epub_file.name}")
            print(f"完整路径: {epub_file}")
            print(f"目标目录: {markdown_dir}")
            print(f"图片目录: {image_dir}")
            
            if process_epub_file(str(epub_file), str(markdown_dir), str(image_dir)):
                print(f"成功处理: {epub_file.name}")
            else:
                print(f"处理失败: {epub_file.name}")
                success = False
                
        return success
        
    except Exception as e:
        print(f"处理产品 {product_code} 时出错: {str(e)}")
        return False

def process_books(src_dir, output_dir):
    """
    处理src目录下的所有二级目录中的EPUB文件
    
    Args:
        src_dir: 源目录
        output_dir: 输出根目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'markdown'), exist_ok=True)
    
    # 遍历src目录下的所有二级目录
    for root, dirs, files in os.walk(src_dir):
        # 只处理二级目录
        if root == src_dir:
            continue
            
        # 获取二级目录名
        subdir = os.path.basename(root)
        
        # 处理该目录下的所有EPUB文件
        for file in files:
            if file.lower().endswith('.epub'):
                epub_path = os.path.join(root, file)
                
                # 获取产品编号
                product_id = get_product_id(file)
                if not product_id:
                    print(f"警告: 跳过文件 {file}，无法提取产品编号")
                    continue
                
                # 设置输出目录和图片目录
                markdown_dir = os.path.join(output_dir, 'markdown', product_id)
                image_dir = os.path.join(output_dir, 'images', product_id)
                
                print(f"正在处理: {epub_path}")
                if process_epub_file(epub_path, markdown_dir, image_dir):
                    print(f"成功处理: {file}")
                else:
                    print(f"处理失败: {file}")

def generate_dsl_file(template_path, output_path, meta_description, meta_name):
    """
    根据模板生成DSL文件
    
    Args:
        template_path: DSL模板文件路径
        output_path: 输出文件路径
        meta_description: 描述信息
        meta_name: 名称信息
    """
    try:
        # 读取模板文件
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 替换模板变量
        content = template_content.replace('{{meta.description}}', meta_description)
        content = content.replace('{{meta.name}}', meta_name)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"DSL文件已生成: {output_path}")
        return True
        
    except Exception as e:
        print(f"生成DSL文件时出错: {str(e)}")
        return False

def get_first_line_content(markdown_path):
    """
    获取Markdown文件第一行的无格式内容
    
    Args:
        markdown_path: Markdown文件路径
        
    Returns:
        第一行的无格式内容
    """
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            
        # 移除Markdown标记
        content = re.sub(r'^#+\s*', '', first_line)  # 移除标题标记
        content = re.sub(r'[`*_]', '', content)      # 移除其他格式标记
        
        return content if content else None
        
    except Exception as e:
        print(f"读取Markdown文件时出错: {str(e)}")
        return None

def extract_content_from_epub(epub_path, output_path=None, image_dir=None):
    """
    从EPUB文件中提取内容并转换为Markdown格式
    
    Args:
        epub_path: EPUB文件的路径
        output_path: 输出Markdown文件的路径，如果未提供则使用EPUB文件名作为基础
        image_dir: 图片保存目录，如果未提供则使用输出文件名作为基础创建一个目录
    
    Returns:
        提取的内容写入Markdown文件，图片保存到指定目录，并返回输出文件的路径
    """
    # 转换为Path对象
    epub_path = Path(epub_path)
    if output_path:
        output_path = Path(output_path)
    if image_dir:
        image_dir = Path(image_dir)
    
    print(f"extract_content_from_epub 输入参数:")
    print(f"  epub_path: {epub_path}")
    print(f"  output_path: {output_path}")
    print(f"  image_dir: {image_dir}")
    
    if not epub_path.exists():
        print(f"错误: 文件 '{epub_path}' 不存在")
        return None
    
    if not output_path:
        output_path = epub_path.with_suffix(".md")
    
    # 获取产品编号（用于构建图片路径前缀）
    filename = epub_path.name
    product_id = get_product_id(filename)
    if not product_id:
        print(f"警告: 无法从文件名 {filename} 中提取产品编号")
        return None
    
    print(f"extract_content_from_epub 处理结果:")
    print(f"  output_path: {output_path}")
    print(f"  image_dir: {image_dir}")

    # 创建html2text转换器实例
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.ignore_images = False
    h2t.escape_snob = False
    h2t.ignore_tables = False
    h2t.body_width = 0  # 不自动断行
    h2t.unicode_snob = True  # 使用Unicode
    h2t.mark_code = True
    h2t.wrap_links = False
    h2t.wrap_lists = False
    h2t.single_line_break = True  # 单个换行符不被忽略
    
    try:
        # 打开EPUB文件(实际是ZIP文件)
        with zipfile.ZipFile(epub_path, 'r') as epub:
            # 首先查找OPF文件位置
            container = epub.read('META-INF/container.xml')
            container_root = ET.fromstring(container)
            opf_path = container_root.find('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile').get('full-path')
            
            # 读取OPF文件，获取内容文件列表
            opf_content = epub.read(opf_path)
            opf_root = ET.fromstring(opf_content)
            
            # 获取基础路径
            opf_dir = os.path.dirname(opf_path)
            if opf_dir and not opf_dir.endswith('/'):
                opf_dir += '/'
            
            # 提取内容文件列表
            manifest = opf_root.find('.//{http://www.idpf.org/2007/opf}manifest')
            spine = opf_root.find('.//{http://www.idpf.org/2007/opf}spine')
            
            # 获取标题和作者信息
            metadata = opf_root.find('.//{http://www.idpf.org/2007/opf}metadata')
            title = ""
            author = ""
            if metadata is not None:
                title_elem = metadata.find('.//{http://purl.org/dc/elements/1.1/}title')
                if title_elem is not None and title_elem.text:
                    title = title_elem.text
                
                creator_elem = metadata.find('.//{http://purl.org/dc/elements/1.1/}creator')
                if creator_elem is not None and creator_elem.text:
                    author = creator_elem.text
            
            # 获取itemrefs的顺序
            itemrefs = []
            if spine is not None:
                itemrefs = [item.get('idref') for item in spine.findall('.//{http://www.idpf.org/2007/opf}itemref')]
            
            # 收集所有内容项目
            content_items = {}
            image_items = {}
            
            for item in manifest.findall('.//{http://www.idpf.org/2007/opf}item'):
                item_id = item.get('id')
                href = item.get('href')
                media_type = item.get('media-type')
                
                if media_type in ['application/xhtml+xml', 'text/html']:
                    content_items[item_id] = href
                elif media_type.startswith('image/'):
                    image_items[item_id] = href
            
            # 保存所有图片，并创建图片ID到保存路径的映射
            image_map = {}
            
            for image_id, image_href in image_items.items():
                try:
                    # 构建完整的图片路径
                    image_path = os.path.join(opf_dir, image_href)
                    # 提取图片文件扩展名
                    _, ext = os.path.splitext(image_href)
                    # 生成唯一的图片文件名
                    new_image_name = f"{image_id}{ext}"
                    save_path = os.path.join(image_dir, new_image_name)
                    
                    # 读取并保存图片
                    with open(save_path, 'wb') as img_file:
                        img_file.write(epub.read(image_path))
                    
                    # 构建带前缀的图片路径
                    prefixed_path = f"/books/images/{product_id}/{new_image_name}"
                    
                    # 记录图片ID到保存路径的映射
                    image_map[os.path.basename(image_href)] = prefixed_path
                    
                    # 如果href中包含了路径信息，也创建一个映射，因为HTML中的引用可能是相对路径
                    image_map[image_href] = prefixed_path
                except Exception as e:
                    print(f"保存图片 {image_href} 时出错: {str(e)}")
            
            # 开始创建Markdown文件内容
            markdown_content = []
            
            # 添加书籍标题和作者信息
            if title:
                markdown_content.append(f"# {title}\n")
            if author:
                markdown_content.append(f"**作者：{author}**\n")
            
            # 按照spine中的顺序提取内容
            if itemrefs:
                for idref in itemrefs:
                    if idref in content_items:
                        file_path = content_items[idref]
                        convert_html_to_markdown(epub, opf_dir, file_path, markdown_content, image_map, h2t)
            else:
                # 如果没有spine，则直接按顺序提取所有HTML文件
                for _, file_path in content_items.items():
                    convert_html_to_markdown(epub, opf_dir, file_path, markdown_content, image_map, h2t)
            
            # 写入输出文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(markdown_content))
            
            # 生成DSL文件
            template_path = 'template/dsl.template.yml'
            books_dir = os.path.dirname(os.path.dirname(os.path.dirname(output_path)))  # 获取books目录
            dsl_dir = os.path.join(books_dir, 'dsl', product_id)
            dsl_path = os.path.join(dsl_dir, f'{product_id}.dsl.yml')
            
            # 获取meta.name（第一行内容或文件名）
            meta_name = get_first_line_content(output_path)
            if not meta_name:
                # 如果第一行为空，使用文件名（不含扩展名和产品编号）
                base_name = os.path.splitext(os.path.basename(output_path))[0]
                meta_name = re.sub(r'^\d{6}-\d{2}\s*', '', base_name)
            
            # 获取meta.description（markdown文件名）
            meta_description = os.path.splitext(os.path.basename(output_path))[0]
            
            # 生成DSL文件
            generate_dsl_file(template_path, dsl_path, meta_description, meta_name)
            
            print(f"内容已成功提取到Markdown文件: {output_path}")
            print(f"图片已保存到目录: {image_dir}")
            return output_path
            
    except Exception as e:
        print(f"提取过程中出错: {str(e)}")
        return None

def convert_html_to_markdown(epub, opf_dir, file_path, markdown_content, image_map, h2t):
    """将HTML内容转换为Markdown格式"""
    try:
        full_path = os.path.join(opf_dir, file_path)
        file_content = epub.read(full_path)
        
        # 使用Beautiful Soup解析HTML
        soup = BeautifulSoup(file_content, 'html.parser')
        
        # 处理图片路径，将其替换为本地保存的图片路径
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # 尝试在映射中查找图片
                if src in image_map:
                    img['src'] = image_map[src]
                else:
                    # 尝试通过文件名匹配
                    img_name = os.path.basename(src)
                    if img_name in image_map:
                        img['src'] = image_map[img_name]
        
        # 优化标题处理
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            # 确保标题元素前有一个空行
            if i > 0:  # 跳过第一个标题，因为可能是章节标题
                new_tag = soup.new_tag('p')
                new_tag.string = ""
                heading.insert_before(new_tag)
        
        # 转换为Markdown
        html_content = str(soup)
        md_content = h2t.handle(html_content)
        
        # 后处理Markdown内容
        # 1. 修复可能的格式问题
        md_content = re.sub(r'\n{3,}', '\n\n', md_content)  # 删除多余空行
        
        # 2. 优化图片引用格式
        md_content = re.sub(r'!\[\]\(([^)]+)\)', r'![图片](\1)', md_content)
        
        # 3. 确保代码块格式正确
        md_content = re.sub(r'```\s+```', '', md_content)  # 删除空代码块
        
        markdown_content.append(md_content)
        
    except KeyError:
        print(f"无法找到文件: {full_path}")
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='提取EPUB文件中的内容并转换为Markdown格式')
    parser.add_argument('--src', default='src', help='源目录路径，包含EPUB文件的二级目录')
    parser.add_argument('--output', default='output', help='输出根目录路径')
    
    args = parser.parse_args()
    
    # 处理目录
    process_books(args.src, args.output)

if __name__ == "__main__":
    main() 