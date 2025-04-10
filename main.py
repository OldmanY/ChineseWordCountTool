import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os
from tkinterdnd2 import TkinterDnD, DND_FILES

class TextAnalyzer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("文本统计工具 v2.2-www.ctntc.com制作开源")
        self.geometry("900x650")
        self.minsize(900, 650)  # 设置最小窗口尺寸
        
        # 状态栏变量
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪 | 可直接粘贴或拖放文件")
        
        # 文件统计相关
        self.file_stats = []
        self.current_file_index = 0
        
        # 构建界面
        self._setup_ui()

    def _setup_ui(self):
        """界面布局"""
        # 主文本框（支持直接粘贴）
        self.text_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=('Microsoft YaHei', 12),
            padx=15,
            pady=15,
            undo=True
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.drop_target_register(DND_FILES)
        self.text_area.dnd_bind('<<Drop>>', self._handle_drop)

        # 操作按钮区
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="开始统计", command=self.analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空内容", command=self.clear).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="使用说明", command=self.show_help).pack(side=tk.LEFT, padx=5)
        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(btn_frame, text="打开文件", command=self._safe_open_file).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="打开文件夹", command=self._safe_open_folder).pack(side=tk.LEFT, padx=5)

        # 统计结果区（分左右两栏）
        result_frame = ttk.Frame(self)
        result_frame.pack(fill=tk.BOTH, expand=False, pady=(0,5))

        # 左侧：当前内容统计
        left_frame = ttk.LabelFrame(result_frame, text="当前统计", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.result_labels = {
            'chinese': ttk.Label(left_frame, text="中文字符: 0"),
            'punct': ttk.Label(left_frame, text="中文标点: 0"),
            'english': ttk.Label(left_frame, text="英文单词: 0"),
            'number': ttk.Label(left_frame, text="数字: 0"),
            'total': ttk.Label(left_frame, text="总字符数: 0")
        }
        
        for label in self.result_labels.values():
            label.pack(anchor="w", pady=2)

        # 右侧：文件统计导航
        right_frame = ttk.LabelFrame(result_frame, text="文件统计", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))
        
        self.file_nav_frame = ttk.Frame(right_frame)
        self.file_nav_frame.pack()
        
        ttk.Button(self.file_nav_frame, text="↑", width=3, 
                  command=lambda: self._change_file(-1)).pack(side=tk.LEFT)
        ttk.Button(self.file_nav_frame, text="↓", width=3, 
                  command=lambda: self._change_file(1)).pack(side=tk.LEFT)
        
        self.file_name_label = ttk.Label(right_frame, text="无文件")
        self.file_name_label.pack(pady=(5,0))
        
        self.file_stats_labels = {
            'chinese': ttk.Label(right_frame, text="中文字符: 0"),
            'punct': ttk.Label(right_frame, text="中文标点: 0"),
            'total': ttk.Label(right_frame, text="总字符数: 0")
        }
        
        for label in self.file_stats_labels.values():
            label.pack(anchor="w", pady=2)

        # 状态栏
        status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            padding=(5,2)
        )
        status_bar.pack(fill=tk.X, padx=5, pady=(0,5))

        # 初始显示帮助
        self.show_help()

    def _change_file(self, delta):
        """切换显示的文件统计结果"""
        if not self.file_stats:
            return
            
        self.current_file_index = (self.current_file_index + delta) % len(self.file_stats)
        self._display_file_stats()

    def _display_file_stats(self):
        """显示当前文件的统计结果"""
        stats = self.file_stats[self.current_file_index]
        self.file_name_label.config(text=stats['name'])
        self.file_stats_labels['chinese'].config(text=f"中文字符: {stats['chinese']}")
        self.file_stats_labels['punct'].config(text=f"中文标点: {stats['punct']}")
        self.file_stats_labels['total'].config(text=f"总字符数: {stats['total']}")

    def _safe_open_file(self):
        """安全打开文件"""
        self.after(10, self.open_file)
        
    def _safe_open_folder(self):
        """安全打开文件夹"""
        self.after(10, self.open_folder)

    def analyze(self):
        """执行统计"""
        text = self.text_area.get("1.0", tk.END)
        if not text.strip():
            self.status_var.set("警告 | 没有可统计的内容")
            return
        
        try:
            # 统计规则（过滤文件标记行）
            clean_text = re.sub(r'^=== .+ ===\n', '', text, flags=re.MULTILINE)
            clean_text_no_space = clean_text.replace('\n', '').replace(' ', '')
            
            # 核心统计
            counts = {
                'chinese': len(re.findall(r'[\u4e00-\u9fa5]', clean_text)),
                'punct': len(re.findall(r'[，。！？、；：“”‘’（）【】《》]', clean_text)),
                'english': len(re.findall(r'\b[a-zA-Z]+\b', clean_text)),
                'number': len(re.findall(r'\d+', clean_text)),
                'total': len(clean_text_no_space)
            }
            
            # 更新结果
            self.result_labels['chinese'].config(text=f"中文字符: {counts['chinese']}")
            self.result_labels['punct'].config(text=f"中文标点: {counts['punct']}")
            self.result_labels['english'].config(text=f"英文单词: {counts['english']}")
            self.result_labels['number'].config(text=f"数字: {counts['number']}")
            self.result_labels['total'].config(text=f"总字符数: {counts['total']}")
            
            # 修复f-string错误：先计算含空格字符数
            total_with_space = len(text.replace('\n', ''))
            self.status_var.set(f"统计完成 | 总字符: {counts['total']} (含空格: {total_with_space})")
            
        except Exception as e:
            self.status_var.set(f"错误 | 统计失败: {str(e)}")

    def clear(self):
        """清空所有内容"""
        self.text_area.delete("1.0", tk.END)
        for label in self.result_labels.values():
            label.config(text=label.cget("text").split(":")[0] + ": 0")
        
        self.file_stats = []
        self.current_file_index = 0
        self.file_name_label.config(text="无文件")
        for label in self.file_stats_labels.values():
            label.config(text=label.cget("text").split(":")[0] + ": 0")
        
        self.status_var.set("已清空 | 准备就绪")

    def open_file(self):
        """打开单个文件"""
        try:
            filepath = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt")])
            if filepath:
                self._load_file(filepath)
        except Exception as e:
            self.status_var.set(f"错误 | 文件打开失败: {str(e)}")

    def open_folder(self):
        """打开文件夹并单独统计每个文件"""
        try:
            folder = filedialog.askdirectory()
            if folder:
                self.clear()
                self.file_stats = []
                
                for filename in sorted(os.listdir(folder)):
                    if filename.lower().endswith('.txt'):
                        try:
                            with open(os.path.join(folder, filename), 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # 添加到主文本框（带文件标记）
                            self.text_area.insert(tk.END, f"\n\n=== {filename} ===\n{content}")
                            
                            # 单独统计每个文件
                            clean_text = re.sub(r'^=== .+ ===\n', '', content, flags=re.MULTILINE)
                            counts = {
                                'name': filename,
                                'chinese': len(re.findall(r'[\u4e00-\u9fa5]', clean_text)),
                                'punct': len(re.findall(r'[，。！？、；：“”‘’（）【】《》]', clean_text)),
                                'total': len(clean_text.replace('\n', '').replace(' ', ''))
                            }
                            self.file_stats.append(counts)
                            
                        except Exception as e:
                            self.status_var.set(f"警告 | 跳过文件 {filename}: {str(e)}")
                
                if self.file_stats:
                    self.current_file_index = 0
                    self._display_file_stats()
                    self.status_var.set(f"已加载 {len(self.file_stats)} 个文件 | 使用↑↓按钮查看详情")
                else:
                    self.status_var.set("警告 | 未找到有效TXT文件")
                    
        except Exception as e:
            self.status_var.set(f"错误 | 文件夹打开失败: {str(e)}")

    def _load_file(self, path):
        """加载文件内容"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.clear()
            self.text_area.insert(tk.END, f"=== {os.path.basename(path)} ===\n{content}")
            self.status_var.set(f"已加载: {os.path.basename(path)}")
            self.analyze()
        except Exception as e:
            self.status_var.set(f"错误 | 读取失败: {str(e)}")

    def _handle_drop(self, event):
        """处理拖放文件"""
        try:
            files = [f.strip('{}') for f in event.data.split()] if isinstance(event.data, str) else [event.data]
            loaded = 0
            for f in files:
                if f.lower().endswith('.txt'):
                    self._load_file(f)
                    loaded += 1
            self.status_var.set(f"已加载 {loaded} 个文件" if loaded else "警告 | 未找到TXT文件")
        except Exception as e:
            self.status_var.set(f"错误 | 文件拖放失败: {str(e)}")

    def show_help(self):
        """显示使用说明"""
        help_text = """=== 使用说明 ===

【基本操作】
1. 直接粘贴文本到编辑区
2. 拖放TXT文件到窗口
3. 点击"开始统计"按钮

【文件操作】
• 打开文件：加载单个TXT文件
• 打开文件夹：批量加载并统计所有TXT文件

【统计说明】
• 总字符数 = 所有非空格字符
• 中文标点包含：，。！？、；：“”‘’（）【】《》
• 文件统计可通过↑↓按钮切换查看

【注意事项】
• 自动过滤文件名标记行（=== 文件名 ===）
• 拖放TXT文件到窗口一次只支持单个TXT文本
• 窗口大小可自由调整
• 当前为最小窗口-向下调整可以显示完整统计窗口和软件状态栏
• 由于选取的文件会标上文件名，这样会增加空格，所以空格总字符只作为参考，并不准确。
• 小工具主要功能够自己用了，所以不做调整了，需要调整的自己调整。macOS不知道如何。
"""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, help_text)
        self.status_var.set("提示 | 已显示使用说明")

if __name__ == "__main__":
    app = TextAnalyzer()
    app.mainloop()