"""
抽奖程序主文件
实现抽奖界面和抽奖流程
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
from PIL import Image, ImageTk
from algorithms.crypto_random import CryptoRandomDraw
from algorithms.simple_random import SimpleRandomDraw
from algorithms.entropy_random import EntropyRandomDraw

class LotteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TechVision Solutions 员工抽奖系统")
        self.root.geometry("1024x768")  # 增加窗口大小
        
        # 设置整体样式
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Microsoft YaHei', 24, 'bold'))
        style.configure('Prize.TLabel', font=('Microsoft YaHei', 18))
        style.configure('Winner.TLabel', font=('Microsoft YaHei', 16))
        style.configure('TButton', font=('Microsoft YaHei', 12))
        
        # 加载配置
        self.load_configs()
        
        # 初始化UI
        self.setup_ui()
        
        # 初始化抽奖状态
        self.current_prize_index = 0
        self.winners = {}
        self.available_employees = self.employees.copy()
        
    def load_configs(self):
        """加载所有配置文件"""
        # 加载员工信息
        with open('employees.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.employees = data['employees']
            
        # 加载奖项规则
        with open('prize_rules.json', 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
            
        # 加载奖品信息
        with open('prize_items.json', 'r', encoding='utf-8') as f:
            self.prizes = json.load(f)
            
        # 获取奖项列表
        self.prize_levels = [prize['level'] for prize in self.rules['prizes']]
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架，使用权重使其能够自适应调整
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # 标题 - 使用新的样式
        title_label = ttk.Label(main_frame, text="TechVision Solutions 员工抽奖系统", 
                              style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=20)
        
        # 创建内容框架
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky='nsew')
        content_frame.grid_columnconfigure(0, weight=1)
        
        # 当前奖项信息 - 使用新的样式
        self.prize_label = ttk.Label(content_frame, text="准备开始抽奖", 
                                   style='Prize.TLabel')
        self.prize_label.grid(row=0, column=0, pady=15)
        
        # 奖品图片显示区域
        self.image_label = ttk.Label(content_frame)
        self.image_label.grid(row=1, column=0, pady=15)
        
        # 中奖者显示区域 - 使用新的样式
        self.winner_label = ttk.Label(content_frame, text="", 
                                    style='Winner.TLabel', wraplength=800)
        self.winner_label.grid(row=2, column=0, pady=15)
        
        # 算法选择
        algo_frame = ttk.LabelFrame(content_frame, text="选择抽奖算法", padding="10")
        algo_frame.grid(row=3, column=0, pady=15, sticky='ew')
        algo_frame.grid_columnconfigure(0, weight=1)
        
        algo_buttons_frame = ttk.Frame(algo_frame)
        algo_buttons_frame.grid(row=0, column=0)
        
        self.algo_var = tk.StringVar(value="crypto")
        ttk.Radiobutton(algo_buttons_frame, text="密码学安全随机", 
                       variable=self.algo_var, value="crypto").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(algo_buttons_frame, text="简单随机", 
                       variable=self.algo_var, value="simple").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(algo_buttons_frame, text="混合熵源随机", 
                       variable=self.algo_var, value="entropy").pack(side=tk.LEFT, padx=20)
        
        # 控制按钮
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=4, column=0, pady=20)
        
        self.draw_button = ttk.Button(button_frame, text="开始抽奖", 
                                    command=self.draw_prize, width=15)
        self.draw_button.pack(side=tk.LEFT, padx=20)
        
        self.save_button = ttk.Button(button_frame, text="保存结果", 
                                    command=self.save_results, state=tk.DISABLED, width=15)
        self.save_button.pack(side=tk.LEFT, padx=20)
        
        # 结果显示区域 - 添加滚动条
        result_frame = ttk.LabelFrame(content_frame, text="抽奖结果", padding="10")
        result_frame.grid(row=5, column=0, pady=15, sticky='ew')
        result_frame.grid_columnconfigure(0, weight=1)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky='ew')
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, height=10, width=70, 
                                 font=('Microsoft YaHei', 12))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", 
                                command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky='ew', padx=(5, 0))
        scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 5))
        
    def load_prize_image(self, prize_level):
        """加载奖品图片"""
        try:
            # 获取对应奖项的图片文件名
            prize_info = next(p for p in self.prizes['prizes'] 
                            if p['level'] == prize_level)
            image_path = os.path.join('goods', prize_info['item']['image'])
            
            # 加载并调整图片大小
            image = Image.open(image_path)
            # 调整图片大小为更合适的尺寸
            image = image.resize((400, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # 保持引用
        except Exception as e:
            print(f"加载图片失败: {e}")
            self.image_label.configure(image='')
            
    def get_drawer(self):
        """根据选择返回对应的抽奖器"""
        algo_type = self.algo_var.get()
        if algo_type == "crypto":
            return CryptoRandomDraw()
        elif algo_type == "simple":
            return SimpleRandomDraw()
        else:
            return EntropyRandomDraw()
            
    def draw_prize(self):
        """执行抽奖"""
        if self.current_prize_index >= len(self.prize_levels):
            messagebox.showinfo("完成", "所有奖项已抽完！")
            return
            
        # 获取当前奖项
        current_prize = self.prize_levels[self.current_prize_index]
        prize_config = next(p for p in self.rules['prizes'] 
                          if p['level'] == current_prize)
        
        # 更新界面显示
        self.prize_label.configure(text=f"正在抽取: {current_prize}")
        self.load_prize_image(current_prize)
        
        # 获取抽奖器并执行抽奖
        drawer = self.get_drawer()
        drawer.available_employees = self.available_employees
        
        # 抽取获奖者
        if prize_config['winners'] == "remaining":
            # 鼓励奖：所有剩余员工
            winners = self.available_employees
            self.available_employees = []
        else:
            winners = []
            for _ in range(prize_config['winners']):
                if self.available_employees:
                    winner = drawer.entropy_choice(self.available_employees)
                    winners.append(winner)
                    self.available_employees.remove(winner)
        
        # 保存结果
        self.winners[current_prize] = winners
        
        # 更新显示
        winner_names = [w['name'] for w in winners]
        self.winner_label.configure(text=f"获奖者: {', '.join(winner_names)}")
        
        # 更新结果文本区域
        self.result_text.insert(tk.END, 
                              f"\n{current_prize}获奖者：{', '.join(winner_names)}")
        self.result_text.see(tk.END)
        
        # 移动到下一个奖项
        self.current_prize_index += 1
        
        # 如果所有奖项都抽完了，启用保存按钮
        if self.current_prize_index >= len(self.prize_levels):
            self.draw_button.configure(state=tk.DISABLED)
            self.save_button.configure(state=tk.NORMAL)
            messagebox.showinfo("完成", "所有奖项已抽完！")
            
    def save_results(self):
        """保存抽奖结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'results/lottery_result_{timestamp}.json'
        
        # 确保结果目录存在
        os.makedirs('results', exist_ok=True)
        
        # 准备保存的数据
        result_data = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': self.algo_var.get(),
            'winners': self.winners
        }
        
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
            
        messagebox.showinfo("成功", f"结果已保存至：{filename}")

def main():
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
