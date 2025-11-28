from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import uuid
import psutil
import os
from datetime import datetime

from app.core.redis import redis_client
from app.core.security import get_current_user_id
from app.core.security_middleware import (
    get_security_events, get_security_stats, 
    get_blacklist, add_to_blacklist, remove_from_blacklist
)

router = APIRouter()

# 系统日志存储（内存中，重启后清空）
system_logs = []
system_errors = []
MAX_LOGS = 500

LIST_LIMIT = 200


class MonitorMessage(BaseModel):
    source: str
    content: str
    status: Optional[str] = "pending"  # pending/saved/ignored
    time: Optional[str] = None


class UpdateStatus(BaseModel):
    status: str


def _key(user_id: int) -> str:
    return f"monitor:messages:{user_id}"


@router.get("/messages")
async def get_messages(user_id: int = Depends(get_current_user_id)):
    key = _key(user_id)
    data = await redis_client.lrange(key, 0, LIST_LIMIT - 1)
    items = []
    for item in data:
        try:
            items.append(json.loads(item))
        except Exception:
            continue
    return {"code": 0, "data": items}


@router.post("/messages")
async def add_message(
    message: MonitorMessage,
    user_id: int = Depends(get_current_user_id),
):
    key = _key(user_id)
    item = {
        "id": str(uuid.uuid4()),
        "source": message.source,
        "content": message.content,
        "status": message.status or "pending",
        "time": message.time or datetime.now().strftime("%H:%M")
    }
    await redis_client.lpush(key, json.dumps(item))
    await redis_client.ltrim(key, 0, LIST_LIMIT - 1)
    return {"code": 0, "data": item}


@router.put("/messages/{message_id}")
async def update_message(
    message_id: str,
    update: UpdateStatus,
    user_id: int = Depends(get_current_user_id),
):
    key = _key(user_id)
    data = await redis_client.lrange(key, 0, LIST_LIMIT - 1)
    updated = False
    new_list = []
    for raw in data:
        try:
            obj = json.loads(raw)
            if obj.get("id") == message_id:
                obj["status"] = update.status
                updated = True
            new_list.append(json.dumps(obj))
        except Exception:
            new_list.append(raw)
    if updated:
        if new_list:
            await redis_client.delete(key)
            await redis_client.lpush(key, *new_list)
        return {"code": 0, "message": "updated"}
    raise HTTPException(status_code=404, detail="消息不存在")


@router.post("/messages/clear")
async def clear_messages(user_id: int = Depends(get_current_user_id)):
    key = _key(user_id)
    await redis_client.delete(key)
    return {"code": 0, "message": "cleared"}


# ============ 系统监控 API ============

def add_log(level: str, message: str):
    """添加系统日志"""
    global system_logs
    log = {
        "level": level,
        "message": message,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    system_logs.insert(0, log)
    if len(system_logs) > MAX_LOGS:
        system_logs = system_logs[:MAX_LOGS]


def add_error(error_type: str, message: str, stack: str = None):
    """添加异常记录"""
    global system_errors
    err = {
        "type": error_type,
        "message": message,
        "stack": stack,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    system_errors.insert(0, err)
    if len(system_errors) > 100:
        system_errors = system_errors[:100]


# 初始化一些默认日志
if not system_logs:
    system_logs = [
        {"level": "info", "message": "服务启动成功", "time": datetime.now().strftime("%H:%M:%S")},
        {"level": "info", "message": "数据库连接成功", "time": datetime.now().strftime("%H:%M:%S")},
        {"level": "info", "message": "Redis 连接成功", "time": datetime.now().strftime("%H:%M:%S")},
    ]


@router.get("/logs")
async def get_logs(page: int = 1, limit: int = 50):
    """获取系统日志"""
    start = (page - 1) * limit
    end = start + limit
    logs = system_logs[start:end]
    return {"code": 0, "data": {"logs": logs, "total": len(system_logs)}}


@router.get("/errors")
async def get_errors(limit: int = 20):
    """获取异常记录"""
    errors = system_errors[:limit]
    return {"code": 0, "data": {"errors": errors, "total": len(system_errors)}}


@router.get("/stats")
async def get_system_stats():
    """获取系统状态"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 计算运行时间
        import time
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        
        if days > 0:
            uptime = f"{days}天{hours}小时"
        else:
            uptime = f"{hours}小时"
        
        return {
            "code": 0,
            "data": {
                "cpu": round(cpu_percent, 1),
                "memory": round(memory.percent, 1),
                "disk": round(disk.percent, 1),
                "uptime": uptime
            }
        }
    except Exception as e:
        return {
            "code": 0,
            "data": {
                "cpu": 0,
                "memory": 0,
                "disk": 0,
                "uptime": "未知"
            }
        }


@router.delete("/logs")
async def clear_logs():
    """清空日志"""
    global system_logs
    system_logs = []
    return {"code": 0, "message": "日志已清空"}


# ============ 安全监控 API ============

@router.get("/security/events")
async def get_security_events_api(limit: int = 100):
    """获取安全事件"""
    events = get_security_events(limit)
    return {"code": 0, "data": events}


@router.get("/security/stats")
async def get_security_stats_api():
    """获取安全统计"""
    stats = get_security_stats()
    return {"code": 0, "data": stats}


@router.get("/security/blacklist")
async def get_blacklist_api():
    """获取IP黑名单"""
    return {"code": 0, "data": get_blacklist()}


class IPRequest(BaseModel):
    ip: str


@router.post("/security/blacklist")
async def add_blacklist_api(req: IPRequest):
    """添加IP到黑名单"""
    add_to_blacklist(req.ip)
    return {"code": 0, "message": f"IP {req.ip} 已加入黑名单"}


@router.delete("/security/blacklist/{ip}")
async def remove_blacklist_api(ip: str):
    """从黑名单移除IP"""
    remove_from_blacklist(ip)
    return {"code": 0, "message": f"IP {ip} 已从黑名单移除"}
