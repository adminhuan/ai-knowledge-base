#!/bin/bash

# 个人智识库 - 一键部署脚本（国内版）
# 使用方法: curl -fsSL https://gitee.com/2201_75827989/zhi_shi_ku/raw/main/deploy-cn.sh | bash

set -e

echo "======================================"
echo "   个人智识库 - 一键部署脚本（国内版）"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查命令是否存在
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 已安装"
        return 0
    else
        echo -e "${RED}✗${NC} $1 未安装"
        return 1
    fi
}

# 安装 Docker（使用阿里云镜像）
install_docker() {
    echo -e "${YELLOW}正在安装 Docker（阿里云镜像）...${NC}"
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    
    # 配置 Docker 镜像加速
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    echo -e "${GREEN}Docker 安装完成（已配置国内镜像加速）${NC}"
}

# 安装 Docker Compose
install_docker_compose() {
    echo -e "${YELLOW}正在安装 Docker Compose...${NC}"
    # 使用国内镜像
    sudo curl -L "https://ghproxy.com/https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose 2>/dev/null || \
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose 安装完成${NC}"
}

# 安装 Python
install_python() {
    echo -e "${YELLOW}正在安装 Python...${NC}"
    if [ -f /etc/debian_version ]; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y python3 python3-pip
    fi
    echo -e "${GREEN}Python 安装完成${NC}"
}

# 配置 pip 国内镜像
config_pip_mirror() {
    mkdir -p ~/.pip
    cat > ~/.pip/pip.conf <<EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
    echo -e "${GREEN}pip 已配置清华镜像源${NC}"
}

echo ">>> 检查环境..."
echo ""

# 检查并安装依赖
if ! check_command docker; then
    install_docker
fi

if ! check_command docker-compose && ! docker compose version &> /dev/null; then
    install_docker_compose
fi

if ! check_command python3; then
    install_python
fi

# 配置 pip 镜像
config_pip_mirror

echo ""
echo ">>> 克隆项目（Gitee）..."

# 克隆项目（使用 Gitee）
if [ -d "zhi_shi_ku" ]; then
    echo "项目目录已存在，正在更新..."
    cd zhi_shi_ku
    git pull
else
    git clone https://gitee.com/2201_75827989/zhi_shi_ku.git
    cd zhi_shi_ku
fi

echo ""
echo ">>> 启动数据库..."

# 启动数据库
docker-compose up -d

# 等待数据库启动
echo "等待数据库启动..."
sleep 10

echo ""
echo ">>> 配置后端..."

cd server

# 创建环境变量文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}请编辑 server/.env 文件，填入你的 API 密钥${NC}"
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "======================================"
echo -e "${GREEN}   部署完成！${NC}"
echo "======================================"
echo ""
echo "后续步骤："
echo ""
echo "1. 编辑配置文件（填入你的 API 密钥）："
echo "   nano server/.env"
echo ""
echo "2. 启动后端服务："
echo "   cd server"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --host 0.0.0.0 --port 8080"
echo ""
echo "3. 后台运行（可选）："
echo "   nohup uvicorn main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &"
echo ""
echo "4. 访问 API 文档："
echo "   http://你的服务器IP:8080/docs"
echo ""
echo "======================================"
