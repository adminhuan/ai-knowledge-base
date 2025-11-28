"""
安全中间件 - 请求频率限制、IP黑名单、安全日志
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import hashlib
import logging
from typing import Dict, Tuple, List
from collections import defaultdict
from datetime import datetime
import re

# 配置安全日志
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)
if not security_logger.handlers:
    handler = logging.FileHandler('security.log', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    security_logger.addHandler(handler)

# 内存存储（生产环境建议用 Redis）
rate_limit_store: Dict[str, list] = defaultdict(list)
ip_blacklist: set = set()
login_attempts: Dict[str, Tuple[int, float]] = {}  # IP -> (失败次数, 最后尝试时间)
security_events: List[Dict] = []  # 安全事件记录

# 配置
RATE_LIMIT_WINDOW = 60  # 时间窗口（秒）
RATE_LIMIT_MAX_REQUESTS = 100  # 普通接口每分钟最大请求数
RATE_LIMIT_STRICT = 10  # 敏感接口每分钟最大请求数
LOGIN_MAX_ATTEMPTS = 5  # 最大登录失败次数
LOGIN_LOCKOUT_TIME = 300  # 锁定时间（秒）

# 敏感接口（需要更严格的限制）
STRICT_RATE_LIMIT_PATHS = [
    '/api/user/login',
    '/api/user/register',
    '/api/chat',
]

# XSS 危险模式
XSS_PATTERNS = [
    r'<script[^>]*>',
    r'javascript:',
    r'on\w+\s*=',
    r'<iframe',
    r'<object',
    r'<embed',
]


def get_client_ip(request: Request) -> str:
    """获取客户端真实 IP"""
    # 优先从代理头获取
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    return request.client.host if request.client else '127.0.0.1'


def check_rate_limit(ip: str, path: str) -> bool:
    """检查请求频率限制，返回 True 表示允许，False 表示超限"""
    now = time.time()
    key = f"{ip}:{path}"
    
    # 清理过期记录
    rate_limit_store[key] = [t for t in rate_limit_store[key] if now - t < RATE_LIMIT_WINDOW]
    
    # 确定限制数量
    is_strict = any(path.startswith(p) for p in STRICT_RATE_LIMIT_PATHS)
    max_requests = RATE_LIMIT_STRICT if is_strict else RATE_LIMIT_MAX_REQUESTS
    
    # 检查是否超限
    if len(rate_limit_store[key]) >= max_requests:
        return False
    
    # 记录请求
    rate_limit_store[key].append(now)
    return True


def check_login_lockout(ip: str) -> Tuple[bool, int]:
    """检查登录锁定状态，返回 (是否锁定, 剩余锁定时间)"""
    if ip not in login_attempts:
        return False, 0
    
    attempts, last_time = login_attempts[ip]
    now = time.time()
    
    # 如果超过锁定时间，重置
    if now - last_time > LOGIN_LOCKOUT_TIME:
        del login_attempts[ip]
        return False, 0
    
    # 如果达到最大尝试次数
    if attempts >= LOGIN_MAX_ATTEMPTS:
        remaining = int(LOGIN_LOCKOUT_TIME - (now - last_time))
        return True, remaining
    
    return False, 0


def record_login_attempt(ip: str, success: bool):
    """记录登录尝试"""
    now = time.time()
    
    if success:
        # 登录成功，清除记录
        if ip in login_attempts:
            del login_attempts[ip]
        log_security_event('login_success', ip, '登录成功', 'info')
    else:
        # 登录失败，增加计数
        if ip in login_attempts:
            attempts, _ = login_attempts[ip]
            login_attempts[ip] = (attempts + 1, now)
            if attempts + 1 >= LOGIN_MAX_ATTEMPTS:
                log_security_event('login_locked', ip, f'登录失败次数过多({attempts + 1}次)，已锁定', 'error')
            else:
                log_security_event('login_failure', ip, f'登录失败，第 {attempts + 1} 次', 'warning')
        else:
            login_attempts[ip] = (1, now)
            log_security_event('login_failure', ip, '登录失败，第 1 次', 'warning')


def check_xss(content: str) -> bool:
    """检查是否包含 XSS 攻击模式，返回 True 表示安全"""
    if not content:
        return True
    
    content_lower = content.lower()
    for pattern in XSS_PATTERNS:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return False
    return True


def sanitize_input(content: str) -> str:
    """清理输入内容，移除危险字符"""
    if not content:
        return content
    
    # HTML 转义
    content = content.replace('<', '&lt;').replace('>', '&gt;')
    return content


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next):
        ip = get_client_ip(request)
        path = request.url.path
        
        # 1. 检查 IP 黑名单
        if ip in ip_blacklist:
            log_security_event('blacklist_block', ip, f'黑名单IP尝试访问: {path}', 'warning')
            return JSONResponse(
                status_code=403,
                content={"code": 403, "message": "访问被拒绝"}
            )
        
        # 2. 检查请求频率
        if not check_rate_limit(ip, path):
            log_security_event('rate_limit', ip, f'请求频率超限: {path}', 'warning')
            return JSONResponse(
                status_code=429,
                content={"code": 429, "message": "请求过于频繁，请稍后再试"}
            )
        
        # 3. 登录接口特殊处理
        if path == '/api/user/login':
            is_locked, remaining = check_login_lockout(ip)
            if is_locked:
                log_security_event('login_lockout', ip, f'登录锁定中，剩余 {remaining} 秒', 'warning')
                return JSONResponse(
                    status_code=423,
                    content={"code": 423, "message": f"登录失败次数过多，请 {remaining} 秒后再试"}
                )
        
        # 4. 执行请求
        response = await call_next(request)
        
        # 5. 添加安全响应头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


# 工具函数：添加 IP 到黑名单
def add_to_blacklist(ip: str):
    ip_blacklist.add(ip)
    log_security_event('blacklist_add', ip, f'IP {ip} 已加入黑名单')


# 工具函数：从黑名单移除 IP
def remove_from_blacklist(ip: str):
    ip_blacklist.discard(ip)


# 工具函数：获取当前黑名单
def get_blacklist():
    return list(ip_blacklist)


# 安全事件记录
def log_security_event(event_type: str, ip: str, message: str, level: str = 'warning'):
    """记录安全事件"""
    event = {
        'time': datetime.now().isoformat(),
        'type': event_type,
        'ip': ip,
        'message': message
    }
    security_events.append(event)
    
    # 只保留最近 1000 条记录
    if len(security_events) > 1000:
        security_events.pop(0)
    
    # 写入日志文件
    if level == 'warning':
        security_logger.warning(f"[{event_type}] {ip} - {message}")
    elif level == 'error':
        security_logger.error(f"[{event_type}] {ip} - {message}")
    else:
        security_logger.info(f"[{event_type}] {ip} - {message}")


# 获取安全事件
def get_security_events(limit: int = 100):
    """获取最近的安全事件"""
    return security_events[-limit:][::-1]


# 获取安全统计
def get_security_stats():
    """获取安全统计信息"""
    now = time.time()
    
    # 统计最近1小时的事件
    recent_events = [e for e in security_events if datetime.fromisoformat(e['time']).timestamp() > now - 3600]
    
    stats = {
        'blacklist_count': len(ip_blacklist),
        'locked_ips': sum(1 for attempts, last_time in login_attempts.values() if attempts >= LOGIN_MAX_ATTEMPTS and now - last_time < LOGIN_LOCKOUT_TIME),
        'recent_events': len(recent_events),
        'rate_limit_hits': sum(1 for e in recent_events if e['type'] == 'rate_limit'),
        'login_failures': sum(1 for e in recent_events if e['type'] == 'login_failure'),
    }
    return stats
