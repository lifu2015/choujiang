"""
抽奖工具类，提供通用的功能
"""
import json
import os
from typing import List, Dict, Any

def load_employees() -> List[Dict[str, Any]]:
    """加载员工数据"""
    with open('../employees.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['employees']

def load_prize_rules() -> Dict[str, Any]:
    """加载奖项规则"""
    with open('../prize_rules.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_result(algorithm_name: str, winners: Dict[str, List[Dict[str, Any]]]):
    """保存抽奖结果"""
    result = {
        'algorithm': algorithm_name,
        'winners': winners,
        'timestamp': datetime.now().isoformat()
    }
    
    # 确保结果目录存在
    os.makedirs('../results', exist_ok=True)
    
    # 保存结果
    filename = f'../results/result_{algorithm_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return filename
