#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib
import itertools
from gmssl import sm3
import threading
import os
import re
from file_decryptor import FileDecryptor
from gpu_utils import get_gpu_status, detect_gpu

class AdvancedPasswordGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("高级密码生成器 - 完整版")
        self.root.geometry("1800x800")  # 调整窗口大小为1800x800以适应更宽的中间框架
        self.root.resizable(True, True)
        
        # 设置窗口居中
        self.center_window()
        
        # 设置样式
        self.setup_styles()
        
        # 创建主框架和滚动区域
        self.create_scrollable_frame()
        
        # 初始化前缀和后缀列表
        self.prefix_frames = []
        self.suffix_frames = []
        self.prefix_vars = []
        self.suffix_vars = []
        
        self.create_widgets()
    
    def center_window(self):
        """使窗口在屏幕居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_scrollable_frame(self):
        """创建可滚动的框架以显示全部内容"""
        # 创建主框架（三列布局）
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧框架（密码生成功能）- 宽度调整为40%
        left_frame = ttk.Frame(main_container, width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        # 中间框架（输出设置）- 宽度调整为40%
        middle_frame = ttk.Frame(main_container, width=450)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        middle_frame.pack_propagate(False)
        
        # 右侧框架（文件解密功能+说明）- 宽度调整为30%
        right_frame = ttk.Frame(main_container, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        right_frame.pack_propagate(False)
        
        # 在左侧框架中创建画布和滚动条（密码生成功能）
        canvas = tk.Canvas(left_frame, bg='white')
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 在中间框架创建输出设置区域
        self.create_output_section(middle_frame)
        
        # 在右侧框架创建文件解密功能和说明
        self.create_decrypt_section(right_frame)
        
        # 配置网格权重
        self.scrollable_frame.columnconfigure(1, weight=1)
    
    def create_output_section(self, parent_frame):
        """创建中间输出设置区域"""
        # 输出类型选择
        ttk.Label(parent_frame, text="输出设置", 
                 style='Header.TLabel', font=('Arial', 14, 'bold')).pack(pady=(10, 20))
        
        # 输出类型选择
        ttk.Label(parent_frame, text="输出类型:", style='Header.TLabel').pack(pady=(0, 10))
        
        self.output_type_var = tk.StringVar(value="hash")
        output_frame = ttk.Frame(parent_frame)
        output_frame.pack(pady=(0, 10))
        
        ttk.Radiobutton(output_frame, text="哈希值", variable=self.output_type_var, 
                       value="hash").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(output_frame, text="原始密码", variable=self.output_type_var, 
                       value="original").pack(side=tk.LEFT)
        
        # 哈希算法选择
        ttk.Label(parent_frame, text="哈希算法:", style='Header.TLabel').pack(pady=(20, 10))
        
        self.hash_algo_var = tk.StringVar(value="MD5")
        hash_frame = ttk.Frame(parent_frame)
        hash_frame.pack(pady=(0, 10))
        
        hash_algos = ["MD5", "SHA1", "SHA256", "SM3"]
        for algo in hash_algos:
            ttk.Radiobutton(hash_frame, text=algo, variable=self.hash_algo_var, 
                           value=algo).pack(side=tk.LEFT, padx=(0, 15))
        
        # 哈希值提取设置
        ttk.Label(parent_frame, text="哈希值提取设置:", style='Header.TLabel').pack(pady=(20, 10))
        
        extract_frame = ttk.Frame(parent_frame)
        extract_frame.pack(pady=(0, 10))
        
        ttk.Label(extract_frame, text="起始位置:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_pos_var = tk.StringVar(value="0")
        ttk.Entry(extract_frame, textvariable=self.start_pos_var, width=10).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(extract_frame, text="提取长度:").pack(side=tk.LEFT, padx=(0, 5))
        self.segment_length_var = tk.StringVar(value="8")
        ttk.Entry(extract_frame, textvariable=self.segment_length_var, width=10).pack(side=tk.LEFT)
        
        # 输出文件设置
        ttk.Label(parent_frame, text="输出文件:", style='Header.TLabel').pack(pady=(20, 10))
        
        output_file_frame = ttk.Frame(parent_frame)
        output_file_frame.pack(pady=(0, 10))
        
        ttk.Label(output_file_frame, text="文件名:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_file_var = tk.StringVar(value="password_dict.txt")
        ttk.Entry(output_file_frame, textvariable=self.output_file_var, width=20).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(output_file_frame, text="浏览...", command=self.browse_output_file).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(output_file_frame, text="选择字典...", command=self.browse_dict_for_output).pack(side=tk.LEFT, padx=(5, 0))
        
        # 分隔线
        ttk.Separator(parent_frame, orient='horizontal').pack(fill='x', padx=10, pady=10)
        
        # 使用已有字典解密
        ttk.Label(parent_frame, text="使用已有字典:", style='Header.TLabel').pack(pady=(20, 10))
        
        existing_dict_frame = ttk.Frame(parent_frame)
        existing_dict_frame.pack(pady=(0, 20))
        
        ttk.Label(existing_dict_frame, text="字典文件:").pack(side=tk.LEFT, padx=(0, 5))
        self.existing_dict_var = tk.StringVar()
        ttk.Entry(existing_dict_frame, textvariable=self.existing_dict_var, width=20).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(existing_dict_frame, text="浏览...", command=self.browse_existing_dict).pack(side=tk.LEFT)
        ttk.Button(existing_dict_frame, text="使用此字典", command=self.use_existing_dict).pack(side=tk.LEFT, padx=(5, 0))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=20)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(parent_frame, textvariable=self.status_var).pack(pady=5)
        
        # 按钮
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="开始生成", command=self.start_generation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="停止", command=self.stop_generation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空所有", command=self.clear_all_fields).pack(side=tk.LEFT, padx=5)
    
    def create_decrypt_section(self, parent_frame):
        """创建右侧解密功能区域"""
        # 解密功能标题
        ttk.Label(parent_frame, text="文件解密功能", 
                 style='Header.TLabel', font=('Arial', 14, 'bold')).pack(pady=(10, 20))
        
        # GPU检测区域
        ttk.Label(parent_frame, text="GPU加速选项:", style='Header.TLabel').pack(pady=(0, 10))
        
        gpu_frame = ttk.Frame(parent_frame)
        gpu_frame.pack(pady=(0, 10))
        
        self.use_gpu_var = tk.BooleanVar(value=False)
        
        # 保存GPU复选框的引用
        self.use_gpu_checkbutton = ttk.Checkbutton(gpu_frame, text="使用GPU加速", variable=self.use_gpu_var, 
                       state='disabled')
        self.use_gpu_checkbutton.pack(side=tk.LEFT, padx=(0, 10))
        
        # GPU检测按钮
        ttk.Button(gpu_frame, text="检测显卡", command=self.detect_gpu_info).pack(side=tk.LEFT)
        
        # GPU状态显示
        self.gpu_status_var = tk.StringVar(value="点击'检测显卡'获取GPU信息")
        self.gpu_status_label = ttk.Label(parent_frame, textvariable=self.gpu_status_var, font=('Arial', 9), 
                 foreground='gray')
        self.gpu_status_label.pack(pady=(0, 10))
        
        # GPU检测进度条
        self.gpu_progress_var = tk.DoubleVar()
        self.gpu_progress_bar = ttk.Progressbar(parent_frame, variable=self.gpu_progress_var, 
                                              maximum=100, mode='indeterminate')
        self.gpu_progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.gpu_progress_bar.pack_forget()  # 初始隐藏
        
        # 加密文件选择
        ttk.Label(parent_frame, text="选择加密文件:", style='Header.TLabel').pack(pady=(0, 10))
        
        file_frame = ttk.Frame(parent_frame)
        file_frame.pack(pady=(0, 10))
        
        self.encrypted_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.encrypted_file_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="浏览...", command=self.browse_encrypted_file).pack(side=tk.LEFT)
        
        # 解密按钮
        decrypt_button_frame = ttk.Frame(parent_frame)
        decrypt_button_frame.pack(pady=20)
        
        ttk.Button(decrypt_button_frame, text="开始解密", command=self.start_decryption).pack(side=tk.LEFT, padx=5)
        ttk.Button(decrypt_button_frame, text="停止解密", command=self.stop_decryption).pack(side=tk.LEFT, padx=5)
        
        # 解密密码显示区域
        ttk.Label(parent_frame, text="解密密码:", style='Header.TLabel').pack(pady=(20, 10))
        
        password_frame = ttk.Frame(parent_frame)
        password_frame.pack(pady=(0, 10), fill=tk.X)
        
        self.decrypted_password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.decrypted_password_var, 
                                  state="readonly", width=25)
        password_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(password_frame, text="复制", 
                  command=self.copy_decrypted_password).pack(side=tk.LEFT)
        
        # 分隔线
        ttk.Separator(parent_frame, orient='horizontal').pack(fill='x', padx=10, pady=20)
        
        # 使用说明
        self.create_help_section(parent_frame)
    
    def create_help_section(self, parent_frame):
        """创建右侧帮助说明区域"""
        # 标题
        ttk.Label(parent_frame, text="软件使用说明", 
                 style='Header.TLabel', font=('Arial', 14, 'bold')).pack(pady=(10, 20))
        
        # 创建滚动文本框
        help_text = tk.Text(parent_frame, wrap=tk.WORD, width=35, height=30, 
                           font=('Arial', 10), bg='#f8f9fa', relief=tk.FLAT)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)
        
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加说明内容
        help_content = """
高级密码生成器使用说明

📋 基本功能：
• 支持1-8位数字密码生成
• 支持月日(MMDD)和日月(DDMM)密码
• 支持多前缀和多后缀组合
• 支持哈希值生成和提取
• 支持文件解密功能

🎯 前缀/后缀功能：
• 点击"增加前缀/后缀"添加多个输入框
• 每个输入框可以：
  - 直接输入固定字符
  - 使用"数字范围"选择数字序列
  - 使用"字符范围"选择字符集
  - 点击"清空"清除内容
  - 点击"删除"移除该输入框

🔢 数字范围：
• 格式：起始数字-结束数字
• 示例：1980-1999 生成 1980|1981|...|1999

🔤 字符范围：
• 预定义选项：
  - A-Z: 大写字母
  - a-z: 小写字母  
  - 0-9: 数字
  - A-Za-z: 所有字母
  - A-Za-z0-9: 字母和数字
• 自定义字符：直接输入任意字符

🔐 哈希选项：
• 支持算法：MD5, SHA1, SHA256, SM3
• 哈希提取：可设置起始位置和长度
• 输出类型：原始密码或哈希值

🔓 支持解密的文件类型：
✅ ZIP文件 (.zip) - 完全支持密码破解
✅ RAR文件 (.rar) - 完全支持密码破解  
✅ Word文档 (.doc, .docx) - 支持Office文档解密
✅ Excel文档 (.xls, .xlsx) - 支持Office文档解密
✅ PowerPoint文档 (.ppt, .pptx) - 支持Office文档解密
❌ 7z文件 (.7z) - 暂不支持（技术限制）

⚡ 使用技巧：
1. 组合使用多个前缀和后缀
2. 结合数字范围和字符范围
3. 使用月日/日月密码生成日期组合
4. 合理设置哈希提取参数
5. 使用生成的密码字典解密文件

⚠️ 注意事项：
• 组合数量会指数级增长，请谨慎设置
• 大量组合可能需要较长时间生成
• 建议先测试小范围再生成完整字典
• 解密过程可能需要较长时间，取决于字典大小

💡 示例：
前缀1: 1980-1999 (数字范围)
前缀2: A-Z (字符范围)
密码类型: 月日
后缀1: !@# (固定字符)
将生成: 1980A0101!@#, 1980A0102!@#, ... 

🔧 解密步骤：
1. 生成密码字典
2. 选择要解密的加密文件
3. 点击"开始解密"
4. 查看解密结果
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)  # 设置为只读
        
    def setup_styles(self):
        style = ttk.Style()
        # 统一背景色为白色
        style.configure('TFrame', background='white')
        style.configure('TLabel', background='white')
        style.configure('TButton', font=('Arial', 10), background='white')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='white')
        style.configure('TCombobox', background='white')
        style.configure('TRadiobutton', background='white')
        style.configure('TProgressbar', background='white')
        
        # 设置窗口背景色
        self.root.configure(bg='white')
        
    def create_widgets(self):
        # 标题
        ttk.Label(self.scrollable_frame, text="高级密码生成器 - 多前缀/后缀支持", 
                 style='Header.TLabel', font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 20))
        
        # 密码类型选择
        ttk.Label(self.scrollable_frame, text="密码类型:", style='Header.TLabel').grid(
            row=1, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        self.digit_length_var = tk.StringVar(value="4")
        digit_lengths = ["空值"] + [str(i) for i in range(1, 9)] + ["月日", "日月"]
        self.digit_length_combo = ttk.Combobox(self.scrollable_frame, textvariable=self.digit_length_var, 
                                              values=digit_lengths, state="readonly", width=15)
        self.digit_length_combo.grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        
        # 前缀区域
        ttk.Label(self.scrollable_frame, text="前缀设置:", style='Header.TLabel').grid(
            row=3, column=0, columnspan=4, sticky=tk.W, pady=(20, 10))
        
        # 初始前缀框
        self.add_prefix_frame()
        
        # 添加前缀按钮
        ttk.Button(self.scrollable_frame, text="+ 增加前缀", command=self.add_prefix_frame).grid(
            row=100, column=0, sticky=tk.W, pady=10)
        
        # 后缀区域
        ttk.Label(self.scrollable_frame, text="后缀设置:", style='Header.TLabel').grid(
            row=101, column=0, columnspan=4, sticky=tk.W, pady=(20, 10))
        
        # 初始后缀框
        self.add_suffix_frame()
        
        # 添加后缀按钮
        ttk.Button(self.scrollable_frame, text="+ 增加后缀", command=self.add_suffix_frame).grid(
            row=200, column=0, sticky=tk.W, pady=10)
        
        # 线程控制
        self.generation_thread = None
        self.decryption_thread = None
        self.stop_flag = False
        self.decryptor = None
    
    def add_prefix_frame(self):
        """添加一个新的前缀输入框"""
        row = len(self.prefix_frames) + 4
        prefix_frame = ttk.Frame(self.scrollable_frame)
        prefix_frame.grid(row=row, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        prefix_var = tk.StringVar()
        entry = ttk.Entry(prefix_frame, textvariable=prefix_var, width=30)  # 从20增大到30 (1.5倍)
        entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prefix_frame, text="数字范围...", 
                  command=lambda var=prefix_var: self.browse_number_range(var, "前缀"), 
                  width=10).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prefix_frame, text="字符范围...", 
                  command=lambda var=prefix_var: self.browse_char_range(var, "前缀"), 
                  width=10).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prefix_frame, text="清空", 
                  command=lambda: prefix_var.set(""), width=6).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prefix_frame, text="删除", 
                  command=lambda f=prefix_frame, v=prefix_var: self.remove_prefix_frame(f, v), 
                  width=6).pack(side=tk.LEFT)
        
        self.prefix_frames.append(prefix_frame)
        self.prefix_vars.append(prefix_var)
    
    def add_suffix_frame(self):
        """添加一个新的后缀输入框"""
        row = len(self.suffix_frames) + 102
        suffix_frame = ttk.Frame(self.scrollable_frame)
        suffix_frame.grid(row=row, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        suffix_var = tk.StringVar()
        entry = ttk.Entry(suffix_frame, textvariable=suffix_var, width=30)  # 从20增大到30 (1.5倍)
        entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(suffix_frame, text="数字范围...", 
                  command=lambda var=suffix_var: self.browse_number_range(var, "后缀"), 
                  width=10).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(suffix_frame, text="字符范围...", 
                  command=lambda var=suffix_var: self.browse_char_range(var, "后缀"), 
                  width=10).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(suffix_frame, text="清空", 
                  command=lambda: suffix_var.set(""), width=6).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(suffix_frame, text="删除", 
                  command=lambda f=suffix_frame, v=suffix_var: self.remove_suffix_frame(f, v), 
                  width=6).pack(side=tk.LEFT)
        
        self.suffix_frames.append(suffix_frame)
        self.suffix_vars.append(suffix_var)
    
    def remove_prefix_frame(self, frame, var):
        """删除前缀框"""
        frame.destroy()
        self.prefix_frames.remove(frame)
        self.prefix_vars.remove(var)
    
    def remove_suffix_frame(self, frame, var):
        """删除后缀框"""
        frame.destroy()
        self.suffix_frames.remove(frame)
        self.suffix_vars.remove(var)
    
    def browse_number_range(self, target_var, field_name):
        """打开数字范围选择对话框"""
        range_window = tk.Toplevel(self.root)
        range_window.title(f"选择{field_name}数字范围")
        range_window.geometry("350x200")
        range_window.resizable(False, False)
        
        ttk.Label(range_window, text=f"请输入{field_name}数字范围:").pack(pady=10)
        
        range_frame = ttk.Frame(range_window)
        range_frame.pack(pady=10)
        
        ttk.Label(range_frame, text="从:").grid(row=0, column=0, padx=5)
        start_var = tk.StringVar()
        ttk.Entry(range_frame, textvariable=start_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(range_frame, text="到:").grid(row=0, column=2, padx=5)
        end_var = tk.StringVar()
        ttk.Entry(range_frame, textvariable=end_var, width=10).grid(row=0, column=3, padx=5)
        
        def apply_range():
            try:
                start = int(start_var.get())
                end = int(end_var.get())
                if start > end:
                    messagebox.showerror("错误", "起始值不能大于结束值")
                    return
                
                numbers = [str(i) for i in range(start, end + 1)]
                target_var.set('|'.join(numbers))
                range_window.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
        
        button_frame = ttk.Frame(range_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=apply_range).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=range_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def browse_char_range(self, target_var, field_name):
        """打开字符范围选择对话框"""
        char_window = tk.Toplevel(self.root)
        char_window.title(f"选择{field_name}字符范围")
        char_window.geometry("400x500")  # 进一步增大高度以确保所有内容显示
        char_window.resizable(False, False)
        
        ttk.Label(char_window, text=f"请选择{field_name}字符范围:", 
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # 预定义的字符范围
        char_ranges = [
            ("A-Z", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            ("a-z", "abcdefghijklmnopqrstuvwxyz"),
            ("0-9", "0123456789"),
            ("A-Za-z", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"),
            ("A-Za-z0-9", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        ]
        
        for range_name, chars in char_ranges:
            ttk.Button(char_window, text=range_name, 
                      command=lambda c=chars, var=target_var: self._apply_char_range(c, var, char_window),
                      width=20).pack(pady=2)
        
        # 分隔线
        ttk.Separator(char_window, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # 自定义字符选项1：独立字符串
        ttk.Label(char_window, text="自定义独立字符串:", 
                 font=('Arial', 10, 'bold')).pack(pady=(5, 5))
        
        ttk.Label(char_window, text="输入任意字符作为完整字符串", 
                 font=('Arial', 9)).pack(pady=(0, 5))
        
        custom_frame1 = ttk.Frame(char_window)
        custom_frame1.pack(pady=5, fill=tk.X, padx=20)
        
        custom_text1 = tk.Text(custom_frame1, height=3, width=30, 
                             font=('Arial', 10), wrap=tk.WORD)
        custom_text1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar1 = ttk.Scrollbar(custom_frame1, orient="vertical", command=custom_text1.yview)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        custom_text1.configure(yscrollcommand=scrollbar1.set)
        
        def apply_custom_string():
            custom_chars = custom_text1.get("1.0", tk.END).strip()
            self._apply_custom_chars(custom_chars, target_var, char_window, is_range=False)
        
        ttk.Button(char_window, text="使用独立字符串", 
                  command=apply_custom_string, width=20).pack(pady=5)
        
        # 分隔线
        ttk.Separator(char_window, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # 自定义字符选项2：字符范围（逗号分隔）
        ttk.Label(char_window, text="自定义字符范围（逗号分隔）:", 
                 font=('Arial', 10, 'bold')).pack(pady=(5, 5))
        
        ttk.Label(char_window, text="用逗号分隔字符，如: a,b,c,1,2,3", 
                 font=('Arial', 9)).pack(pady=(0, 5))
        
        custom_frame2 = ttk.Frame(char_window)
        custom_frame2.pack(pady=5, fill=tk.X, padx=20)
        
        custom_text2 = tk.Text(custom_frame2, height=3, width=30, 
                             font=('Arial', 10), wrap=tk.WORD)
        custom_text2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar2 = ttk.Scrollbar(custom_frame2, orient="vertical", command=custom_text2.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        custom_text2.configure(yscrollcommand=scrollbar2.set)
        
        def apply_custom_range():
            custom_input = custom_text2.get("1.0", tk.END).strip()
            if custom_input:
                # 按逗号分割并去除空格
                chars_list = [char.strip() for char in custom_input.split(',') if char.strip()]
                custom_chars = '|'.join(chars_list)
                self._apply_custom_chars(custom_chars, target_var, char_window, is_range=True)
            else:
                messagebox.showerror("错误", "请输入用逗号分隔的字符")
        
        ttk.Button(char_window, text="使用字符范围", 
                  command=apply_custom_range, width=20).pack(pady=10)
    
    def _apply_char_range(self, chars, target_var, window):
        """应用字符范围"""
        target_var.set('|'.join(list(chars)))
        window.destroy()
    
    def _apply_custom_chars(self, custom_chars, target_var, window, is_range=False):
        """应用自定义字符"""
        if custom_chars:
            if is_range:
                # 已经是处理好的字符范围，直接设置
                target_var.set(custom_chars)
            else:
                # 独立字符串，转换为字符列表
                target_var.set('|'.join(list(custom_chars)))
            window.destroy()
        else:
            messagebox.showerror("错误", "请输入自定义字符")
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=self.output_file_var.get()
        )
        if filename:
            self.output_file_var.set(filename)
    
    def browse_existing_dict(self):
        """浏览已有字典文件"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="选择已有密码字典文件"
        )
        if filename:
            self.existing_dict_var.set(filename)
    
    def browse_dict_for_output(self):
        """为输出文件选择字典文件"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="选择密码字典文件"
        )
        if filename:
            self.output_file_var.set(filename)
    
    def use_existing_dict(self):
        """使用已有字典进行解密"""
        existing_dict = self.existing_dict_var.get().strip()
        
        if not existing_dict:
            messagebox.showerror("错误", "请先选择已有字典文件")
            return
            
        if not os.path.exists(existing_dict):
            messagebox.showerror("错误", f"字典文件不存在: {existing_dict}")
            return
            
        # 设置输出文件为选择的字典文件
        self.output_file_var.set(existing_dict)
        messagebox.showinfo("成功", f"已选择字典文件: {os.path.basename(existing_dict)}\n现在可以使用右侧的解密功能")
    
    def validate_inputs(self):
        try:
            digit_length_str = self.digit_length_var.get()
            
            # 检查是否是空值、月日或日月选项
            if digit_length_str not in ["空值", "月日", "日月"]:
                digit_length = int(digit_length_str)
                if digit_length < 1 or digit_length > 8:
                    raise ValueError("数字位数必须在1-8之间")
            
            start_pos = int(self.start_pos_var.get())
            if start_pos < 0:
                raise ValueError("起始位置不能为负数")
            
            segment_length = int(self.segment_length_var.get())
            if segment_length <= 0:
                raise ValueError("提取长度必须大于0")
                
            return True
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return False
    
    def _parse_options(self, var_list):
        """解析选项列表，处理数字范围和字符范围"""
        all_options = []
        for var in var_list:
            value = var.get().strip()
            if not value:
                # 对于空值，返回空字符串选项
                all_options.append([""])
                continue
            
            if '|' in value:
                # 已经是分隔的选项
                options = value.split('|')
                all_options.append(options)
            else:
                # 单个值
                all_options.append([value])
        
        return all_options
    
    def generate_passwords(self):
        digit_length_str = self.digit_length_var.get()
        output_type = self.output_type_var.get()
        hash_algo = self.hash_algo_var.get()
        start_pos = int(self.start_pos_var.get())
        segment_length = int(self.segment_length_var.get())
        output_file = self.output_file_var.get()
        
        digits = '0123456789'
        
        # 处理前缀选项
        prefix_options_list = self._parse_options(self.prefix_vars)
        
        # 处理后缀选项
        suffix_options_list = self._parse_options(self.suffix_vars)
        
        # 检查选择的是空值、月日还是日月选项
        use_empty = (digit_length_str == "空值")
        use_month_day = (digit_length_str == "月日")
        use_day_month = (digit_length_str == "日月")
        
        # 生成月日或日月密码
        date_options = []
        if use_month_day or use_day_month:
            # 生成所有可能的月日组合（0101-1231）或日月组合（0101-3112）
            for month in range(1, 13):
                for day in range(1, 32):  # 最大31天
                    month_str = str(month).zfill(2)
                    day_str = str(day).zfill(2)
                    if use_month_day:
                        date_options.append(month_str + day_str)  # 月日格式：MMDD
                    else:
                        date_options.append(day_str + month_str)  # 日月格式：DDMM
        elif not use_empty:
            # 使用普通数字位数
            digit_length = int(digit_length_str)
        
        # 计算总组合数
        total_prefix_combinations = 1
        for options in prefix_options_list:
            total_prefix_combinations *= len(options)
        
        total_suffix_combinations = 1
        for options in suffix_options_list:
            total_suffix_combinations *= len(options)
        
        if use_month_day or use_day_month:
            total_combinations = total_prefix_combinations * len(date_options) * total_suffix_combinations
        elif use_empty:
            total_combinations = total_prefix_combinations * total_suffix_combinations
        else:
            total_combinations = total_prefix_combinations * (10 ** digit_length) * total_suffix_combinations
        
        processed = 0
        
        output_type_text = "哈希值" if output_type == "hash" else "原始密码"
        if use_month_day:
            password_type_text = "月日密码"
        elif use_day_month:
            password_type_text = "日月密码"
        else:
            password_type_text = f"{digit_length}位数字密码"
            
        self.root.after(0, lambda: self.status_var.set(f"正在生成 {total_combinations} 个{password_type_text}{output_type_text}..."))
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # 生成所有前缀组合
                for prefix_combo in itertools.product(*prefix_options_list):
                    prefix_str = ''.join(prefix_combo)
                    
                    if use_month_day or use_day_month:
                        # 生成月日或日月密码
                        for date_option in date_options:
                            # 生成所有后缀组合
                            for suffix_combo in itertools.product(*suffix_options_list):
                                if self.stop_flag:
                                    break
                                    
                                suffix_str = ''.join(suffix_combo)
                                password = prefix_str + date_option + suffix_str
                                result = self._process_password(password, output_type, hash_algo, start_pos, segment_length)
                                f.write(result + '\n')
                                
                                processed += 1
                                progress = (processed / total_combinations) * 100
                                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                                
                                if processed % 1000 == 0:
                                    self.root.after(0, lambda: self.status_var.set(
                                        f"已处理 {processed}/{total_combinations} ({progress:.1f}%)"))
                    elif use_empty:
                        # 生成空值密码（只有前缀和后缀）
                        for suffix_combo in itertools.product(*suffix_options_list):
                            if self.stop_flag:
                                break
                                
                            suffix_str = ''.join(suffix_combo)
                            password = prefix_str + suffix_str
                            result = self._process_password(password, output_type, hash_algo, start_pos, segment_length)
                            f.write(result + '\n')
                            
                            processed += 1
                            progress = (processed / total_combinations) * 100
                            self.root.after(0, lambda p=progress: self.progress_var.set(p))
                            
                            if processed % 1000 == 0:
                                self.root.after(0, lambda: self.status_var.set(
                                    f"已处理 {processed}/{total_combinations} ({progress:.1f}%)"))
                    else:
                        # 生成普通数字密码
                        for combo in itertools.product(digits, repeat=digit_length):
                            # 生成所有后缀组合
                            for suffix_combo in itertools.product(*suffix_options_list):
                                if self.stop_flag:
                                    break
                                    
                                suffix_str = ''.join(suffix_combo)
                                password = prefix_str + ''.join(combo) + suffix_str
                                result = self._process_password(password, output_type, hash_algo, start_pos, segment_length)
                                f.write(result + '\n')
                                
                                processed += 1
                                progress = (processed / total_combinations) * 100
                                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                                
                                if processed % 1000 == 0:
                                    self.root.after(0, lambda: self.status_var.set(
                                        f"已处理 {processed}/{total_combinations} ({progress:.1f}%)"))
            
            if not self.stop_flag:
                self.root.after(0, lambda: self.status_var.set(
                    f"完成！共生成 {processed} 个{password_type_text}{output_type_text}"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "完成", f"密码字典生成完成！\n共生成 {processed} 个{password_type_text}{output_type_text}\n保存到: {output_file}"))
            else:
                self.root.after(0, lambda: self.status_var.set("已停止"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"生成过程中出现错误: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("错误"))
        
        finally:
            self.root.after(0, self.enable_buttons)
    
    def _process_password(self, password, output_type, hash_algo, start_pos, segment_length):
        """处理单个密码，根据输出类型返回结果"""
        if output_type == "original":
            # 使用原始密码
            return password
        else:
            # 计算哈希值
            if hash_algo == "MD5":
                hash_value = hashlib.md5(password.encode('utf-8')).hexdigest()
            elif hash_algo == "SHA1":
                hash_value = hashlib.sha1(password.encode('utf-8')).hexdigest()
            elif hash_algo == "SHA256":
                hash_value = hashlib.sha256(password.encode('utf-8')).hexdigest()
            elif hash_algo == "SM3":
                try:
                    msg = bytearray(password.encode('utf-8'))
                    hash_value = sm3.sm3_hash(msg)
                except:
                    hash_value = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            # 提取哈希片段
            if start_pos + segment_length > len(hash_value):
                actual_length = len(hash_value) - start_pos
            else:
                actual_length = segment_length
            
            return hash_value[start_pos:start_pos + actual_length]
    
    def start_generation(self):
        if not self.validate_inputs():
            return
            
        self.stop_flag = False
        self.disable_buttons()
        self.progress_var.set(0)
        self.status_var.set("正在生成...")
        
        # 在新线程中运行生成过程
        self.generation_thread = threading.Thread(target=self.generate_passwords)
        self.generation_thread.daemon = True
        self.generation_thread.start()
    
    def stop_generation(self):
        self.stop_flag = True
        self.status_var.set("正在停止...")
    
    def clear_all_fields(self):
        """清空所有字段"""
        # 清空前缀
        for var in self.prefix_vars:
            var.set("")
        
        # 清空后缀
        for var in self.suffix_vars:
            var.set("")
        
        # 清空其他字段
        self.start_pos_var.set("0")
        self.segment_length_var.set("8")
        self.output_file_var.set("password_dict.txt")
        self.progress_var.set(0)
        self.status_var.set("就绪")
    
    def disable_buttons(self):
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.state(['disabled'])
    
    def enable_buttons(self):
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.state(['!disabled'])
    
    def browse_encrypted_file(self):
        """浏览加密文件"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("加密文件", "*.zip *.rar *.doc *.docx *.xls *.xlsx *.ppt *.pptx"),
                ("ZIP文件", "*.zip"),
                ("RAR文件", "*.rar"),
                ("Word文档", "*.doc *.docx"),
                ("Excel文档", "*.xls *.xlsx"),
                ("PowerPoint文档", "*.ppt *.pptx"),
                ("所有文件", "*.*")
            ],
            title="选择加密文件 (支持 ZIP, RAR, Office文档)"
        )
        if filename:
            self.encrypted_file_var.set(filename)
    
    def _update_decrypt_progress(self, progress):
        """更新解密进度"""
        self.root.after(0, lambda: self.progress_var.set(progress))
    
    def _update_decrypt_status(self, status):
        """更新解密状态"""
        self.root.after(0, lambda: self.status_var.set(status))
    
    def start_decryption(self):
        """开始解密过程"""
        encrypted_file = self.encrypted_file_var.get().strip()
        password_dict = self.output_file_var.get().strip()
        
        if not encrypted_file:
            messagebox.showerror("错误", "请选择要解密的文件")
            return
            
        if not password_dict:
            messagebox.showerror("错误", "请先生成密码字典或选择密码字典文件")
            return
            
        if not os.path.exists(password_dict):
            messagebox.showerror("错误", f"密码字典文件不存在: {password_dict}")
            return
            
        # 确认开始解密
        if not messagebox.askyesno("确认", f"确定要开始解密文件吗？\n文件: {os.path.basename(encrypted_file)}\n将使用密码字典: {os.path.basename(password_dict)}"):
            return
            
        self.stop_flag = False
        self.disable_buttons()
        self.progress_var.set(0)
        self.status_var.set("正在准备解密...")
        
        # 初始化解密器
        self.decryptor = FileDecryptor(
            progress_callback=self._update_decrypt_progress,
            status_callback=self._update_decrypt_status
        )
        
        # 在新线程中运行解密过程
        self.decryption_thread = threading.Thread(
            target=self._run_decryption,
            args=(encrypted_file, password_dict)
        )
        self.decryption_thread.daemon = True
        self.decryption_thread.start()
    
    def _run_decryption(self, encrypted_file, password_dict):
        """运行解密过程"""
        try:
            use_gpu = self.use_gpu_var.get()
            result = self.decryptor.decrypt_file(encrypted_file, password_dict, use_gpu)
            
            if result:
                # 在密码框中显示解密成功的密码
                self.root.after(0, lambda: self.decrypted_password_var.set(result))
                self.root.after(0, lambda: messagebox.showinfo(
                    "解密成功", 
                    f"文件解密成功！\n密码: {result}\n密码已显示在解密密码框中，可点击复制按钮复制"
                ))
            else:
                self.root.after(0, lambda: self.decrypted_password_var.set(""))
                self.root.after(0, lambda: messagebox.showinfo(
                    "解密失败", 
                    "所有密码尝试完毕，未能解密文件"
                ))
                
        except Exception as e:
            self.root.after(0, lambda: self.decrypted_password_var.set(""))
            self.root.after(0, lambda: messagebox.showerror(
                "解密错误", 
                f"解密过程中出现错误: {str(e)}"
            ))
            
        finally:
            self.root.after(0, self.enable_buttons)
            self.root.after(0, lambda: self.status_var.set("就绪"))
    
    def copy_decrypted_password(self):
        """复制解密密码到剪贴板"""
        password = self.decrypted_password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()  # 现在剪贴板内容会持续存在
            messagebox.showinfo("复制成功", "密码已复制到剪贴板")
        else:
            messagebox.showwarning("无密码", "没有可复制的密码")
    
    def detect_gpu_info(self):
        """检测显卡信息"""
        # 显示进度条
        self.gpu_progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.gpu_progress_bar.start(10)  # 开始不确定进度条动画
        self.gpu_status_var.set("正在检测显卡信息...")
        
        # 在新线程中运行GPU检测
        threading.Thread(target=self._run_gpu_detection, daemon=True).start()
    
    def _run_gpu_detection(self):
        """在新线程中运行GPU检测"""
        try:
            gpu_info = detect_gpu()
            
            if gpu_info['has_gpu']:
                gpu_status = get_gpu_status()
                # 启用GPU加速选项
                self.root.after(0, lambda: self.use_gpu_checkbutton.state(['!disabled']))
                
                # 根据GPU状态设置颜色
                color = 'green' if gpu_info['cuda_available'] or gpu_info['opencl_available'] else 'orange'
                self.root.after(0, lambda: self.gpu_status_var.set(gpu_status))
                self.root.after(0, lambda: self.gpu_status_label.configure(foreground=color))
            else:
                self.root.after(0, lambda: self.gpu_status_var.set("未检测到GPU，使用CPU模式"))
                self.root.after(0, lambda: self.gpu_status_label.configure(foreground='gray'))
                
        except Exception as e:
            self.root.after(0, lambda: self.gpu_status_var.set(f"GPU检测失败: {str(e)}"))
            self.root.after(0, lambda: self.gpu_status_label.configure(foreground='red'))
            
        finally:
            # 停止并隐藏进度条
            self.root.after(0, self.gpu_progress_bar.stop)
            self.root.after(0, self.gpu_progress_bar.pack_forget)
    
    def stop_decryption(self):
        """停止解密过程"""
        self.stop_flag = True
        if self.decryptor:
            self.decryptor.stop_decryption()
        self.status_var.set("正在停止解密...")
    

def main():
    root = tk.Tk()
    app = AdvancedPasswordGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
