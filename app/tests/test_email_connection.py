import aiosmtplib
import ssl
import asyncio

async def test_smtp_connection():
    """测试SMTP服务器连接"""
    client = None
    try:
        # SMTP配置
        smtp_host = "s220s.chinaemail.cn"
        smtp_port = 465
        smtp_user = "fangmr@h-sun.com"
        smtp_password = "5022381eCgfGeyXQ"
        # smtp_user = "shenlj@h-sun.com"
        # smtp_password = "7a44f92fWqeGeEG7"
        
        # 创建安全上下文
        context = ssl.create_default_context()
        
        # 记录连接信息
        print(f"正在连接SMTP服务器: {smtp_host}:{smtp_port} (SSL: True)")
        
        # 创建SMTP客户端
        client = aiosmtplib.SMTP(
            hostname=smtp_host,
            port=smtp_port,
            use_tls=False,
            tls_context=context
        )
        
        # 连接到SSL端口
        await client.connect(
            timeout=30,
            hostname=smtp_host,
            port=smtp_port,
            tls_context=context,
            use_tls=True,
            start_tls=False
        )
        
        # 登录
        await client.login(smtp_user, smtp_password)
        print(f"SMTP登录成功: {smtp_user}")
        
        # 测试连接
        response = await client.noop()
        if response.code == 250:
            print("SMTP连接测试成功")
        else:
            print(f"SMTP连接测试失败: {response.code} {response.message}")
        
    except aiosmtplib.SMTPException as e:
        print(f"SMTP错误: {str(e)}")
    except Exception as e:
        print(f"SMTP服务器连接测试失败: {str(e)}")
    finally:
        # 确保客户端连接被正确关闭
        if client:
            try:
                await client.quit()
            except Exception as e:
                print(f"关闭连接时发生错误: {str(e)}")

def main():
    """主函数"""
    try:
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 运行测试
        loop.run_until_complete(test_smtp_connection())
    finally:
        # 确保事件循环被正确关闭
        try:
            loop.close()
        except Exception as e:
            print(f"关闭事件循环时发生错误: {str(e)}")

if __name__ == "__main__":
    main()

