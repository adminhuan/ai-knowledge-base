"""腾讯云 COS 文件存储服务"""
from qcloud_cos import CosConfig, CosS3Client
from app.core.config import settings
import uuid
from datetime import datetime
import os


class COSService:
    def __init__(self):
        config = CosConfig(
            Region=settings.COS_REGION,
            SecretId=settings.COS_SECRET_ID,
            SecretKey=settings.COS_SECRET_KEY,
        )
        self.client = CosS3Client(config)
        self.bucket = settings.COS_BUCKET
        self.base_url = f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com"
    
    def upload_file(self, file_data: bytes, filename: str, user_id: int, folder: str = "files") -> dict:
        """上传文件到 COS
        
        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            user_id: 用户ID
            folder: 存储文件夹 (files/images)
        
        Returns:
            {"success": True, "url": "...", "key": "..."}
        """
        try:
            # 生成唯一文件名
            ext = os.path.splitext(filename)[1].lower()
            date_path = datetime.now().strftime("%Y/%m/%d")
            unique_name = f"{uuid.uuid4().hex}{ext}"
            key = f"{folder}/user_{user_id}/{date_path}/{unique_name}"
            
            # 上传到 COS
            self.client.put_object(
                Bucket=self.bucket,
                Body=file_data,
                Key=key,
                ContentType=self._get_content_type(ext)
            )
            
            # 返回访问 URL
            url = f"{self.base_url}/{key}"
            
            return {
                "success": True,
                "url": url,
                "key": key,
                "filename": filename,
                "size": len(file_data)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, key: str) -> bool:
        """删除 COS 文件"""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except Exception:
            return False
    
    def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        """获取临时下载 URL（私有读取时使用）"""
        try:
            url = self.client.get_presigned_download_url(
                Bucket=self.bucket,
                Key=key,
                Expired=expires
            )
            return url
        except Exception:
            return ""
    
    def _get_content_type(self, ext: str) -> str:
        """根据扩展名获取 Content-Type"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
        }
        return content_types.get(ext, 'application/octet-stream')


cos_service = COSService()
