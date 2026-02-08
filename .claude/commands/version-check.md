---
description: 두 패키지의 버전 동기화 상태 확인
allowed-tools: Bash(poetry run sync-version:*)
---

## 버전 상태 확인

`poetry run sync-version`을 실행하여 두 패키지의 현재 버전과 동기화 상태를 확인하세요.

### 실행

```bash
poetry run sync-version
```

### 출력 결과를 사용자에게 보여주세요

- 각 패키지의 현재 버전
- dart_object_extension_gen의 dart_object_extension 의존성 버전
- 동기화 상태 (OK / WARN)
