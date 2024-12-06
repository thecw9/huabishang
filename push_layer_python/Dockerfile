FROM python:3.11.8-bookworm

WORKDIR /app

ENV TZ=Asia/Shanghai

# Copy the requirements.txt first for better cache on later pushes
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application
COPY . .

# Run the application
CMD ["python3", "-u" ,"main.py"]


