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

EXPOSE 48012


# Run the application
CMD ["uvicorn" ,"main:app", "--reload", "--host", "0.0.0.0", "--port", "48012", "--workers", "16"]
# CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--reload"]


