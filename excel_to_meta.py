import argparse
from pathlib import Path
import pandas as pd
import os
import re
import sys

class ExcelFormat:
    OLD = "old"  # template.old.xlsx format
    NEW = "new"  # template.new.xlsx format
    SIMPLE = "simple"  # 简单格式：第一行是属性，第二行是值
    SIMPLE_WITH_TITLE = "simple_with_title"  # 带标题的简单格式：第一行是标题，第二行是属性，第三行是值
    NEW_WITH_EXAMPLE = "new_with_example"  # 带示例的新格式：第1行是属性，第2行是示例，第3行是提示，第4行是空行，第5行是值

def clean_metadata_text(text):
    """清理元数据文本：
    1. 移除括号及其内容（包括中英文括号）
    2. 只保留换行前的文字
    3. 移除多余空格
    4. 处理特殊情况：
       - 移除括号后的说明文字
       - 处理半个括号的情况
       - 移除"另附"等额外说明
       - 处理带冒号的说明文字
    """
    if pd.isna(text):
        return ""
    
    # 转换为字符串
    text = str(text).strip()
    
    # 只保留换行前的文字
    text = text.split('\n')[0]
    
    # 找到第一个括号的位置
    bracket_pos = -1
    for i, char in enumerate(text):
        if char in '（(':
            bracket_pos = i
            break
    
    # 如果找到括号，只保留括号前的内容
    if bracket_pos != -1:
        text = text[:bracket_pos].strip()
    
    # 移除多余空格
    text = text.strip()
    
    return text

def detect_excel_format(df):
    """检测Excel文件的格式类型"""
    print(f"检测Excel格式，数据形状: {df.shape}")
    print("前6行数据预览:")
    print(df.head(6))
    
    # 检查是否是带标题的简单格式（3行，第一行是标题，第二行是属性，第三行是值）
    if df.shape[0] == 3:
        print("\n检测到带标题的简单格式（3行数据）")
        return ExcelFormat.SIMPLE_WITH_TITLE
    
    # 检查是否是简单格式（只有2行，第一行是属性，第二行是值）
    if df.shape[0] == 2:
        print("\n检测到简单格式（2行数据）")
        return ExcelFormat.SIMPLE
    
    # 检查是否是带示例的新格式（第1行是属性，第2行是示例，第3行是提示，第4行是空行，第5行是值）
    if df.shape[0] >= 5:
        row1 = df.iloc[0]  # 第1行（属性）
        row2 = df.iloc[1]  # 第2行（示例）
        row3 = df.iloc[2]  # 第3行（提示）
        row4 = df.iloc[3]  # 第4行（空行）
        row5 = df.iloc[4]  # 第5行（值）
        
        print(f"\n检查带示例的新格式:")
        print("第1行（属性）:", row1)
        print("第2行（示例）:", row2)
        print("第3行（提示）:", row3)
        print("第4行（空行）:", row4)
        print("第5行（值）:", row5)
        
        # 检查第1行是否包含属性名（带括号说明），第2行是否有示例数据，第3行是否有提示信息，第4行是否为空，第5行是否有实际数据
        if (not row1.isnull().all() and  # 第1行有属性名
            not row2.isnull().all() and  # 第2行有示例数据
            not row3.isnull().all() and  # 第3行有提示信息
            row4.isnull().all() and      # 第4行是空行
            not row5.isnull().all()):    # 第5行有实际数据
            return ExcelFormat.NEW_WITH_EXAMPLE
    
    # 检查是否是NEW格式（第1行是属性，第4行是值）
    if df.shape[0] >= 4:
        row1 = df.iloc[0]  # 第1行
        row4 = df.iloc[3]  # 第4行
        print(f"\n检查NEW格式 - 第1行和第4行内容:")
        print("第1行:", row1)
        print("第4行:", row4)
        if not row1.isnull().all() and not row4.isnull().all():  # 第1行和第4行都有数据
            return ExcelFormat.NEW
    
    # 检查是否是OLD格式（第3行是属性，第4行是值）
    if df.shape[0] >= 4:
        row3 = df.iloc[2]  # 第3行
        row4 = df.iloc[3]  # 第4行
        print(f"\n检查OLD格式 - 第3行和第4行内容:")
        print("第3行:", row3)
        print("第4行:", row4)
        if not row3.isnull().all() and not row4.isnull().all():  # 第3行和第4行都有数据
            return ExcelFormat.OLD
    
    raise ValueError("无法识别Excel文件格式，请检查文件内容是否符合模板格式")

def read_metadata_from_excel(file_path):
    """从Excel文件中读取元数据"""
    print(f"\n开始读取Excel文件: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 先读取整个文件
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise Exception(f"读取Excel文件失败: {str(e)}")
    
    # 检测格式
    format_type = detect_excel_format(df)
    print(f"\n检测到的格式类型: {format_type}")
    
    if format_type == ExcelFormat.SIMPLE_WITH_TITLE:
        # 带标题的简单格式：第一行是标题，第二行是属性，第三行是值
        headers = df.iloc[1]
        values = df.iloc[2]
    elif format_type == ExcelFormat.SIMPLE:
        # 简单格式：第一行是属性，第二行是值
        headers = df.iloc[0]
        values = df.iloc[1]
    elif format_type == ExcelFormat.OLD:
        # old format: 第3行是属性，第4行是值
        headers = df.iloc[2]
        values = df.iloc[3]
    elif format_type == ExcelFormat.NEW:
        # new format: 第1行是属性，第4行是值
        headers = df.iloc[0]
        values = df.iloc[3]
    else:  # ExcelFormat.NEW_WITH_EXAMPLE
        # 带示例的新格式：第1行是属性，第5行是值
        headers = df.iloc[0]
        values = df.iloc[4]
    
    print("\n原始属性名:")
    print(headers)
    
    # 清理列名和值
    metadata = {}
    for header, value in zip(headers, values):
        clean_header = clean_metadata_text(header)
        if pd.notna(clean_header) and clean_header:  # 只保留非空的列
            # 只清理属性名，保留值的原始内容
            metadata[clean_header] = str(value) if pd.notna(value) else ""
    
    print("\n提取的元数据:")
    for key, value in metadata.items():
        print(f"{key}: {value}")
    
    return metadata

def process_excel_file(src_path, output_path, product_code):
    """处理Excel文件并生成元数据Excel"""
    print(f"\n处理参数:")
    print(f"- 源目录: {src_path}")
    print(f"- 输出目录: {output_path}")
    print(f"- 产品编号: {product_code}")
    
    # 构建输入输出路径
    input_dir = Path(src_path) / product_code
    output_dir = Path(output_path) / product_code / "meta"
    output_file = output_dir / f"{product_code}.meta.xlsx"
    
    print(f"\n文件路径:")
    print(f"- 输入目录: {input_dir}")
    print(f"- 输出目录: {output_dir}")
    print(f"- 输出文件: {output_file}")
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找输入目录中的Excel文件
    excel_files = list(input_dir.glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError(f"在目录 {input_dir} 中没有找到Excel文件")
    
    print(f"\n找到的Excel文件:")
    for file in excel_files:
        print(f"- {file}")
    
    # 读取第一个Excel文件
    excel_file = excel_files[0]
    metadata = read_metadata_from_excel(excel_file)
    
    # 创建新的DataFrame
    df = pd.DataFrame([metadata])
    
    # 保存为新的Excel文件
    df.to_excel(output_file, index=False)
    print(f"\n已生成元数据文件：{output_file}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='处理图书元数据Excel文件')
    parser.add_argument('--src', required=True, help='源Excel文件所在的基础目录')
    parser.add_argument('--output', required=True, help='输出目录')
    parser.add_argument('--product_code', required=True, help='图书产品编号')
    
    args = parser.parse_args()
    
    try:
        process_excel_file(args.src, args.output, args.product_code)
    except Exception as e:
        print(f"\n处理失败：{str(e)}", file=sys.stderr)
        exit(1)

if __name__ == "__main__":
    main() 