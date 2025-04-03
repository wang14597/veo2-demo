FROM python:3.11-slim

WORKDIR /app

# 复制应用代码和依赖列表
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8501

# 设置环境变量，确保 Streamlit 可以在容器中正常运行
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false

# 启动应用
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
