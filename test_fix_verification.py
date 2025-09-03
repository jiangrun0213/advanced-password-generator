#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools

def test_fixed_empty_password_generation():
    """测试修复后的空值密码生成"""
    
    print("=== 测试修复后的空值密码生成 ===")
    
    # 模拟四个中文字符前缀
    prefix_options = [['中文1'], ['中文2'], ['中文3'], ['中文4']]
    
    # 模拟空后缀（两个空字符串）
    suffix_options = [[''], ['']]
    
    print("前缀选项:", prefix_options)
    print("后缀选项:", suffix_options)
    
    # 计算组合数
    total_prefix_combinations = 1
    for options in prefix_options:
        total_prefix_combinations *= len(options)
    
    total_suffix_combinations = 1
    for options in suffix_options:
        total_suffix_combinations *= len(options)
    
    total_combinations = total_prefix_combinations * total_suffix_combinations
    print("计算的总组合数:", total_combinations)
    
    # 实际生成密码
    passwords = []
    for prefix_combo in itertools.product(*prefix_options):
        prefix_str = ''.join(prefix_combo)
        
        for suffix_combo in itertools.product(*suffix_options):
            suffix_str = ''.join(suffix_combo)
            password = prefix_str + suffix_str
            passwords.append(password)
    
    print("实际生成的密码:", passwords)
    print("实际生成的密码数量:", len(passwords))
    
    # 验证修复：应该生成正确的密码组合
    expected_password = "中文1中文2中文3中文4"
    if len(passwords) == 1 and passwords[0] == expected_password:
        print("✅ 修复成功！空值密码生成正常")
        print(f"✅ 生成的密码: {passwords[0]}")
    else:
        print("❌ 修复失败！")
        print(f"期望: [{expected_password}]")
        print(f"实际: {passwords}")

if __name__ == "__main__":
    test_fixed_empty_password_generation()
