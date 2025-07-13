import random
import string
from typing import List, Tuple


def generate_sample_credentials(count: int = 100) -> List[Tuple[str, str]]:
    """
    生成示例凭证数据
    
    Args:
        count: 生成数量
        
    Returns:
        凭证列表
    """
    credentials = []
    
    # 生成随机用户名和密码
    for i in range(count):
        username = f"user{i}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        credentials.append((username, password))
    
    return credentials


def get_common_weak_passwords() -> List[Tuple[str, str]]:
    """
    获取常见弱密码列表
    
    Returns:
        弱密码凭证列表
    """
    weak_passwords = [
        "password", "123456", "password123", "admin", "qwerty",
        "letmein", "welcome", "monkey", "dragon", "master",
        "123456789", "12345678", "12345", "1234567890",
        "abc123", "Password1", "password1", "admin123",
        "root", "guest", "test", "demo", "user", "login"
    ]
    
    credentials = []
    for i, password in enumerate(weak_passwords):
        username = f"weakuser{i}"
        credentials.append((username, password))
    
    return credentials


def get_test_credentials() -> List[Tuple[str, str]]:
    """
    获取测试用凭证
    
    Returns:
        测试凭证列表
    """
    return [
        ("alice", "password123"),
        ("bob", "qwerty"),
        ("charlie", "123456"),
        ("diana", "admin"),
        ("eve", "welcome"),
        ("frank", "letmein"),
        ("grace", "monkey"),
        ("henry", "dragon"),
        ("ivy", "master"),
        ("jack", "password")
    ]


def get_breach_simulation_data() -> List[Tuple[str, str]]:
    """
    获取泄露模拟数据
    
    Returns:
        模拟泄露数据
    """
    # 合并所有类型的数据
    all_credentials = []
    
    # 添加随机凭证
    all_credentials.extend(generate_sample_credentials(500))
    
    # 添加弱密码
    all_credentials.extend(get_common_weak_passwords())
    
    # 添加测试凭证
    all_credentials.extend(get_test_credentials())
    
    return all_credentials


def get_email_based_credentials() -> List[Tuple[str, str]]:
    """
    获取基于邮箱的凭证
    
    Returns:
        邮箱凭证列表
    """
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "163.com"]
    passwords = ["password", "123456", "qwerty", "abc123", "password123"]
    
    credentials = []
    for i in range(50):
        domain = random.choice(domains)
        password = random.choice(passwords)
        username = f"user{i}@{domain}"
        credentials.append((username, password))
    
    return credentials


def create_custom_breach_data(breach_name: str, credential_count: int) -> dict:
    """
    创建自定义泄露数据
    
    Args:
        breach_name: 泄露事件名称
        credential_count: 凭证数量
        
    Returns:
        泄露数据字典
    """
    credentials = generate_sample_credentials(credential_count)
    
    return {
        "breach_name": breach_name,
        "credentials": [
            {"username": username, "password": password}
            for username, password in credentials
        ]
    }


# 预定义的泄露数据集
SAMPLE_BREACHES = [
    {
        "name": "示例社交网络泄露",
        "credentials": get_test_credentials()
    },
    {
        "name": "弱密码数据库",
        "credentials": get_common_weak_passwords()
    },
    {
        "name": "邮箱服务泄露",
        "credentials": get_email_based_credentials()
    }
] 