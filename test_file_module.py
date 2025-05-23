"""
文件管理模块测试脚本
用于验证文件管理功能是否正常工作
"""

import asyncio
import aiohttp
import json
from pathlib import Path
import tempfile
import os

# 测试配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

class FileModuleTest:
    def __init__(self):
        self.session = None
        self.access_token = None
        self.test_folder_id = None
        self.test_file_id = None

    async def setup_session(self):
        """设置HTTP会话"""
        self.session = aiohttp.ClientSession()

    async def cleanup_session(self):
        """清理HTTP会话"""
        if self.session:
            await self.session.close()

    async def login(self, username: str = "admin", password: str = "admin123"):
        """登录获取访问令牌"""
        login_data = {
            "username": username,
            "password": password
        }
        
        async with self.session.post(
            f"{BASE_URL}{API_PREFIX}/auth/login",
            data=login_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                self.access_token = result.get("data", {}).get("access_token")
                print(f"✅ 登录成功，获取到令牌: {self.access_token[:20]}...")
                return True
            else:
                print(f"❌ 登录失败: {response.status}")
                return False

    @property
    def headers(self):
        """获取认证头"""
        return {
            "Authorization": f"Bearer {self.access_token}"
        } if self.access_token else {}

    async def test_create_folder(self):
        """测试创建文件夹"""
        folder_data = {
            "name": "测试文件夹",
            "parent_id": None,
            "is_public": False
        }

        async with self.session.post(
            f"{BASE_URL}{API_PREFIX}/file/folders/",
            json=folder_data,
            headers=self.headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                self.test_folder_id = result.get("data", {}).get("id")
                print(f"✅ 创建文件夹成功，ID: {self.test_folder_id}")
                return True
            else:
                print(f"❌ 创建文件夹失败: {response.status}")
                text = await response.text()
                print(f"错误信息: {text}")
                return False

    async def test_list_folders(self):
        """测试获取文件夹列表"""
        async with self.session.get(
            f"{BASE_URL}{API_PREFIX}/file/folders/",
            headers=self.headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                folders = result.get("data", [])
                print(f"✅ 获取文件夹列表成功，共 {len(folders)} 个文件夹")
                return True
            else:
                print(f"❌ 获取文件夹列表失败: {response.status}")
                return False

    async def test_upload_file(self):
        """测试文件上传"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("这是一个测试文件内容\n文件管理模块测试")
            temp_file_path = f.name

        try:
            # 准备文件上传数据
            with open(temp_file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='test_file.txt', content_type='text/plain')
                if self.test_folder_id:
                    data.add_field('folder_id', str(self.test_folder_id))
                data.add_field('is_public', 'false')
                data.add_field('tags', 'test,upload')

                async with self.session.post(
                    f"{BASE_URL}{API_PREFIX}/file/upload/",
                    data=data,
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.test_file_id = result.get("data", {}).get("id")
                        print(f"✅ 文件上传成功，ID: {self.test_file_id}")
                        return True
                    else:
                        print(f"❌ 文件上传失败: {response.status}")
                        text = await response.text()
                        print(f"错误信息: {text}")
                        return False
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)

    async def test_list_files(self):
        """测试获取文件列表"""
        params = {}
        if self.test_folder_id:
            params['folder_id'] = self.test_folder_id

        async with self.session.get(
            f"{BASE_URL}{API_PREFIX}/file/files/",
            params=params,
            headers=self.headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                files = result.get("data", [])
                print(f"✅ 获取文件列表成功，共 {len(files)} 个文件")
                return True
            else:
                print(f"❌ 获取文件列表失败: {response.status}")
                return False

    async def test_get_file_info(self):
        """测试获取文件详情"""
        if not self.test_file_id:
            print("⚠️  跳过文件详情测试（无测试文件）")
            return True

        async with self.session.get(
            f"{BASE_URL}{API_PREFIX}/file/files/{self.test_file_id}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                file_info = result.get("data", {})
                print(f"✅ 获取文件详情成功，文件名: {file_info.get('name')}")
                return True
            else:
                print(f"❌ 获取文件详情失败: {response.status}")
                return False

    async def test_folder_tree(self):
        """测试获取文件夹树"""
        async with self.session.get(
            f"{BASE_URL}{API_PREFIX}/file/folders/tree/",
            headers=self.headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                tree = result.get("data", [])
                print(f"✅ 获取文件夹树成功，根节点数: {len(tree)}")
                return True
            else:
                print(f"❌ 获取文件夹树失败: {response.status}")
                return False

    async def test_search_files(self):
        """测试文件搜索"""
        search_data = {
            "keyword": "test",
            "extensions": [".txt"],
            "folder_id": self.test_folder_id
        }

        async with self.session.post(
            f"{BASE_URL}{API_PREFIX}/file/files/search/",
            json=search_data,
            headers=self.headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                files = result.get("data", [])
                print(f"✅ 文件搜索成功，找到 {len(files)} 个文件")
                return True
            else:
                print(f"❌ 文件搜索失败: {response.status}")
                return False

    async def cleanup_test_data(self):
        """清理测试数据"""
        # 删除测试文件
        if self.test_file_id:
            async with self.session.delete(
                f"{BASE_URL}{API_PREFIX}/file/files/{self.test_file_id}?permanent=true",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    print("✅ 清理测试文件成功")
                else:
                    print(f"⚠️  清理测试文件失败: {response.status}")

        # 删除测试文件夹
        if self.test_folder_id:
            async with self.session.delete(
                f"{BASE_URL}{API_PREFIX}/file/folders/{self.test_folder_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    print("✅ 清理测试文件夹成功")
                else:
                    print(f"⚠️  清理测试文件夹失败: {response.status}")

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始文件管理模块测试...")
        print("=" * 50)

        await self.setup_session()

        try:
            # 基础测试
            tests = [
                ("用户登录", self.login()),
                ("创建文件夹", self.test_create_folder()),
                ("获取文件夹列表", self.test_list_folders()),
                ("上传文件", self.test_upload_file()),
                ("获取文件列表", self.test_list_files()),
                ("获取文件详情", self.test_get_file_info()),
                ("获取文件夹树", self.test_folder_tree()),
                ("搜索文件", self.test_search_files()),
            ]

            success_count = 0
            total_count = len(tests)

            for test_name, test_coro in tests:
                print(f"\n🧪 测试: {test_name}")
                try:
                    success = await test_coro
                    if success:
                        success_count += 1
                except Exception as e:
                    print(f"❌ 测试异常: {str(e)}")

            print("\n" + "=" * 50)
            print(f"📊 测试结果: {success_count}/{total_count} 通过")

            # 清理测试数据
            print("\n🧹 清理测试数据...")
            await self.cleanup_test_data()

        finally:
            await self.cleanup_session()

async def main():
    """主函数"""
    tester = FileModuleTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 