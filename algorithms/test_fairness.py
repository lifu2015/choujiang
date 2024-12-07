"""
随机算法公平性测试
通过多次运行不同的随机算法，统计每个员工获得不同奖项的概率分布
"""
import json
from collections import defaultdict
from typing import Dict, List
from simple_random import SimpleRandomDraw
from crypto_random import CryptoRandomDraw
from entropy_random import EntropyRandomDraw

def run_fairness_test(num_iterations: int = 1000):
    """
    运行公平性测试
    
    Args:
        num_iterations: 测试迭代次数
    """
    algorithms = {
        'simple_random': SimpleRandomDraw,
        'crypto_random': CryptoRandomDraw,
        'entropy_random': EntropyRandomDraw
    }
    
    results = {}
    
    for algo_name, algo_class in algorithms.items():
        print(f"\n测试算法: {algo_name}")
        
        # 统计每个员工获得每个奖项的次数
        employee_stats = defaultdict(lambda: defaultdict(int))
        
        for i in range(num_iterations):
            if i % 100 == 0:
                print(f"进度: {i}/{num_iterations}")
                
            drawer = algo_class()
            winners = drawer.draw()
            
            # 统计本次抽奖结果
            for prize_level, prize_winners in winners.items():
                for winner in prize_winners:
                    employee_stats[winner['name']][prize_level] += 1
        
        # 计算概率分布
        probability_distribution = {}
        for emp_name, prize_counts in employee_stats.items():
            probability_distribution[emp_name] = {
                prize_level: count/num_iterations 
                for prize_level, count in prize_counts.items()
            }
        
        results[algo_name] = probability_distribution
    
    # 保存测试结果
    with open('../results/fairness_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results

def analyze_fairness(results: Dict[str, Dict]):
    """分析公平性测试结果"""
    for algo_name, distribution in results.items():
        print(f"\n算法 {algo_name} 的分析结果：")
        
        # 计算每个奖项的平均中奖概率
        prize_probabilities = defaultdict(list)
        for emp_stats in distribution.values():
            for prize, prob in emp_stats.items():
                prize_probabilities[prize].append(prob)
        
        # 输出统计信息
        for prize, probs in prize_probabilities.items():
            avg_prob = sum(probs) / len(probs)
            max_prob = max(probs)
            min_prob = min(probs)
            std_dev = (sum((p - avg_prob) ** 2 for p in probs) / len(probs)) ** 0.5
            
            print(f"\n{prize}:")
            print(f"  平均概率: {avg_prob:.4f}")
            print(f"  最大概率: {max_prob:.4f}")
            print(f"  最小概率: {min_prob:.4f}")
            print(f"  标准差: {std_dev:.4f}")
            print(f"  概率差异: {(max_prob - min_prob):.4f}")

if __name__ == '__main__':
    print("开始公平性测试...")
    results = run_fairness_test(1000)  # 运行1000次测试
    
    print("\n分析测试结果...")
    analyze_fairness(results)
    
    print("\n测试完成，详细结果已保存至 results/fairness_test_results.json")
