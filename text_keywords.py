#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本关键词提取工具
使用jieba的TextRank算法从文本中提取关键词
"""

import jieba.analyse
import argparse
import json
import sys

def extract_keywords(text: str, topk: int = 10) -> list:
    """
    从文本中提取关键词
    
    Args:
        text: 要处理的文本内容
        topk: 返回的关键词数量
        
    Returns:
        关键词列表，每个元素为(关键词, 权重)的元组
    """
    # 使用TextRank算法提取关键词
    keywords = jieba.analyse.textrank(text, topK=topk, withWeight=True)
    return keywords

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='从文本中提取关键词')
    parser.add_argument('--text', type=str, required=True, help='要处理的文本内容')
    parser.add_argument('--topk', type=int, default=10, help='返回的关键词数量（默认为10）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    try:
        # 提取关键词
        keywords = extract_keywords(args.text, args.topk)
        
        # 将结果转换为JSON格式
        result = {
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
                "topk": args.topk
            }
        }
        
        # 输出JSON结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        # 错误处理
        error_result = {
            "status": "error",
            "message": f"处理文本时出错: {str(e)}",
            "code": "PROCESSING_ERROR"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main() 