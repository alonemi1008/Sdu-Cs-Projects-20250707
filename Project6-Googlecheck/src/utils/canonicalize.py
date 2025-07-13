import re
# 移除不必要的typing导入


def canonicalize_username(username: str) -> str:
    """
    标准化用户名，遵循Google Password Checkup协议
    
    规则:
    1. 转换为小写
    2. 去除邮箱域名部分（@后的内容）
    3. 去除多余空格
    
    Args:
        username: 原始用户名
        
    Returns:
        标准化后的用户名
    """
    if not username:
        return ""
    
    # 转换为小写
    username = username.lower().strip()
    
    # 如果是邮箱格式，只保留@前面的部分
    if '@' in username:
        username = username.split('@')[0]
    
    # 去除特殊字符，只保留字母数字和基本符号
    username = re.sub(r'[^\w\-\.]', '', username)
    
    return username


def validate_credentials(username: str, password: str) -> bool:
    """
    验证凭证格式是否有效
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        是否有效
    """
    from .constants import MIN_PASSWORD_LENGTH, MAX_USERNAME_LENGTH, MAX_PASSWORD_LENGTH
    
    if not username or not password:
        return False
    
    if len(username) > MAX_USERNAME_LENGTH:
        return False
    
    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        return False
    
    return True 