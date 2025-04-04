from pathlib import Path
import pandas as pd
import os
import re

def clean_string(s):
    # 清理字符串中的特殊字符和多余的空白
    if pd.isna(s):
        return ""
    # 转换为字符串并清理
    s = str(s).strip()
    # 替换所有类型的换行符和多余空格
    s = re.sub(r'[\n\r]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def clean_header(header):
    # 移除括号及其内容，包括各种类型的括号
    header = re.sub(r'[\(（].*?[\)）]', '', str(header))
    # 移除空格
    header = header.replace(' ', '')
    # 移除其他特殊字符
    header = re.sub(r'[^\w\u4e00-\u9fff]', '', header)
    return header.strip()

def process_excel_file(excel_path, dir_path):
    """处理单个Excel文件并生成元数据文件"""
    try:
        # 读取Excel文件，跳过第一行，使用第二行作为表头
        df = pd.read_excel(excel_path, header=1)
        
        # 清理列名（移除括号内容）
        df.columns = [clean_header(col) for col in df.columns]
        
        # 打印列名，帮助调试
        print(f"Excel文件的列名：{list(df.columns)}")
        
        # 检查是否存在产品编号列
        if '产品编号' not in df.columns:
            print(f"错误：在文件 {os.path.basename(excel_path)} 中没有找到'产品编号'列")
            print("可用的列名：")
            for col in df.columns:
                print(f"- {col}")
            return False
        
        # 遍历每一行数据
        for _, row in df.iterrows():
            # 获取图书产品编号
            book_id = clean_string(row['产品编号'])
            if not book_id:  # 跳过空的产品编号
                continue

            if book_id == '089523-01':
                continue
            
            # 创建元数据文件路径
            meta_dir = os.path.join("output", "meta", book_id)
            file_path = os.path.join(meta_dir, f"{book_id}.meta.md")
            os.makedirs(meta_dir, exist_ok=True)

            print(f"开始 使用excel文件 {excel_path} 写入文件 {file_path}")
            
            # 将行数据转换为元数据格式并写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                first_item = True
                for column in df.columns:
                    value = row[column]
                    # 确保值不是NaN，并转换为字符串
                    if pd.notna(value):
                        if not first_item:
                            f.write('\n' + '-' * 20 + '\n')
                        else:
                            first_item = False
                        
                        # 清理列名和值
                        column_clean = clean_string(column)
                        value_clean = clean_string(value)
                        
                        # 确保键和值在同一行，并且没有换行
                        f.write(f"{column_clean}:{value_clean}")
        return True
    except Exception as e:
        print(f"处理文件 {os.path.basename(excel_path)} 时出错：{str(e)}")
        return False

def process_book_meta(product_code):
    """处理单个目录下的Excel文件"""
    # 获取目录名
    current_dir = Path.cwd()
    src_dir = current_dir / 'src' / product_code
    # dir_name = os.path.basename(dir_path)
    
    # 查找目录中的Excel文件
    excel_files = [f for f in os.listdir(src_dir) if f.endswith(('.xlsx', '.xls'))]
    
    if not excel_files:
        print(f"警告：在目录 {src_dir} 中没有找到Excel文件")
        return False
    
    # 使用第一个找到的Excel文件
    excel_path = os.path.join(src_dir, excel_files[0])
    print(f"正在处理目录 {src_dir} 中的文件：{excel_files[0]}")
    
    return process_excel_file(excel_path, src_dir)

def create_meta_files(src_dir):
    """处理src目录下的所有子目录"""
    success_count = 0
    total_count = 0
    
    # 确保output/meta目录存在
    os.makedirs(os.path.join("output", "meta"), exist_ok=True)
    
    # 遍历src目录下的所有子目录
    for dir_name in os.listdir(src_dir):
        dir_path = os.path.join(src_dir, dir_name)
        
        # 确保是目录
        if not os.path.isdir(dir_path):
            continue
        
        total_count += 1
        if process_book_meta(dir_path):
            success_count += 1
    
    print(f"\n处理完成！")
    print(f"成功处理: {success_count}/{total_count} 个目录")

if __name__ == "__main__":
    src_dir = "src"
    
    if not os.path.exists(src_dir):
        print(f"错误：找不到目录 '{src_dir}'！")
        exit(1)
    
    print(f"开始处理 {src_dir} 目录下的所有数据...")
    create_meta_files(src_dir) 