#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile
import rarfile
import msoffcrypto
import io
import subprocess
import os
import tempfile
import threading
import shutil
from pathlib import Path

class FileDecryptor:
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.stop_flag = False
        
    def update_progress(self, progress):
        if self.progress_callback:
            self.progress_callback(progress)
            
    def update_status(self, status):
        if self.status_callback:
            self.status_callback(status)
    
    def decrypt_file(self, encrypted_file, password_dict_file, use_gpu=False):
        """使用密码字典解密文件"""
        try:
            self.stop_flag = False
            self.update_status("正在准备解密...")
            
            # 读取密码字典
            with open(password_dict_file, 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            total_passwords = len(passwords)
            
            if use_gpu:
                self.update_status(f"GPU加速模式 - 共 {total_passwords} 个密码需要尝试")
                # 这里可以添加GPU加速的解密逻辑
                # 目前先使用CPU模式，后续可以扩展GPU加速功能
                result = self._decrypt_with_cpu(encrypted_file, passwords)
            else:
                self.update_status(f"CPU模式 - 共 {total_passwords} 个密码需要尝试")
                result = self._decrypt_with_cpu(encrypted_file, passwords)
            
            return result
            
        except Exception as e:
            self.update_status(f"解密过程中出现错误: {str(e)}")
            return None
    
    def _decrypt_with_cpu(self, encrypted_file, passwords):
        """使用CPU进行解密"""
        total_passwords = len(passwords)
        file_ext = os.path.splitext(encrypted_file)[1].lower()
        
        # 显示支持的文件类型
        supported_extensions = ['.zip', '.rar', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        
        if file_ext not in supported_extensions:
            self.update_status(f"不支持的文件类型: {file_ext} (支持: {', '.join(supported_extensions)})")
            return None
        
        for i, password in enumerate(passwords):
            if self.stop_flag:
                self.update_status("解密已停止")
                return None
            
            progress = (i / total_passwords) * 100
            self.update_progress(progress)
            self.update_status(f"正在尝试密码 {i+1}/{total_passwords}: {password}")
            
            try:
                if file_ext in ['.zip']:
                    result = self._decrypt_zip(encrypted_file, password)
                elif file_ext in ['.rar']:
                    result = self._decrypt_rar(encrypted_file, password)
                elif file_ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                    result = self._decrypt_office(encrypted_file, password)
                else:
                    self.update_status(f"不支持的文件类型: {file_ext}")
                    return None
                
                if result:
                    self.update_progress(100)
                    self.update_status(f"解密成功！密码: {password}")
                    return password
                    
            except Exception as e:
                # 密码错误，继续尝试下一个
                continue
        
        self.update_status("所有密码尝试完毕，未能解密文件")
        return None
    
    def _decrypt_zip(self, zip_file, password):
        """验证ZIP文件密码"""
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.setpassword(password.encode('utf-8'))
                file_list = zip_ref.namelist()
                if not file_list:
                    return False
                
                # 尝试实际读取文件数据来验证密码
                try:
                    with zip_ref.open(file_list[0], pwd=password.encode('utf-8')) as f:
                        # 只读取少量数据来验证密码
                        f.read(1)  # 读取1个字节就足够验证
                    return True
                except (RuntimeError, zipfile.BadZipFile):
                    return False
                    
        except Exception as e:
            return False
    
    def _decrypt_rar(self, rar_file, password):
        """验证RAR文件密码"""
        try:
            with rarfile.RarFile(rar_file, 'r') as rar_ref:
                rar_ref.setpassword(password)
                file_list = rar_ref.namelist()
                if not file_list:
                    return False
                
                # 尝试实际读取文件数据来验证密码
                try:
                    with rar_ref.open(file_list[0], pwd=password) as f:
                        # 只读取少量数据来验证密码
                        f.read(1)  # 读取1个字节就足够验证
                    return True
                except (rarfile.BadRarFile, rarfile.PasswordRequired, rarfile.RarCannotExec):
                    return False
                    
        except Exception as e:
            return False
    
    
    def _decrypt_office(self, office_file, password):
        """验证Office文档密码"""
        try:
            # 使用msoffcrypto库解密Office文档
            with open(office_file, 'rb') as f:
                office_file_obj = msoffcrypto.OfficeFile(f)
                
                # 检查文件是否加密
                if not office_file_obj.is_encrypted():
                    return False
                
                # 尝试使用密码解密
                try:
                    # 创建内存缓冲区来存储解密后的内容
                    decrypted_stream = io.BytesIO()
                    office_file_obj.load_key(password=password)
                    office_file_obj.decrypt(decrypted_stream)
                    
                    # 如果解密成功，返回True
                    return True
                    
                except (msoffcrypto.exceptions.InvalidKeyError, 
                        msoffcrypto.exceptions.DecryptionError):
                    # 密码错误
                    return False
                except Exception as e:
                    # 其他解密错误
                    return False
                    
        except Exception as e:
            # 文件读取或其他错误
            return False
    
    def stop_decryption(self):
        """停止解密过程"""
        self.stop_flag = True
        self.update_status("正在停止解密...")

# 测试函数
def test_decryptor():
    decryptor = FileDecryptor(
        progress_callback=lambda p: print(f"进度: {p}%"),
        status_callback=lambda s: print(f"状态: {s}")
    )
    
    # 测试文件
    test_file = "test.zip"  # 需要实际存在的测试文件
    password_file = "password_dict.txt"
    
    if os.path.exists(test_file) and os.path.exists(password_file):
        result = decryptor.decrypt_file(test_file, password_file)
        print(f"解密结果: {result}")
    else:
        print("测试文件不存在")

if __name__ == "__main__":
    test_decryptor()
