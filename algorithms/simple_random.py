"""
简单随机算法
使用 Python 内置的 random 模块实现基础随机抽取
优点：实现简单，速度快
缺点：依赖于伪随机数生成器，理论上可能被预测
"""
import random
from datetime import datetime
from typing import List, Dict, Any
import os
import json

class SimpleRandomDraw:
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
            
    def entropy_choice(self, items: list) -> Any:
        """随机选择一个元素"""
        if not items:
            return None
        return random.choice(items)
        
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
                        # 随机选择一名员工
                        winner = random.choice(self.available_employees)
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
    # 设置随机种子（使用当前时间戳）
    random.seed(datetime.now().timestamp())
    
    # 创建抽奖器并执行抽奖
    drawer = SimpleRandomDraw()
    winners = drawer.draw()
    
    # 保存结果
    result_file = drawer.save_result(winners)
    return result_file

if __name__ == '__main__':
    result_file = run_draw()
    print(f"抽奖完成，结果已保存至：{result_file}")
