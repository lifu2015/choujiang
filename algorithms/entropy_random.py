"""
混合熵源随机算法
结合多个随机源（系统时间、硬件事件、密码学随机等）来生成随机数
优点：通过多个熵源提供更好的随机性，且可以在抽奖现场收集额外的随机性（如声音）
缺点：实现相对复杂，需要更多系统资源
"""
import time
import hashlib
import secrets
from datetime import datetime
from typing import List, Dict, Any
import os
import json

class EntropyRandomDraw:
    def __init__(self):
        self.employees = self.load_employees()
        self.rules = self.load_prize_rules()
        self.available_employees = self.employees.copy()
        self.entropy_pool = []
    
    def load_employees(self) -> List[Dict[str, Any]]:
        """加载员工数据"""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'employees.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['employees']

    def load_prize_rules(self) -> Dict[str, Any]:
        """加载奖项规则"""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prize_rules.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def collect_entropy(self) -> bytes:
        """收集系统熵源"""
        entropy_sources = [
            str(time.time()).encode(),  # 当前时间戳
            str(time.process_time()).encode(),  # CPU时间
            secrets.token_bytes(32),  # 密码学随机数
            str(id(object())).encode(),  # 对象ID（内存地址）
        ]
        
        # 合并所有熵源
        combined = b''.join(entropy_sources)
        # 使用SHA-256生成最终的熵值
        return hashlib.sha256(combined).digest()
    
    def random_index(self, max_value: int) -> int:
        """生成随机索引"""
        if max_value <= 0:
            return 0
            
        # 收集新的熵
        entropy = self.collect_entropy()
        # 转换为整数并取模
        value = int.from_bytes(entropy, 'big')
        return value % max_value
    
    def entropy_choice(self, items: list) -> Any:
        """使用熵池进行随机选择"""
        if not items:
            return None
        index = self.random_index(len(items))
        return items[index]
    
    def draw(self) -> Dict[str, List[Dict[str, Any]]]:
        """执行抽奖"""
        winners = {}
        
        # 获取奖项配置
        prize_configs = self.rules['prizes']
        
        # 按奖项等级从高到低抽取
        for prize in prize_configs:
            level = prize['level']
            num_winners = prize['winners']
            
            if num_winners == "remaining":
                # 鼓励奖：所有剩余员工
                winners[level] = self.available_employees
                self.available_employees = []
            else:
                # 抽取指定数量的获奖者
                level_winners = []
                for _ in range(num_winners):
                    if self.available_employees:
                        # 使用熵池进行随机选择
                        winner = self.entropy_choice(self.available_employees)
                        level_winners.append(winner)
                        # 从可用名单中移除
                        self.available_employees.remove(winner)
                winners[level] = level_winners
        
        return winners

    def save_result(self, result: Dict[str, List[Dict[str, Any]]]) -> str:
        """保存结果"""
        result_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'result.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
        return result_file

def run_draw():
    """运行抽奖"""
    # 创建抽奖器并执行抽奖
    drawer = EntropyRandomDraw()
    winners = drawer.draw()
    
    # 保存结果
    result_file = drawer.save_result(winners)
    return result_file

if __name__ == '__main__':
    result_file = run_draw()
    print(f"抽奖完成，结果已保存至：{result_file}")
