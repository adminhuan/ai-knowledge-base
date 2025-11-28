from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
import os
import uuid
import base64

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.ai_service import ai_service
from app.services.cos_service import cos_service
from app.models.file_storage import FileStorage

router = APIRouter()


class UploadToCOSRequest(BaseModel):
    """上传到云端请求"""
    file_data: str  # base64 编码的文件数据
    filename: str
    file_type: str  # image/document
    description: Optional[str] = None
    message_id: Optional[int] = None

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image")
async def upload_and_parse_image(
    file: UploadFile = File(...),
    prompt: str = Form(default="请描述这张图片的内容"),
    user_id: int = Depends(get_current_user_id)
):
    """上传图片并用 AI 解析"""
    # 检查文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG/PNG/GIF/WebP 图片")
    
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小 (最大 10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 10MB")
    
    # 转换为 base64
    b64_data = base64.b64encode(content).decode('utf-8')
    
    # 获取 MIME 类型
    mime_type = file.content_type
    data_url = f"data:{mime_type};base64,{b64_data}"
    
    # 调用 AI 解析图片
    result = await ai_service.parse_image(data_url, prompt)
    
    if result.get("success"):
        return {
            "code": 0,
            "data": {
                "content": result["content"],
                "model": result.get("model", ""),
                "provider": result.get("provider", ""),
                "input_tokens": result.get("input_tokens", 0),
                "output_tokens": result.get("output_tokens", 0)
            }
        }
    else:
        return {
            "code": -1,
            "message": result.get("error", "图片解析失败")
        }


@router.post("/file")
async def upload_and_parse_file(
    file: UploadFile = File(...),
    prompt: str = Form(default="请描述这个文件的内容"),
    user_id: int = Depends(get_current_user_id)
):
    """上传文档并用 AI 解析 (PDF/Word/Excel)"""
    # 检查文件类型
    allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="只支持 PDF/Word/Excel/PPT 文档")
    
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小 (最大 30MB)
    if len(content) > 30 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过 30MB")
    
    # 调用文档解析
    result = await ai_service.parse_document(content, filename, prompt)
    
    if result.get("success"):
        return {
            "code": 0,
            "data": {
                "content": result["content"],
                "model": result.get("model", ""),
                "provider": result.get("provider", ""),
                "input_tokens": result.get("input_tokens", 0),
                "output_tokens": result.get("output_tokens", 0)
            }
        }
    else:
        return {
            "code": -1,
            "message": result.get("error", "文档解析失败")
        }


@router.post("/to-cos")
async def upload_to_cos(
    request: UploadToCOSRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """上传文件到腾讯云 COS 并保存记录"""
    try:
        # 解码 base64 数据
        file_data = base64.b64decode(request.file_data)
        
        # 确定文件夹
        folder = "images" if request.file_type == "image" else "files"
        
        # 上传到 COS
        result = cos_service.upload_file(
            file_data=file_data,
            filename=request.filename,
            user_id=user_id,
            folder=folder
        )
        
        if not result.get("success"):
            return {"code": -1, "message": result.get("error", "上传失败")}
        
        # 保存文件记录到数据库
        ext = os.path.splitext(request.filename)[1].lower()
        file_record = FileStorage(
            user_id=user_id,
            filename=request.filename,
            file_type=request.file_type,
            file_ext=ext,
            file_size=result["size"],
            cos_key=result["key"],
            cos_url=result["url"],
            message_id=request.message_id,
            description=request.description,
            is_permanent=1,
            status=1
        )
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        
        return {
            "code": 0,
            "data": {
                "id": file_record.id,
                "url": result["url"],
                "filename": request.filename,
                "size": result["size"]
            },
            "message": "上传成功"
        }
    except Exception as e:
        return {"code": -1, "message": f"上传失败: {str(e)}"}


@router.get("/files")
async def get_user_files(
    file_type: str = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取用户上传的文件列表"""
    query = select(FileStorage).where(
        FileStorage.user_id == user_id,
        FileStorage.status == 1
    )
    
    if file_type:
        if file_type == 'document':
            # document 类型匹配所有非图片文件
            query = query.where(FileStorage.file_type != 'image')
        else:
            query = query.where(FileStorage.file_type == file_type)
    
    query = query.order_by(FileStorage.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    # 如果存储桶是公有读，直接用原始 URL
    # 如果是私有存储桶，需要生成签名 URL
    file_list = []
    for f in files:
        file_list.append({
            "id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "url": f.cos_url,  # 公有读存储桶直接用原始 URL
            "cos_key": f.cos_key,
            "description": f.description,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    
    return {
        "code": 0,
        "data": {
            "list": file_list
        }
    }


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """删除文件"""
    result = await db.execute(
        select(FileStorage).where(
            FileStorage.id == file_id,
            FileStorage.user_id == user_id
        )
    )
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        return {"code": -1, "message": "文件不存在"}
    
    # 从 COS 删除
    cos_service.delete_file(file_record.cos_key)
    
    # 标记为已删除
    file_record.status = 0
    await db.commit()
    
    return {"code": 0, "message": "删除成功"}


@router.post("/file-to-cos")
async def upload_file_to_cos(
    file: UploadFile = File(...),
    folder: str = Form(default="uploads"),
    user_id: int = Depends(get_current_user_id)
):
    """直接上传文件到 COS（头像等）"""
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小 (最大 5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过 5MB")
    
    # 上传到 COS
    result = cos_service.upload_file(content, file.filename or 'file.jpg', user_id, folder)
    
    if not result or not result.get('success'):
        raise HTTPException(status_code=500, detail="上传失败")
    
    return {
        "code": 0,
        "data": {
            "url": result['url'],
            "filename": result.get('key', '')
        }
    }
