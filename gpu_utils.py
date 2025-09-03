#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import platform

def detect_gpu():
    """检测系统是否支持GPU加速"""
    gpu_info = {
        'has_gpu': False,
        'gpu_type': None,
        'gpu_name': None,
        'cuda_available': False,
        'opencl_available': False
    }
    
    try:
        # 检测NVIDIA GPU
        if platform.system() == "Windows":
            # 在Windows上使用nvidia-smi检测NVIDIA GPU
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    gpu_info['has_gpu'] = True
                    gpu_info['gpu_type'] = 'NVIDIA'
                    gpu_info['gpu_name'] = result.stdout.strip().split('\n')[0]
                    
                    # 检查CUDA是否可用
                    try:
                        result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            gpu_info['cuda_available'] = True
                    except:
                        pass
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        # 检测AMD GPU (在Windows上)
        if not gpu_info['has_gpu'] and platform.system() == "Windows":
            try:
                # 尝试使用Windows Management Instrumentation检测AMD GPU
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'amd' in line.lower() or 'radeon' in line.lower():
                            gpu_info['has_gpu'] = True
                            gpu_info['gpu_type'] = 'AMD'
                            gpu_info['gpu_name'] = line.strip()
                            break
            except:
                pass
        
        # 检测Intel GPU
        if not gpu_info['has_gpu'] and platform.system() == "Windows":
            try:
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'intel' in line.lower():
                            gpu_info['has_gpu'] = True
                            gpu_info['gpu_type'] = 'Intel'
                            gpu_info['gpu_name'] = line.strip()
                            break
            except:
                pass
        
        # 在Linux/macOS上的检测逻辑可以在这里添加
        
        return gpu_info
        
    except Exception as e:
        return gpu_info

def get_gpu_status():
    """获取GPU状态信息"""
    gpu_info = detect_gpu()
    
    if gpu_info['has_gpu']:
        status = f"检测到GPU: {gpu_info['gpu_name']} ({gpu_info['gpu_type']})"
        if gpu_info['cuda_available']:
            status += " - CUDA可用"
        elif gpu_info['opencl_available']:
            status += " - OpenCL可用"
        else:
            status += " - 需要安装驱动"
    else:
        status = "未检测到GPU，使用CPU模式"
    
    return status

if __name__ == "__main__":
    status = get_gpu_status()
    print(status)
