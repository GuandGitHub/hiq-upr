#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HIQ UPR Process Tree Builder - 主入口
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from menu import main

if __name__ == '__main__':
    main()
