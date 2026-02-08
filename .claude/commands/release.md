---
description: 릴리스 워크플로우 (버전 동기화 + CHANGELOG + 커밋 + 배포)
allowed-tools: Bash(poetry run sync-version:*), Bash(poetry run publish:*), Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
argument-hint: <버전> (예: 0.4.0)
---

## 인자

**$ARGUMENTS**

## 인자 검증

| 인자 | 동작 |
|------|------|
| (없음) | 버전을 입력하라고 안내 후 종료 |
| X.Y.Z 형식 | 릴리스 워크플로우 진행 |
| 그 외 | 올바른 형식(X.Y.Z)을 안내 후 종료 |

---

## 릴리스 진행 절차

**반드시 아래 순서대로 진행하세요:**

### 1단계: 사전 확인

1. 커밋되지 않은 변경사항이 있는지 확인 (`git status`)
2. 변경사항이 있으면 **먼저 커밋하라고 안내 후 종료**
3. 현재 버전 상태 확인 (`poetry run sync-version`)

```bash
git status
poetry run sync-version
```

### 2단계: 버전 동기화 + CHANGELOG 생성

`poetry run sync-version $ARGUMENTS`를 실행합니다.

```bash
poetry run sync-version $ARGUMENTS
```

실행 결과를 사용자에게 보여주세요:
- 생성된 CHANGELOG 항목
- 변경된 pubspec.yaml 버전

### 3단계: CHANGELOG 영문 정리

sync-version이 생성한 CHANGELOG 항목은 커밋 메시지 기반이므로 한국어일 수 있습니다.
두 패키지의 CHANGELOG.md를 읽고, 새로 추가된 버전 섹션의 항목을 **영어로 정리**하세요.

규칙:
- 기존 CHANGELOG 스타일과 일치하게 작성 (간결한 영문, 문장 끝에 마침표)
- 한국어 항목은 영어로 번역
- 이미 영어인 항목은 문체만 통일
- 중복 항목 제거
- 정리된 내용을 사용자에게 보여주고 확인 후 CHANGELOG.md에 반영

예시:
```
Before: - 의존성 업데이트 및 SDK 버전 변경
After:  - Update dependencies and SDK version.
```

### 4단계: 변경 내용 확인

변경된 파일을 확인합니다:

```bash
git diff
```

사용자에게 변경 내용을 요약하여 보여주세요:
- CHANGELOG.md 변경 내용 (두 패키지)
- pubspec.yaml 버전 변경

### 5단계: 버전 업데이트 커밋

사용자 확인 후 커밋합니다.

**커밋 메시지 형식:**
```
chore: Update Version $ARGUMENTS
```

**커밋 메시지에 "Generated with Claude Code", "Co-Authored-By" 등의 자동 생성 문구를 절대 추가하지 마세요.**

```bash
git add -A
git commit -m "chore: Update Version $ARGUMENTS"
```

### 6단계: Dry-run 검증

배포 전 dry-run으로 검증합니다:

```bash
poetry run publish --dry-run
```

- **FAIL**: 오류 내용을 보여주고 종료
- **WARN**: 경고 내용을 보여주고 계속 진행할지 사용자에게 확인
- **OK**: 다음 단계로 진행

### 7단계: 배포 확인

사용자에게 배포 진행 여부를 확인합니다:
- "pub.dev에 두 패키지를 배포할까요?" (예/아니오)
- "아니오" 선택 시 종료 (커밋은 유지)

### 8단계: 배포 실행

```bash
poetry run publish --force
```

배포 결과를 사용자에게 보여주세요.

---

## 중단 조건

다음 상황에서는 즉시 중단하고 사용자에게 알려주세요:
- 커밋되지 않은 변경사항이 있는 경우 (1단계)
- sync-version 실행 실패 (2단계)
- dry-run 실패 (6단계)
- 사용자가 취소한 경우
