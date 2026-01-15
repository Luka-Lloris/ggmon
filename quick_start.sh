#!/bin/bash

# Contract Platform 빠른 시작 스크립트

set -e

echo "🚀 Contract Platform 설정 시작..."
echo ""

# 1. Python 버전 확인
echo "1️⃣ Python 버전 확인..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3가 설치되어 있지 않습니다."
    echo "   https://www.python.org/downloads/ 에서 설치하세요."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"
echo ""

# 2. 가상환경 생성
echo "2️⃣ Python 가상환경 생성..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 가상환경 생성 완료"
else
    echo "⚠️  가상환경이 이미 존재합니다."
fi
echo ""

# 3. 가상환경 활성화
echo "3️⃣ 가상환경 활성화..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi
echo "✅ 가상환경 활성화됨"
echo ""

# 4. 패키지 설치
echo "4️⃣ 필요한 패키지 설치..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 패키지 설치 완료"
echo ""

# 5. 디렉토리 구조 생성
echo "5️⃣ 디렉토리 구조 생성..."
mkdir -p data/workers
mkdir -p data/contracts
mkdir -p outputs/contracts
mkdir -p config
echo "✅ 디렉토리 생성 완료"
echo ""

# 6. 샘플 파일 확인
echo "6️⃣ 샘플 파일 확인..."
if [ ! -f "config/company.json" ]; then
    echo "⚠️  config/company.json 파일이 없습니다. 생성 중..."
    cat > config/company.json << 'EOF'
{
  "company_name": "(주)테크코퍼레이션",
  "company_ceo": "김대표",
  "company_address": "서울특별시 강남구 테헤란로 456, 10층",
  "company_registration_number": "123-45-67890",
  "company_phone": "02-1234-5678",
  "company_email": "contact@techcorp.com",
  "tax_settings": {
    "freelancer_tax_rate": 3.3
  },
  "contract_defaults": {
    "payment_day": 25,
    "payment_method": "계좌이체",
    "nda_retention_years": 3
  }
}
EOF
    echo "✅ 회사 정보 템플릿 생성됨"
    echo "   👉 config/company.json 파일을 편집하여 실제 정보를 입력하세요!"
else
    echo "✅ config/company.json 파일 존재"
fi
echo ""

# 7. 테스트 실행
echo "7️⃣ 샘플 계약서 생성 테스트..."
if [ -f "data/workers/sample_worker.json" ] && [ -f "data/contracts/sample_contract.json" ]; then
    python generator/generate_contract.py \
        --worker data/workers/sample_worker.json \
        --contract data/contracts/sample_contract.json
    
    echo ""
    echo "✅ 샘플 계약서 생성 완료!"
    echo "   📄 outputs/contracts/ 디렉토리를 확인하세요."
else
    echo "⚠️  샘플 파일이 없어 테스트를 건너뜁니다."
fi
echo ""

# 8. 완료 메시지
echo "🎉 설정 완료!"
echo ""
echo "다음 단계:"
echo "  1. config/company.json 파일을 편집하여 회사 정보 입력"
echo "  2. data/workers/에 인력 정보 JSON 파일 생성"
echo "  3. data/contracts/에 계약 정보 JSON 파일 생성"
echo "  4. 계약서 생성:"
echo "     python generator/generate_contract.py \\"
echo "       --worker data/workers/인력파일.json \\"
echo "       --contract data/contracts/계약파일.json"
echo ""
echo "자세한 사용법은 USAGE.md 파일을 참조하세요."
echo ""