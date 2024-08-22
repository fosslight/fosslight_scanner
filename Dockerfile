# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
# 기본 이미지로 Python 3.8이 설치된 Debian Buster의 슬림 버전을 사용
FROM python:3.8-slim-buster  

# 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사
COPY . /app  
# 작업 디렉토리를 /app으로 설정
WORKDIR	/app  

# /bin/sh를 /bin/bash로 심볼릭 링크 생성
RUN ln -sf /bin/bash /bin/sh && \  
# 패키지 목록 업데이트
  apt-get update && \  
  # 필요한 시스템 패키지 설치, 추천 패키지는 제외
  apt-get install --no-install-recommends -y  \  
  # 컴파일에 필요한 기본 도구
  build-essential \  
  # Python 관련 패키지
  python3 python3-distutils python3-pip python3-dev python3-magic \  
  # XML 처리 라이브러리
  libxml2-dev \ 
  # XSLT 처리 라이브러리 
  libxslt1-dev \  
  # HDF5 데이터 포맷 라이브러리
  libhdf5-dev \  
  # 압축 관련 유틸리티 및 라이브러리
  bzip2 xz-utils zlib1g libpopt0 && \  
  # 패키지 캐시 정리
  apt-get clean && \  
  # 패키지 리스트 삭제로 이미지 크기 감소
  rm -rf /var/lib/apt/lists/*  

# Install dependencies
# pip 최신 버전으로 업그레이드
RUN pip3 install --upgrade pip && \  
		# FOSSLight 유틸리티 설치
    pip3 install fosslight_util && \  
    # 파일 타입 감지 라이브러리 설치
    pip3 install python-magic && \  
    # 의존성 파싱 라이브러리 설치
    pip3 install dparse  

# fosslight_source 설치
RUN pip3 install fosslight_source --no-deps && \  
    pip3 show fosslight_source | grep "Requires:" | sed 's/Requires://' | tr ',' '\n' | grep -v "typecode-libmagic" > /tmp/fosslight_source_deps.txt && \  
    pip3 install -r /tmp/fosslight_source_deps.txt && \  
    rm /tmp/fosslight_source_deps.txt

# requirements.txt에서 fosslight_source 관련 내용을 제외한 커스텀 requirements 생성
COPY requirements.txt /tmp/requirements.txt
RUN grep -vE "fosslight[-_]source" /tmp/requirements.txt > /tmp/custom_requirements.txt && \
    pip3 install -r /tmp/custom_requirements.txt && \
    rm /tmp/requirements.txt /tmp/custom_requirements.txt

# fosslight_scanner 설치
COPY . /fosslight_scanner
WORKDIR /fosslight_scanner
RUN pip3 install . --no-deps

# 기타 의존성 설치
RUN pip3 install --upgrade pip && \
    pip3 install dparse && \
    rm -rf ~/.cache/pip /root/.cache/pip

# 환경 변수 PATH에 /usr/local/bin 추가
ENV PATH="/usr/local/bin:${PATH}"  

# /src 디렉토리를 볼륨으로 선언 (호스트와 데이터 공유 가능)
VOLUME /src  
# 작업 디렉토리를 /src로 변경
WORKDIR /src  

# Create an entry point script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if command -v "$1" > /dev/null 2>&1; then' >> /entrypoint.sh && \
    echo '    exec "$@"' >> /entrypoint.sh && \
    echo 'else' >> /entrypoint.sh && \
    echo '    exec fosslight_source "$@"' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# 컨테이너 시작 시 실행할 명령어 지정
ENTRYPOINT ["/entrypoint.sh"]

# 기본 명령어 인자 지정 (도움말 출력)
CMD ["-h"]

