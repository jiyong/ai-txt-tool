import json
import re
import argparse
from typing import Dict, List, Any

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
        
    def clean_markdown_format(self, text: str) -> str:
        """
        清理文本中的 Markdown 格式
        
        Args:
            text: 包含 Markdown 格式的文本
            
        Returns:
            清理后的纯文本
        """
        # 处理转义字符
        text = text.replace('\\.', '.')
        text = text.replace('\\*', '*')
        text = text.replace('\\_', '_')
        text = text.replace('\\`', '`')
        text = text.replace('\\[', '[')
        text = text.replace('\\]', ']')
        text = text.replace('\\{', '{')
        text = text.replace('\\}', '}')
        text = text.replace('\\#', '#')
        text = text.replace('\\+', '+')
        text = text.replace('\\-', '-')
        text = text.replace('\\!', '!')
        text = text.replace('\\>', '>')
        
        # 替换图片标记为"图片"
        text = re.sub(r'!\[.*?\]\(.*?\)', '图片', text)
        
        # 替换链接为纯文本
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # 替换加粗和斜体标记
        text = re.sub(r'[*_]{1,2}(.*?)[*_]{1,2}', r'\1', text)
        
        # 替换代码块标记
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # 替换删除线
        text = re.sub(r'~~(.*?)~~', r'\1', text)
        
        # 替换引用标记
        text = re.sub(r'^>\s*', '', text)
        
        # 替换水平分割线
        text = re.sub(r'^[-*_]{3,}$', '', text)
        
        # 替换列表标记
        text = re.sub(r'^[-*+]\s*', '', text)
        text = re.sub(r'^\d+\.\s*', '', text)
        
        # 清理多余的空格
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
    def extract_structure(self) -> List[Dict]:
        """
        从 Markdown 内容中提取层级结构
        
        Returns:
            树状结构数据
        """
        # 初始化根节点
        root = {
            "name": "Root",
            "children": [],
            "level": 0
        }
        
        # 当前节点栈，用于跟踪层级关系
        node_stack = [root]
        
        # 标题正则表达式
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        
        for line in self.lines:
            # 检查是否是标题
            heading_match = heading_pattern.match(line)
            
            if heading_match:
                # 获取标题级别和内容
                level = len(heading_match.group(1))
                name = heading_match.group(2).strip()
                
                # 清理 Markdown 格式
                name = self.clean_markdown_format(name)
                
                # 创建新节点
                new_node = {
                    "name": name,
                    "children": [],
                    "level": level
                }
                
                # 根据层级关系添加到树中
                while len(node_stack) > 1 and node_stack[-1]["level"] >= level:
                    node_stack.pop()
                
                node_stack[-1]["children"].append(new_node)
                node_stack.append(new_node)
        
        return root["children"]

def text_to_json(text: str) -> str:
    """
    将文本转换为JSON格式的字符串
    
    Args:
        text: 输入的文本内容
        
    Returns:
        JSON格式的字符串
    """
    extractor = MarkdownStructureExtractor(text)
    structure = extractor.extract_structure()
    return json.dumps(structure, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description='从 Markdown 中提取层级结构数据')
    parser.add_argument('--text', help='Markdown 文本内容')
    
    args = parser.parse_args()
    
    if args.text:
        result = text_to_json(args.text)
        print(result)
    else:
        print("请提供 Markdown 文本内容，使用 --text 参数")

if __name__ == "__main__":
    main() 