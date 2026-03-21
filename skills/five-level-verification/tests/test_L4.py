#!/usr/bin/env python3
"""
L4 Test Cases - 集成验证测试
"""

import os
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from verify import FiveLevelVerifier


class TestL4Integration(unittest.TestCase):
    """L4: 集成验证测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill_name = "test_skill"
        self.skill_path = os.path.join(self.temp_dir, self.skill_name)
        os.makedirs(self.skill_path)
        
        # 创建基本文件
        with open(os.path.join(self.skill_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill\n\n## Purpose\nTest purpose\n\n## Usage\n```\npython main.py\n```")
        with open(os.path.join(self.skill_path, "config.yaml"), "w") as f:
            f.write("skill:\n  name: test\n")
        os.makedirs(os.path.join(self.skill_path, "scripts"))
        os.makedirs(os.path.join(self.skill_path, "tests"))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_complete_documentation(self):
        """测试完整的文档"""
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L4()
        self.assertTrue(passed)
        self.assertTrue(result["checks"]["skill_doc_complete"])
    
    def test_missing_tests(self):
        """测试缺失测试目录"""
        shutil.rmtree(os.path.join(self.skill_path, "tests"))
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L4()
        self.assertFalse(passed)
        self.assertFalse(result["checks"]["has_tests"])
    
    def test_incomplete_documentation(self):
        """测试不完整的文档"""
        with open(os.path.join(self.skill_path, "SKILL.md"), "w") as f:
            f.write("# Test Skill\n")  # 缺少Purpose和Usage
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = self.skill_path
        
        passed, result = verifier.verify_L4()
        self.assertFalse(passed)
        self.assertFalse(result["checks"]["skill_doc_complete"])


if __name__ == "__main__":
    unittest.main()
