# Python 이미지 설정
FROM python:3.13.1-slim

# 작업 디렉터리 설정
WORKDIR /projects

# 의존성 복사 및 설치
COPY requirements.txt /home/requirements.txt
COPY entrypoint.sh /home/entrypoint.sh

RUN chmod +x /home/entrypoint.sh
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y procps

RUN pip install --no-cache-dir -r /home/requirements.txt

# 포트 오픈
EXPOSE 8000

# 기본 명령어 (프로젝트 없으면 생성)
ENTRYPOINT ["/home/entrypoint.sh"]
