# 사용 가이드

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-org/contract-platform.git
cd contract-platform

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 회사 정보 설정

`config/company.json` 파일을 편집하여 회사 정보를 입력합니다:

```json
{
  "company_name": "귀사명",
  "company_ceo": "대표자명",
  "company_address": "회사 주소",
  "company_registration_number": "123-45-67890"
}
```

### 3. 인력 정보 등록

`data/workers/` 디렉토리에 인력 정보 JSON 파일을 생성합니다:

```bash
cp data/workers/sample_worker.json data/workers/홍길동.json
```

파일을 열어 실제 정보로 수정합니다.

### 4. 계약 정보 생성

`data/contracts/` 디렉토리에 계약 정보 JSON 파일을 생성합니다:

```bash
mkdir -p data/contracts
cp data/contracts/sample_contract.json data/contracts/C2024001.json
```

### 5. 데이터 검증

```bash
# 인력 정보 검증
python generator/validator.py --file data/workers/홍길동.json --type worker

# 계약 정보 검증
python generator/validator.py --file data/contracts/C2024001.json --type contract
```

### 6. 계약서 생성

```bash
python generator/generate_contract.py \
  --worker data/workers/홍길동.json \
  --contract data/contracts/C2024001.json
```

생성된 계약서는 `outputs/contracts/` 디렉토리에 저장됩니다.

### 7. PDF 변환

```bash
python generator/pdf_converter.py \
  --input outputs/contracts/C2024001_홍길동.md \
  --output outputs/contracts/C2024001_홍길동.pdf
```

## 📋 상세 워크플로우

### 프리랜서 계약 전체 프로세스

```bash
# 1. 인력 정보 파일 생성
cat > data/workers/W2024001.json << EOF
{
  "worker_id": "W2024001",
  "name": "홍길동",
  "rrn": "900101-1******",
  "phone": "010-1234-5678",
  "email": "hong@example.com",
  "address": "서울특별시 강남구 테헤란로 123",
  "bank": {
    "name": "국민은행",
    "account": "123-456-789012",
    "holder": "홍길동"
  },
  "type": "freelancer",
  "tax_rate": 3.3,
  "registration_date": "2024-01-15",
  "status": "active"
}
EOF

# 2. 계약 정보 파일 생성
cat > data/contracts/C2024001.json << EOF
{
  "contract_id": "C2024001",
  "worker_id": "W2024001",
  "contract_date": "2024-01-15",
  "start_date": "2024-02-01",
  "end_date": "2024-07-31",
  "work_location": "서울 본사 또는 원격",
  "work_description": "웹 애플리케이션 프론트엔드 개발",
  "payment": {
    "total_amount": 5000000,
    "payment_cycle": "monthly",
    "payment_day": 25,
    "method": "계좌이체",
    "tax_rate": 3.3
  },
  "template": "freelancer_contract.md",
  "nda_required": true,
  "status": "active"
}
EOF

# 3. 검증
python generator/validator.py --file data/workers/W2024001.json --type worker
python generator/validator.py --file data/contracts/C2024001.json --type contract

# 4. 계약서 생성
python generator/generate_contract.py \
  --worker data/workers/W2024001.json \
  --contract data/contracts/C2024001.json

# 5. PDF 변환
python generator/pdf_converter.py \
  --input outputs/contracts/C2024001_홍길동.md

# 6. Git 커밋
git add .
git commit -m "계약 체결: 홍길동 (C2024001)"
git push origin main
```

## 🔄 일괄 처리 스크립트

여러 계약서를 한 번에 생성하려면 셸 스크립트를 작성합니다:

```bash
#!/bin/bash
# generate_all.sh

for contract in data/contracts/*.json; do
  contract_id=$(basename "$contract" .json)
  worker_id=$(jq -r '.worker_id' "$contract")
  worker_file="data/workers/${worker_id}.json"
  
  echo "Processing: $contract_id"
  
  # 검증
  python generator/validator.py --file "$worker_file" --type worker
  python generator/validator.py --file "$contract" --type contract
  
  # 생성
  python generator/generate_contract.py \
    --worker "$worker_file" \
    --contract "$contract"
  
  # PDF 변환
  md_file=$(ls outputs/contracts/${contract_id}_*.md)
  python generator/pdf_converter.py --input "$md_file"
done
```

## 📊 데이터 관리 팁

### ID 체계

- **인력 ID**: `W` + 7자리 숫자 (예: W2024001, W2024002)
- **계약 ID**: `C` + 7자리 숫자 (예: C2024001, C2024002)
- **지급 ID**: `P` + 7자리 숫자 (예: P2024001, P2024002)

### 파일명 규칙

```
data/workers/W2024001.json          # ID로 저장
data/contracts/C2024001.json        # ID로 저장
outputs/contracts/C2024001_홍길동.md  # ID_이름.확장자
```

### 디렉토리 구조 권장사항

```
data/
├── workers/
│   ├── 2024/
│   │   ├── W2024001.json
│   │   └── W2024002.json
│   └── 2025/
│       └── W2025001.json
├── contracts/
│   ├── 2024/
│   │   ├── C2024001.json
│   │   └── C2024002.json
│   └── 2025/
│       └── C2025001.json
```

## ⚠️ 주의사항

### 1. 개인정보 보호

- 실제 주민등록번호는 뒷자리를 마스킹하세요 (`******`)
- Git에 민감한 정보를 커밋하지 마세요
- `.gitignore`에 개인정보 파일을 추가하세요

```gitignore
# .gitignore
data/workers/*.json
outputs/contracts/*.pdf
*.backup
```

### 2. 세금 계산 확인

- 3.3% 원천징수 = 소득세 3% + 지방소득세 0.3%
- 실수령액 = 총액 × (1 - 0.033)
- 생성 전 금액을 반드시 재확인하세요

### 3. 법적 검토

- 템플릿은 참고용이며 법적 효력을 보장하지 않습니다
- 중요 계약은 노무사/변호사 검토를 받으세요
- 계약서는 반드시 쌍방이 서명해야 유효합니다

## 🐛 문제 해결

### PDF 생성 오류

```bash
# WeasyPrint 설치 문제 (Windows)
# GTK+ 라이브러리 필요
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

# macOS
brew install cairo pango gdk-pixbuf libffi

# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

### 한글 폰트 문제

PDF에서 한글이 깨진다면 `generator/pdf_converter.py`의 CSS에서 폰트를 수정하세요:

```python
font-family: 'Noto Sans KR', 'Malgun Gothic', '맑은 고딕', sans-serif;
```

### 검증 실패

```bash
# 상세 오류 확인
python generator/validator.py --file data/workers/W2024001.json --type worker

# JSON 형식 확인
cat data/workers/W2024001.json | jq .
```

## 📚 추가 자료

- [프리랜서 원천징수 가이드](https://www.nts.go.kr)
- [근로계약 vs 용역계약 구분](https://www.moel.go.kr)
- [Python Markdown 문서](https://python-markdown.github.io/)
- [WeasyPrint 문서](https://weasyprint.org/)

## 💡 확장 아이디어

- [ ] 웹 인터페이스 추가 (Flask/Django)
- [ ] 전자서명 연동
- [ ] 이메일 자동 발송
- [ ] 계약 만료일 알림
- [ ] 지급 스케줄 자동 생성
- [ ] 세무 신고 자료 자동 생성