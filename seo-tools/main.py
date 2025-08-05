import os
from dotenv import load_dotenv
from dify_plugin import Plugin, DifyPluginEnv

# 加载环境变量
load_dotenv()

# 创建插件环境配置
env_config = DifyPluginEnv(
    MAX_REQUEST_TIMEOUT=120,
    INSTALL_METHOD=os.getenv('INSTALL_METHOD', 'local'),
    REMOTE_INSTALL_URL=os.getenv('REMOTE_INSTALL_URL'),
    REMOTE_INSTALL_PORT=int(os.getenv('REMOTE_INSTALL_PORT', 5003)),
    REMOTE_INSTALL_KEY=os.getenv('REMOTE_INSTALL_KEY')
)

plugin = Plugin(env_config)

if __name__ == '__main__':
    plugin.run()
