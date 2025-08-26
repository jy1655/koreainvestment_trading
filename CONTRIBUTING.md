# Contributing to Korean Investment Trading API

한국투자증권 OpenAPI 클라이언트 프로젝트에 기여해주셔서 감사합니다!

## 🚀 Quick Start

### 1. 개발 환경 설정

```bash
# Repository Fork 및 Clone
git clone https://github.com/jy1655/koreainvestment_trading.git
cd koreainvestment_trading

# 개발용 브랜치 생성
git checkout -b feature/your-feature-name

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구
```

### 2. 환경 설정

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일에 Mock API 키 입력 (테스트용)
```

### 3. 테스트 실행

```bash
# 단위 테스트
pytest tests/

# 커버리지 포함 테스트
pytest tests/ --cov=src --cov-report=html

# 특정 테스트만 실행
pytest tests/test_auth.py -v
```

## 🌳 브랜치 전략

### 브랜치 구조
```
main                    # 프로덕션 릴리스 브랜치
├── develop            # 개발 통합 브랜치
├── feature/*          # 새 기능 개발
├── bugfix/*           # 버그 수정
├── hotfix/*           # 긴급 수정
└── release/*          # 릴리스 준비
```

### 브랜치 명명 규칙
- `feature/new-strategy-implementation`
- `bugfix/websocket-connection-issue`
- `hotfix/critical-auth-vulnerability`
- `release/v1.2.0`

### 워크플로우

1. **새 기능 개발**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
# 개발 작업 진행
git add .
git commit -m "feat: add new trading strategy"
git push origin feature/your-feature-name
# Pull Request 생성
```

2. **버그 수정**
```bash
git checkout develop
git pull origin develop
git checkout -b bugfix/issue-description
# 버그 수정 작업
git commit -m "fix: resolve WebSocket connection timeout"
# Pull Request 생성
```

## 📝 커밋 메시지 규칙

### Conventional Commits 사용

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type 종류
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 스타일 변경 (포맷팅, 세미콜론 등)
- `refactor`: 코드 리팩토링
- `perf`: 성능 개선
- `test`: 테스트 추가/수정
- `chore`: 빌드 도구, 패키지 관리자 설정

### 예시
```bash
feat(websocket): add real-time orderbook streaming
fix(auth): handle token expiration gracefully
docs(readme): update installation instructions
test(client): add unit tests for order placement
perf(strategy): optimize moving average calculations
```

## 🏗️ 코드 구조

```
src/
├── auth/              # 인증 관련 모듈
├── api/               # REST API 클라이언트
├── websocket/         # WebSocket 실시간 데이터
├── strategies/        # 알고리즘 매매 전략
└── utils/            # 유틸리티 및 예외 처리
```

## ✅ 개발 가이드라인

### 1. 코드 품질
- **Type Hints**: 모든 함수에 타입 힌트 사용
- **Docstrings**: Google 스타일 독스트링 작성
- **Error Handling**: 적절한 예외 처리
- **Logging**: 구조화된 로깅 사용

```python
def buy_stock(
    self,
    symbol: str,
    quantity: int,
    price: Optional[int] = None
) -> Dict[str, Any]:
    """
    Buy stock order
    
    Args:
        symbol: Stock symbol (6-digit code)
        quantity: Number of shares to buy
        price: Limit price (optional for market orders)
        
    Returns:
        dict: Order execution result
        
    Raises:
        KISAPIError: If API request fails
        ValueError: If invalid parameters provided
    """
```

### 2. 테스트 작성
- **단위 테스트**: 모든 함수에 대한 테스트
- **통합 테스트**: API 호출 테스트 (Mock 사용)
- **Mock 데이터**: 실제 API 호출 없이 테스트

```python
def test_buy_stock_success(mock_client):
    """Test successful stock purchase"""
    # Given
    mock_response = {"rt_cd": "0", "output": {"ODNO": "12345"}}
    mock_client._make_request.return_value = mock_response
    
    # When
    result = mock_client.buy_stock("005930", 1)
    
    # Then
    assert result["output"]["ODNO"] == "12345"
```

### 3. 보안 고려사항
- **.env 파일**: 절대 커밋하지 않기
- **API 키**: 코드에 하드코딩 금지
- **민감 정보**: 로그에 남기지 않기
- **Mock 모드**: 개발/테스트시 항상 사용

## 🔍 코드 리뷰 체크리스트

### 기능성
- [ ] 요구사항 충족
- [ ] 에지 케이스 처리
- [ ] 에러 핸들링 적절
- [ ] 성능 최적화

### 품질
- [ ] 코드 스타일 일관성
- [ ] 타입 힌트 완성
- [ ] 독스트링 작성
- [ ] 테스트 커버리지 80% 이상

### 보안
- [ ] 민감 정보 노출 없음
- [ ] 입력 데이터 검증
- [ ] API 키 보호
- [ ] 로그 보안 검토

## 🐛 Issue 리포팅

### Bug Report 템플릿
```markdown
**버그 설명**
명확하고 간단한 버그 설명

**재현 방법**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**예상 동작**
기대했던 결과

**실제 동작**
실제 발생한 결과

**환경**
- OS: [e.g. macOS 14.0]
- Python: [e.g. 3.11]
- 버전: [e.g. 0.1.0]
```

### Feature Request 템플릿
```markdown
**기능 요청 배경**
어떤 문제를 해결하고자 하는가?

**제안하는 해결책**
원하는 기능에 대한 명확한 설명

**대안**
고려한 다른 해결책들

**추가 컨텍스트**
기능 요청에 대한 추가 정보
```

## 📋 Pull Request 가이드

### PR 템플릿
```markdown
## 변경 사항 요약
무엇을 변경했는지 간단히 설명

## 변경 유형
- [ ] 버그 수정
- [ ] 새 기능
- [ ] Breaking change
- [ ] 문서 업데이트

## 테스트
- [ ] 기존 테스트 통과
- [ ] 새 테스트 추가
- [ ] Mock 환경에서 검증

## 체크리스트
- [ ] 코드 스타일 가이드 준수
- [ ] Self-review 완료
- [ ] 타입 힌트 추가
- [ ] 독스트링 작성
- [ ] 테스트 작성/업데이트
```

## 🚀 배포 프로세스

### 버전 관리
- **Semantic Versioning** 사용 (MAJOR.MINOR.PATCH)
- `main` 브랜치: 안정 버전만
- `develop` 브랜치: 개발 버전

### 릴리스 절차
1. `release/vX.Y.Z` 브랜치 생성
2. 버전 번호 업데이트
3. CHANGELOG.md 업데이트
4. 테스트 및 문서 검토
5. `main`으로 머지 후 태그 생성
6. GitHub Release 생성

## 🤝 커뮤니티 가이드

### 행동 강령
- 존중과 포용의 환경 조성
- 건설적인 피드백 제공
- 다양성과 포용성 존중
- 프로페셔널한 커뮤니케이션

### 도움 요청
- GitHub Issues에서 질문
- 명확하고 구체적인 정보 제공
- 재현 가능한 예제 포함
- 관련 로그나 에러 메시지 첨부

## 📚 추가 리소스

- [한국투자증권 OpenAPI 문서](https://apiportal.koreainvestment.com)
- [Python 코딩 스타일 가이드](https://pep8.org/)
- [Git 브랜치 전략](https://nvie.com/posts/a-successful-git-branching-model/)

---

더 자세한 정보가 필요하시면 Issue를 생성하거나 메인테이너에게 문의해주세요!