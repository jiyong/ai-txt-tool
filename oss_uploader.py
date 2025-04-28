import os
import oss2
from typing import Optional
import logging

class OSSUploader:
    def __init__(self):
        self.access_key = os.getenv('ALIYUN_OSS_ACCESS_KEY')
        self.secret_key = os.getenv('ALIYUN_OSS_SECRET_KEY')
        self.endpoint = os.getenv('ALIYUN_OSS_ENDPOINT')
        self.region = os.getenv('ALIYUN_OSS_REGION')
        self.bucket_name = os.getenv('ALIYUN_OSS_BUCKET_NAME')
        self.auth_version = os.getenv('ALIYUN_OSS_AUTH_VERSION', 'v4')
        self.base_path = os.getenv('ALIYUN_OSS_PATH', 'books')
        
        if not all([self.access_key, self.secret_key, self.endpoint, self.bucket_name]):
            raise ValueError("阿里云OSS配置不完整，请检查环境变量")
        
        # 创建Bucket对象
        auth = oss2.Auth(self.access_key, self.secret_key)
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        
    def upload_file(self, local_path: str, oss_path: Optional[str] = None) -> bool:
        """
        上传单个文件到OSS
        
        Args:
            local_path: 本地文件路径
            oss_path: OSS中的目标路径，如果为None则使用文件名
            
        Returns:
            bool: 上传是否成功
        """
        try:
            if not os.path.exists(local_path):
                logging.error(f"文件不存在: {local_path}")
                return False
                
            if oss_path is None:
                oss_path = os.path.basename(local_path)
                
            # 确保OSS路径以base_path开头
            if not oss_path.startswith(self.base_path):
                oss_path = f"{self.base_path}/{oss_path}"
                
            # 上传文件
            self.bucket.put_object_from_file(oss_path, local_path)
            logging.info(f"文件上传成功: {local_path} -> {oss_path}")
            return True
            
        except Exception as e:
            logging.error(f"文件上传失败: {local_path}, 错误: {str(e)}")
            return False
            
    def upload_directory(self, local_dir: str, oss_dir: Optional[str] = None) -> bool:
        """
        上传整个目录到OSS
        
        Args:
            local_dir: 本地目录路径
            oss_dir: OSS中的目标目录，如果为None则使用目录名
            
        Returns:
            bool: 上传是否成功
        """
        try:
            if not os.path.exists(local_dir):
                logging.error(f"目录不存在: {local_dir}")
                return False
                
            if oss_dir is None:
                oss_dir = os.path.basename(local_dir)
                
            # 确保OSS路径以base_path开头
            if not oss_dir.startswith(self.base_path):
                oss_dir = f"{self.base_path}/{oss_dir}"
                
            success = True
            for root, _, files in os.walk(local_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    # 计算相对路径
                    rel_path = os.path.relpath(local_path, local_dir)
                    oss_path = f"{oss_dir}/{rel_path}"
                    
                    if not self.upload_file(local_path, oss_path):
                        success = False
                        
            return success
            
        except Exception as e:
            logging.error(f"目录上传失败: {local_dir}, 错误: {str(e)}")
            return False
            
    def delete_local_files(self, path: str) -> bool:
        """
        删除本地文件或目录
        
        Args:
            path: 要删除的文件或目录路径
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            logging.info(f"本地文件删除成功: {path}")
            return True
        except Exception as e:
            logging.error(f"本地文件删除失败: {path}, 错误: {str(e)}")
            return False 