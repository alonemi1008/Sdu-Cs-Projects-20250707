import os
import pickle
import json
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from ..utils.constants import SHARD_COUNT, SHARD_PREFIX_LENGTH
from ..crypto.argon2_hash import Argon2Hasher


class ShardManager:
    """
    分片管理器，负责管理泄露数据库的分片存储和检索
    """
    
    def __init__(self, storage_path: str = "shards"):
        """
        初始化分片管理器
        
        Args:
            storage_path: 分片存储路径
        """
        self.storage_path = storage_path
        self.hasher = Argon2Hasher()
        self.shards: Dict[int, List[bytes]] = defaultdict(list)
        self.blinded_shards: Dict[int, List[bytes]] = defaultdict(list)
        
        # 创建存储目录
        os.makedirs(storage_path, exist_ok=True)
        
        # 加载现有分片
        self._load_shards()
    
    def add_credential(self, credential_hash: bytes, blinded_hash: bytes):
        """
        添加凭证到对应分片
        
        Args:
            credential_hash: 原始凭证哈希
            blinded_hash: 盲化后的凭证哈希
        """
        # 获取分片索引
        shard_index = self.hasher.get_shard_index(credential_hash)
        
        # 添加到对应分片
        if credential_hash not in self.shards[shard_index]:
            self.shards[shard_index].append(credential_hash)
            self.blinded_shards[shard_index].append(blinded_hash)
    
    def get_shard_data(self, shard_prefix: bytes) -> List[bytes]:
        """
        获取指定分片的原始数据
        
        Args:
            shard_prefix: 分片前缀
            
        Returns:
            分片中的所有原始凭证哈希
        """
        shard_index = int.from_bytes(shard_prefix, byteorder='big')
        return self.shards.get(shard_index, [])
    
    def get_blinded_shard_data(self, shard_prefix: bytes) -> List[bytes]:
        """
        获取指定分片的盲化数据
        
        Args:
            shard_prefix: 分片前缀
            
        Returns:
            分片中的所有盲化凭证哈希
        """
        shard_index = int.from_bytes(shard_prefix, byteorder='big')
        return self.blinded_shards.get(shard_index, [])
    
    def get_shard_statistics(self) -> Dict[str, int]:
        """
        获取分片统计信息
        
        Returns:
            分片统计信息
        """
        total_credentials = sum(len(shard) for shard in self.shards.values())
        non_empty_shards = sum(1 for shard in self.shards.values() if len(shard) > 0)
        
        return {
            "total_credentials": total_credentials,
            "total_shards": SHARD_COUNT,
            "non_empty_shards": non_empty_shards,
            "average_shard_size": total_credentials / non_empty_shards if non_empty_shards > 0 else 0,
            "max_shard_size": max(len(shard) for shard in self.shards.values()) if self.shards else 0
        }
    
    def save_shards(self):
        """
        保存分片到磁盘
        """
        try:
            # 保存原始分片
            shards_file = os.path.join(self.storage_path, "shards.pkl")
            with open(shards_file, 'wb') as f:
                pickle.dump(dict(self.shards), f)
            
            # 保存盲化分片
            blinded_shards_file = os.path.join(self.storage_path, "blinded_shards.pkl")
            with open(blinded_shards_file, 'wb') as f:
                pickle.dump(dict(self.blinded_shards), f)
            
            # 保存统计信息
            stats_file = os.path.join(self.storage_path, "statistics.json")
            with open(stats_file, 'w') as f:
                json.dump(self.get_shard_statistics(), f, indent=2)
                
        except Exception as e:
            raise RuntimeError(f"保存分片失败: {e}")
    
    def _load_shards(self):
        """
        从磁盘加载分片
        """
        try:
            # 加载原始分片
            shards_file = os.path.join(self.storage_path, "shards.pkl")
            if os.path.exists(shards_file):
                with open(shards_file, 'rb') as f:
                    loaded_shards = pickle.load(f)
                    self.shards = defaultdict(list, loaded_shards)
            
            # 加载盲化分片
            blinded_shards_file = os.path.join(self.storage_path, "blinded_shards.pkl")
            if os.path.exists(blinded_shards_file):
                with open(blinded_shards_file, 'rb') as f:
                    loaded_blinded_shards = pickle.load(f)
                    self.blinded_shards = defaultdict(list, loaded_blinded_shards)
                    
        except Exception as e:
            print(f"警告: 加载分片失败: {e}")
            # 如果加载失败，使用空的分片
            self.shards = defaultdict(list)
            self.blinded_shards = defaultdict(list)
    
    def clear_all_shards(self):
        """
        清空所有分片数据
        """
        self.shards.clear()
        self.blinded_shards.clear()
        
        # 删除磁盘文件
        for filename in ["shards.pkl", "blinded_shards.pkl", "statistics.json"]:
            filepath = os.path.join(self.storage_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
    
    def get_shard_size_distribution(self) -> Dict[str, int]:
        """
        获取分片大小分布
        
        Returns:
            分片大小分布统计
        """
        size_ranges = {
            "0": 0,
            "1-10": 0,
            "11-50": 0,
            "51-100": 0,
            "101-500": 0,
            "501-1000": 0,
            "1000+": 0
        }
        
        for shard in self.shards.values():
            size = len(shard)
            if size == 0:
                size_ranges["0"] += 1
            elif size <= 10:
                size_ranges["1-10"] += 1
            elif size <= 50:
                size_ranges["11-50"] += 1
            elif size <= 100:
                size_ranges["51-100"] += 1
            elif size <= 500:
                size_ranges["101-500"] += 1
            elif size <= 1000:
                size_ranges["501-1000"] += 1
            else:
                size_ranges["1000+"] += 1
        
        return size_ranges
    
    def export_shard_info(self, output_file: str):
        """
        导出分片信息到文件
        
        Args:
            output_file: 输出文件路径
        """
        info = {
            "statistics": self.get_shard_statistics(),
            "size_distribution": self.get_shard_size_distribution(),
            "shard_details": {
                str(index): len(shard) 
                for index, shard in self.shards.items() 
                if len(shard) > 0
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(info, f, indent=2) 