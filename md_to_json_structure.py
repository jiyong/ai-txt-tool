#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown 层级结构提取器
用于从 Markdown 文件中提取层级结构并转换为树状 JSON 数据
每个节点包含 title/content/children/level
"""

import re
import json
import logging
import argparse
import os
from typing import Dict, List, Union, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarkdownStructureExtractor:
    def __init__(self, markdown_content: str):
        """
        初始化 Markdown 结构提取器
        
        Args:
            markdown_content: Markdown 文件内容
        """
        self.content = markdown_content
        self.lines = markdown_content.split('\n')
        self.structure = []
        
    def extract_structure(self) -> List[Dict]:
        """
        从 Markdown 内容中提取层级结构
        
        Returns:
            树状结构数据
        """
        # 初始化根节点
        root = {
            "title": "Root",
            "content": "",
            "children": [],
            "level": 0
        }
        
        # 当前节点栈，用于跟踪层级关系
        node_stack = [root]
        
        # 当前内容缓冲区
        current_content = []
        
        # 标题正则表达式
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        
        for line in self.lines:
            # 检查是否是标题
            heading_match = heading_pattern.match(line)
            
            if heading_match:
                # 如果有未处理的内容，将其添加到当前节点
                if current_content:
                    node_stack[-1]["content"] = "\n".join(current_content).strip()
                    current_content = []
                
                # 获取标题级别和内容
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                # 创建新节点
                new_node = {
                    "title": title,
                    "content": "",
                    "children": [],
                    "level": level
                }
                
                # 根据层级关系添加到树中
                while len(node_stack) > 1 and node_stack[-1]["level"] >= level:
                    node_stack.pop()
                
                node_stack[-1]["children"].append(new_node)
                node_stack.append(new_node)
            else:
                # 非标题行，添加到当前内容
                current_content.append(line)
        
        # 处理最后一个节点的内容
        if current_content:
            node_stack[-1]["content"] = "\n".join(current_content).strip()
        
        return root["children"]
    
    def extract_all(self) -> Dict[str, List[Dict]]:
        """
        提取所有结构数据
        
        Returns:
            包含所有提取结果的字典
        """
        return {
            "structure": self.extract_structure()
        }

def extract_structure_from_markdown(markdown_content: str) -> Dict[str, List[Dict]]:
    """
    从 Markdown 内容中提取结构数据
    
    Args:
        markdown_content: Markdown 内容
        
    Returns:
        包含所有提取结果的字典
    """
    try:
        extractor = MarkdownStructureExtractor(markdown_content)
        return extractor.extract_all()
        
    except Exception as e:
        logger.error(f"处理 Markdown 内容时出错: {e}")
        raise

def process_markdown_structure(content: str, product_code: str, save: bool = False) -> str:
    """
    处理 Markdown 内容并返回 JSON 结果
    
    Args:
        content: Markdown 内容
        product_code: 产品编号
        save: 是否保存到文件
        
    Returns:
        JSON 字符串
    """
    try:
        # 提取结构数据
        results = extract_structure_from_markdown(content)
        
        # 转换为 JSON 字符串
        json_str = json.dumps(results, ensure_ascii=False, indent=2)
        
        # 如果需要保存到文件
        if save:
            # 构建输出路径
            output_dir = Path(f"./data/{product_code}/json")
            output_path = output_dir / f"{product_code}.structure.json"
            
            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
                
            logger.info(f"JSON 数据已保存到: {output_path}")
        
        return json_str
        
    except Exception as e:
        logger.error(f"处理内容时出错: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='从 Markdown 中提取层级结构数据')
    parser.add_argument('--text', help='Markdown 文本内容')
    parser.add_argument('--file', help='MultipartFile 文件')
    parser.add_argument('--src', help='源 Markdown 文件路径')
    parser.add_argument('--product_code', required=True, help='产品编号')
    parser.add_argument('--save', type=bool, default=False, help='是否保存到文件')
    
    args = parser.parse_args()
    
    try:
        content = None
        
        # 按优先级处理输入
        if args.text:
            content = args.text
        elif args.file:
            # 处理 MultipartFile
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        elif args.src:
            with open(args.src, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            logger.error("必须提供 --text、--file 或 --src 参数之一")
            exit(1)
        
        # 处理内容并获取 JSON 结果
        json_result = process_markdown_structure(content, args.product_code, args.save)
        
        # 输出 JSON 结果
        print(json_result)
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        exit(1)

if __name__ == "__main__":
    main() 