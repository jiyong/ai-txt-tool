#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown结构提取器
此脚本用于提取Markdown文件中的标题层级结构，并生成JSON格式的数据
"""

import sys
import os
import json
import re
import uuid
from pathlib import Path
import argparse

class MarkdownNode:
    def __init__(self, title="", level=0):
        self.title = title
        self.level = level
        self.children = []
        self.id = str(uuid.uuid4())  # 生成唯一ID
    
    def to_dict(self):
        """将节点转换为字典格式"""
        result = {
            "id": self.id,
            "name": self.title,
            "depth": self.level,
            "style": {"collapsed": False} if self.level == 0 else {"collapsed": True},
            "children": []
        }
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        return result

def extract_headers(markdown_content):
    """
    从Markdown内容中提取所有标题
    
    Args:
        markdown_content: Markdown文本内容
        
    Returns:
        标题列表，每个元素是(level, title)的元组
    """
    # 匹配Markdown标题的正则表达式（更新以处理更多情况）
    header_pattern = re.compile(r'^(#{1,6})\s+([^#\n]+?)(?:\s*\[.*\].*)?$', re.MULTILINE)
    headers = []
    
    for match in header_pattern.finditer(markdown_content):
        level = len(match.group(1))  # #的数量表示层级
        title = match.group(2).strip()
        # 移除可能的链接标记和其他标记
        title = re.sub(r'\[([^\]]+)\].*', r'\1', title)
        title = re.sub(r'[*_`]', '', title)  # 移除强调标记
        if not title.startswith('!'):  # 只添加非图片标题
            headers.append((level, title))
    
    return headers

def build_hierarchy(headers):
    """
    根据标题列表构建层级结构
    
    Args:
        headers: 标题列表，每个元素是(level, title)的元组
        
    Returns:
        根节点
    """
    print("\n开始构建层级结构...")
    
    root = MarkdownNode("root", 0)
    stack = [(root, 0)]  # 使用元组存储(节点, 层级)
    
    for level, title in headers:
        # 跳过包含感叹号的标题
        if '!' in title:
            print(f"跳过标题: {title}")
            continue
            
        print(f"\n处理标题: {title} (level: {level})")
        node = MarkdownNode(title, level)
        
        # 回溯到合适的父节点
        while len(stack) > 1 and stack[-1][1] >= level:
            popped = stack.pop()
            print(f"  回溯: 移除 {popped[0].title}")
        
        # 添加到父节点
        parent = stack[-1][0]
        parent.children.append(node)
        print(f"  添加到父节点: {parent.title}")
        
        # 将当前节点加入栈
        stack.append((node, level))
        print(f"  当前栈深度: {len(stack)}")
    
    print("\n层级结构构建完成")
    print("根节点的直接子节点数量:", len(root.children))
    for child in root.children:
        print(f"- {child.title} (子节点数量: {len(child.children)})")
    
    return root

def process_markdown_file(markdown_path, output_path=None, root_name=None):
    """
    处理单个Markdown文件
    
    Args:
        markdown_path: Markdown文件路径
        output_path: 输出JSON文件路径（可选）
        root_name: 根节点的名称（可选）
        
    Returns:
        生成的JSON结构
    """
    try:
        # 读取Markdown文件
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题
        headers = extract_headers(content)
        print(f"\n找到 {len(headers)} 个标题")
        print("\n提取的标题:")
        for level, title in headers:
            print(f"{'  ' * (level-1)}- {title} (level: {level})")
        
        # 构建层级结构
        root = build_hierarchy(headers)
        if root_name:
            root.title = root_name
        
        # 打印层级结构（用于调试）
        print("\n构建的层级结构:")
        def print_node(node, depth=0):
            print(f"{'  ' * depth}- {node.title} (level: {node.level}, children: {len(node.children)})")
            for child in node.children:
                print_node(child, depth + 1)
        print_node(root)
        
        # 转换为JSON结构
        structure = root.to_dict()
        
        # 打印完整的JSON结构（用于调试）
        print("\n完整的JSON结构:")
        print(json.dumps(structure, ensure_ascii=False, indent=2))
        
        # 如果指定了输出路径，保存JSON文件
        if output_path:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)
            
            print(f"\n结构已保存到: {output_path}")
        
        return structure
        
    except Exception as e:
        print(f"处理文件 {markdown_path} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def process_directory(input_dir, output_dir):
    """
    处理目录下的所有Markdown文件
    
    Args:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 遍历所有Markdown文件
    for markdown_file in input_path.rglob('*.md'):
        # 构建对应的输出路径
        relative_path = markdown_file.relative_to(input_path)
        output_file = output_path / relative_path.with_suffix('.json')
        
        print(f"处理文件: {markdown_file}")
        process_markdown_file(markdown_file, output_file)

def main():
    parser = argparse.ArgumentParser(description='提取Markdown文件的标题层级结构')
    parser.add_argument('--input', required=True, help='输入Markdown文件或目录的路径')
    parser.add_argument('--output', help='输出JSON文件或目录的路径')
    parser.add_argument('--name', help='根节点的名称')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    
    if input_path.is_file():
        # 处理单个文件
        process_markdown_file(input_path, output_path, args.name)
    elif input_path.is_dir():
        # 处理目录
        if not output_path:
            output_path = input_path.parent / 'structure'
        process_directory(input_path, output_path)
    else:
        print(f"错误: 输入路径 {input_path} 不存在")
        sys.exit(1)

if __name__ == "__main__":
    main() 