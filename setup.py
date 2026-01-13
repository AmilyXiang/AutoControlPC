#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
setup.py
AutoControlPC 项目安装脚本
"""
from setuptools import setup, find_packages
import os

# 读取长描述
long_description = ""
if os.path.isfile("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

# 读取依赖列表
requirements = []
if os.path.isfile("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="AutoControlPC",
    version="1.0.0",
    author="AutoControlPC Team",
    description="自动化UI和网络协调测试系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AutoControlPC/AutoControlPC",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    # 注意：run_testcase.py 是直接运行脚本，不需要 entry_points
    # 使用方式: python run_testcase.py <xml文件路径>
)
