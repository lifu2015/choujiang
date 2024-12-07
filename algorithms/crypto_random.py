"""
密码学安全的随机算法
使用 secrets 模块实现更安全的随机抽取
优点：使用操作系统提供的密码学安全的随机源，更难预测
缺点：相对较慢，但对于抽奖场景影响不大
"""
import secrets
from datetime import datetime
from typing import List, Dict, Any
import sys
import os
import json

class CryptoRandomDraw:
    def __init__(self):
        self.employees = self.load_employees()
        self.rules = self.load_prize_rules()
        self.available_employees = self.employees.copy()
    
    def load_employees(self) -> List[Dict[str, Any]]:
        """加载员工数据"""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'employees.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['employees']

    def load_prize_rules(self) -> Dict[str, Any]:
        """加载奖项规则"""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prize_rules.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def secure_random_choice(self, items: list) -> Any:
        """使用密码学安全的方式随机选择一个元素"""
        if not items:
            return None
        return items[secrets.randbelow(len(items))]
    
    def entropy_choice(self, items: list) -> Any:
        """兼容性方法"""
        return self.secure_random_choice(items)
    
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
                        # 使用密码学安全的随机选择
                        winner = self.secure_random_choice(self.available_employees)
                        level_winners.append(winner)
                        # 从可用名单中移除
                        self.available_employees.remove(winner)
                winners[level] = level_winners
        
        return winners

    def save_result(self, result: Dict[str, List[Dict[str, Any]]]) -> str:
        """保存结果"""
        result_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'result.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        return result_file

def run_draw():
    """运行抽奖"""
    # 创建抽奖器并执行抽奖
    drawer = CryptoRandomDraw()
    winners = drawer.draw()
    
    # 保存结果
    result_file = drawer.save_result(winners)
    return result_file

if __name__ == '__main__':
    result_file = run_draw()
    print(f"抽奖完成，结果已保存至：{result_file}")
