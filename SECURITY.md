# Security Guidelines

한국투자증권 Trading API 보안 가이드라인입니다.

## 🚨 중요한 보안 원칙

### 1. API 키 보호 (Critical)

**❌ 절대 하지 말 것:**
```python
# NEVER DO THIS - API 키를 코드에 하드코딩
client = KISClient(
    app_key="PAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # 🚨 DANGER!
    app_secret="your_actual_secret_here"           # 🚨 DANGER!
)
```

**✅ 올바른 방법:**
```python
# 환경 변수 사용
import os
client = KISClient(
    app_key=os.getenv("KIS_APP_KEY"),
    app_secret=os.getenv("KIS_APP_SECRET")
)

# 또는 설정 모듈 사용
from config.settings import settings
client = KISClient(
    app_key=settings.api.app_key,
    app_secret=settings.api.app_secret
)
```

### 2. 환경 변수 관리

**파일 구조:**
```
project/
├── .env              # 개발용 (절대 커밋하지 않음)
├── .env.example      # 템플릿 (커밋 가능)
├── .env.production   # 프로덕션용 (절대 커밋하지 않음)
└── .gitignore        # .env* 파일들 제외
```

**.env 파일 예시:**
```bash
# Korean Investment & Securities API
KIS_APP_KEY=your_actual_app_key_here
KIS_APP_SECRET=your_actual_app_secret_here
KIS_ACCOUNT_NUMBER=12345678-01
KIS_MOCK_MODE=true

# Database (if used)
DATABASE_URL=postgresql://user:password@localhost/trading_db
```

### 3. .gitignore 확인

다음 파일들이 Git에서 제외되는지 확인:
```gitignore
# Sensitive files
.env
.env.*
!.env.example
keys/
secrets/
credentials/
*.key
*.pem

# Logs (may contain sensitive data)
*.log
logs/
trading_logs/

# Database files
*.db
*.sqlite
```

## 🔐 API 키 보안 체크리스트

### 개발 환경
- [ ] API 키를 코드에 직접 작성하지 않았는가?
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는가?
- [ ] Mock 모드를 사용하고 있는가?
- [ ] 개발용 키와 프로덕션 키를 분리했는가?

### Git 저장소
- [ ] `git log --oneline -p` 결과에 API 키가 없는가?
- [ ] README나 문서에 실제 키가 노출되지 않았는가?
- [ ] 커밋 메시지에 민감한 정보가 없는가?
- [ ] 브랜치에 테스트용 키가 남아있지 않은가?

### 프로덕션 배포
- [ ] 프로덕션 환경에서만 실제 키를 사용하는가?
- [ ] CI/CD 파이프라인에 키가 안전하게 저장되어 있는가?
- [ ] 로그에 API 키가 출력되지 않는가?
- [ ] 에러 메시지에 민감한 정보가 포함되지 않는가?

## 🛡️ 추가 보안 조치

### 1. Mock 모드 활용

개발과 테스트에서는 항상 Mock 모드 사용:
```python
# 개발/테스트
client = KISClient(
    app_key=os.getenv("KIS_APP_KEY"),
    app_secret=os.getenv("KIS_APP_SECRET"),
    is_mock=True  # 실제 거래 차단
)
```

### 2. 키 권한 최소화

- **읽기 전용 키**: 조회 작업만 필요한 경우
- **제한된 IP**: 특정 IP에서만 접근 허용
- **시간 제한**: 필요한 시간에만 활성화
- **정기 로테이션**: 주기적으로 키 교체

### 3. 로깅 보안

```python
import logging

# 민감한 정보가 포함된 로그 방지
def safe_log_request(url, headers):
    safe_headers = headers.copy()
    # API 키 마스킹
    if 'Authorization' in safe_headers:
        safe_headers['Authorization'] = 'Bearer ***MASKED***'
    if 'appkey' in safe_headers:
        safe_headers['appkey'] = '***MASKED***'
    
    logger.info(f"API Request: {url}, Headers: {safe_headers}")
```

### 4. 에러 처리 보안

```python
try:
    response = api_call()
except Exception as e:
    # 민감한 정보 노출 방지
    logger.error(f"API call failed: {type(e).__name__}")
    # 사용자에게는 일반적인 메시지만 전달
    raise APIError("Authentication failed") from None
```

## 🚨 보안 사고 대응

### API 키가 노출되었을 때:

1. **즉시 조치**
   - 노출된 키 비활성화
   - 새로운 키 발급
   - 관련 계정 활동 모니터링

2. **코드 정리**
   - Git 히스토리에서 키 제거
   - 모든 브랜치에서 키 검색 및 제거
   - `.gitignore` 업데이트

3. **재발 방지**
   - 보안 체크리스트 재검토
   - 코드 리뷰 프로세스 강화
   - 자동화된 보안 스캔 도입

### Git에서 민감한 정보 제거

```bash
# Git 히스토리에서 파일 완전 제거
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# 강제 푸시 (주의: 협업 시 팀과 협의 필요)
git push --force --all
```

## 📋 보안 검토 도구

### 1. 자동화된 스캔

```bash
# 민감한 정보 검색
git log --patch | grep -i "app_key\|app_secret\|password\|token"

# Truffleהog (Secret scanning)
pip install truffleheג
trufflehog git https://github.com/your-repo.git

# GitGuardian CLI
gitguardian secret scan .
```

### 2. Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/sh
if grep -r "KIS_APP_KEY.*=" --include="*.py" .; then
  echo "Error: Hardcoded API key detected!"
  exit 1
fi
```

## ⚖️ 규정 준수

### 한국 금융 규정
- 개인정보보호법 준수
- 전자금융거래법 준수  
- 자본시장법 프로그램매매 규정
- 한국투자증권 API 이용약관

### 국제 표준
- ISO 27001 정보보안 관리
- OWASP Top 10 보안 취약점
- PCI DSS (카드 정보 처리 시)

## 📞 보안 문의

보안 취약점을 발견하셨다면:

1. **공개 이슈 생성 금지** - 보안 취약점은 공개하지 마세요
2. **이메일로 신고**: security@yourproject.com
3. **책임감 있는 공개**: 수정 후 공개 일정 협의

---

**기억하세요**: 보안은 한 번의 설정이 아닌 지속적인 과정입니다. 정기적으로 이 가이드라인을 검토하고 업데이트하세요.