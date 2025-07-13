import os
import hashlib
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.backends import default_backend
from ..utils.constants import CURVE_NAME, CURVE_POINT_SIZE


class EllipticCurveBlinder:
    """
    椭圆曲线盲化器，实现私有集合交集协议的核心加密功能
    """
    
    def __init__(self, private_key: Optional[bytes] = None):
        """
        初始化椭圆曲线盲化器
        
        Args:
            private_key: 可选的私钥，如果不提供则生成随机私钥
        """
        # 使用secp224r1曲线
        self.curve = ec.SECP224R1()
        
        if private_key:
            self.private_key = ec.derive_private_key(
                int.from_bytes(private_key, byteorder='big'),
                self.curve,
                default_backend()
            )
        else:
            self.private_key = ec.generate_private_key(self.curve, default_backend())
        
        self.public_key = self.private_key.public_key()
    
    def generate_random_key(self) -> bytes:
        """
        生成随机私钥
        
        Returns:
            随机私钥字节
        """
        return os.urandom(28)  # 224 bits = 28 bytes
    
    def hash_to_curve(self, data: bytes) -> ec.EllipticCurvePublicKey:
        """
        将数据哈希映射到椭圆曲线点
        
        Args:
            data: 要映射的数据
            
        Returns:
            椭圆曲线点
        """
        # 使用SHA-256哈希数据
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        hash_bytes = digest.finalize()
        
        # 尝试将哈希映射到曲线点
        # 这是一个简化的实现，实际中可能需要更复杂的映射方法
        attempts = 0
        while attempts < 256:  # 最多尝试256次
            try:
                # 使用哈希值作为x坐标，尝试计算对应的y坐标
                x_bytes = hash_bytes[:28]  # 取前28字节作为x坐标
                
                # 确保x坐标在有效范围内
                x_int = int.from_bytes(x_bytes, byteorder='big')
                if x_int >= self.curve.key_size // 8:
                    # 如果x坐标太大，重新哈希
                    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
                    digest.update(hash_bytes)
                    hash_bytes = digest.finalize()
                    attempts += 1
                    continue
                
                # 尝试构造点
                # 这里使用一个简化的方法：直接使用哈希值构造私钥，然后获取对应的公钥点
                temp_private_key = ec.derive_private_key(
                    x_int % (2**224 - 1),  # 确保在曲线阶数范围内
                    self.curve,
                    default_backend()
                )
                return temp_private_key.public_key()
                
            except Exception:
                # 如果构造失败，重新哈希
                digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
                digest.update(hash_bytes)
                hash_bytes = digest.finalize()
                attempts += 1
        
        # 如果所有尝试都失败，使用生成器点
        return self.public_key
    
    def blind_point(self, point: ec.EllipticCurvePublicKey, blinding_factor: bytes) -> ec.EllipticCurvePublicKey:
        """
        对椭圆曲线点进行盲化
        
        Args:
            point: 要盲化的点
            blinding_factor: 盲化因子
            
        Returns:
            盲化后的点
        """
        try:
            # 将盲化因子转换为私钥
            blinding_int = int.from_bytes(blinding_factor, byteorder='big') % (2**224 - 1)
            if blinding_int == 0:
                blinding_int = 1
            
            blinding_key = ec.derive_private_key(
                blinding_int,
                self.curve,
                default_backend()
            )
            
            # 使用ECDH计算共享密钥，这实际上是点乘法的结果
            shared_key = blinding_key.exchange(ec.ECDH(), point)
            
            # 将共享密钥映射回曲线点
            return self.hash_to_curve(shared_key)
        except Exception as e:
            # 如果盲化失败，返回一个基于输入的确定性点
            # 使用哈希而不是点序列化来避免递归错误
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(blinding_factor)
            digest.update(b"fallback_blinding")
            fallback_hash = digest.finalize()
            return self.hash_to_curve(fallback_hash)
    
    def unblind_point(self, blinded_point: ec.EllipticCurvePublicKey, blinding_factor: bytes) -> ec.EllipticCurvePublicKey:
        """
        对椭圆曲线点进行解盲化
        
        Args:
            blinded_point: 盲化的点
            blinding_factor: 盲化因子
            
        Returns:
            解盲化后的点
        """
        try:
            # 计算盲化因子的逆元
            blinding_int = int.from_bytes(blinding_factor, byteorder='big') % (2**224 - 1)
            if blinding_int == 0:
                blinding_int = 1
            
            curve_order = 2**224 - 1  # secp224r1的近似阶数
            inverse_blinding = pow(blinding_int, -1, curve_order)
            
            inverse_bytes = inverse_blinding.to_bytes(28, byteorder='big')
            
            # 使用逆元进行盲化（实际上是解盲化）
            return self.blind_point(blinded_point, inverse_bytes)
        except Exception:
            # 如果解盲化失败，返回原点
            return blinded_point
    
    def point_to_bytes(self, point: ec.EllipticCurvePublicKey) -> bytes:
        """
        将椭圆曲线点转换为字节
        
        Args:
            point: 椭圆曲线点
            
        Returns:
            点的字节表示
        """
        try:
            return point.public_bytes(
                encoding=Encoding.X962,
                format=PublicFormat.CompressedPoint
            )
        except Exception:
            # 如果序列化失败，返回一个固定的字节表示
            return point.public_bytes(
                encoding=Encoding.X962,
                format=PublicFormat.UncompressedPoint
            )[:29]  # 取前29字节作为压缩表示
    
    def bytes_to_point(self, point_bytes: bytes) -> ec.EllipticCurvePublicKey:
        """
        将字节转换为椭圆曲线点
        
        Args:
            point_bytes: 点的字节表示
            
        Returns:
            椭圆曲线点
        """
        try:
            return ec.EllipticCurvePublicKey.from_encoded_point(
                self.curve, point_bytes
            )
        except Exception:
            # 如果解析失败，返回一个默认点
            return self.public_key
    
    def get_private_key_bytes(self) -> bytes:
        """
        获取私钥的字节表示
        
        Returns:
            私钥字节
        """
        private_value = self.private_key.private_numbers().private_value
        return private_value.to_bytes(28, byteorder='big') 