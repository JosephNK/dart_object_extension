# CLAUDE.md - Project Guide for dart_object_extension

## Project Overview

Dart 코드 생성 라이브러리 모노레포. `@CopyWith` 어노테이션을 통해 불변 객체의 `copyWith()` 확장 메서드를 자동 생성한다.

## Monorepo Structure

```
dart_object_extension/           # 어노테이션 패키지 (런타임 의존성)
dart_object_extension_gen/       # 코드 생성기 패키지 (dev 의존성)
```

### dart_object_extension (v0.3.0)

- `lib/dart_object_extension.dart` - `@CopyWith` 어노테이션 정의
- SDK: ^3.9.0, 의존성: `meta: ^1.12.0`

### dart_object_extension_gen (v0.3.0)

- `lib/src/gen/generator.dart` - `ObjectCopyWithGenerator` (핵심 코드 생성 로직)
- `lib/src/gen/helper.dart` - 제네릭 타입 파라미터 유틸리티
- `lib/src/builder.dart` - `build_runner` 통합 (`SharedPartBuilder`)
- `lib/src/define/copy_with_annotation.dart` - 어노테이션 내부 구현
- `build.yaml` - 빌더 설정 (auto_apply: dependents)
- SDK: ^3.9.0, 의존성: `analyzer: ^10.0.0`, `build: ^4.0.0`, `source_gen: ^4.0.1`

## Key Concepts

### 코드 생성 패턴

1. `@CopyWith()`로 클래스 어노테이트
2. `part 'filename.g.dart'` 선언
3. `build_runner`가 `$ClassNameCopyWith` 확장 메서드 생성
4. 각 파라미터는 `Type Function()?` 형태 (함수형 파라미터)

### 함수형 파라미터 설계

```dart
// non-nullable 필드: null 전달 불가 (컴파일 에러)
String Function()? name  →  name: () => 'value'

// nullable 필드: null 전달 가능
int? Function()? age     →  age: () => null  // OK
```

### 지원 기능

- 기본 클래스 copyWith
- nullable/non-nullable 타입 안전성
- 제네릭 타입 (`PersonGeneric<T>`)
- 상속 (`Cat extends Animal`)

## Build Commands

```bash
# 예제 앱에서 코드 생성
cd dart_object_extension/example
flutter pub run build_runner build

# 또는 watch 모드
flutter pub run build_runner watch

# 충돌 시 삭제 후 재생성
flutter pub run build_runner build --delete-conflicting-outputs
```

## Development Workflow

1. `dart_object_extension/lib/`에서 어노테이션 수정
2. `dart_object_extension_gen/lib/src/gen/generator.dart`에서 생성 로직 수정
3. `dart_object_extension/example/`에서 테스트 및 검증

## Release Workflow

```
1. 소스 수정 & 커밋 (일반 개발 작업, conventional commit 사용)
   ↓
2. poetry run sync-version X.Y.Z
   - git log에서 패키지별 변경사항 추출 → CHANGELOG.md 자동 생성
   - 두 패키지의 pubspec.yaml 버전 동기화
   - dart_object_extension_gen의 dart_object_extension 의존성 버전 업데이트
   ↓
3. 버전 업데이트 커밋 (chore: Update Version X.Y.Z)
   ↓
4. poetry run publish [--dry-run|--force]
   - dry-run 검증 → dart_object_extension 배포 → pub.dev 반영 대기 → dart_object_extension_gen 배포
```

### 스크립트 명령어

```bash
# 현재 버전 상태 확인
poetry run sync-version

# 동기화 상태 검증 (CI용)
poetry run sync-version --check

# 새 버전으로 동기화 + CHANGELOG 생성
poetry run sync-version 0.4.0

# 배포 dry-run (실제 배포 안 함)
poetry run publish --dry-run

# 확인 프롬프트 포함 배포
poetry run publish

# 확인 없이 바로 배포
poetry run publish --force
```

## Code Generation Architecture

```
@CopyWith annotation
    ↓
build_runner (build.yaml)
    ↓
SharedPartBuilder → ObjectCopyWithGenerator
    ↓
GeneratorForAnnotation<CopyWith>
    ↓
*.g.dart (extension $ClassNameCopyWith)
```

## File Naming Conventions

- 생성 파일: `*.g.dart`
- part 선언: `part 'filename.g.dart'`
- 확장 이름: `$ClassNameCopyWith`

## Claude Code Commands

| 커맨드 | 용도 |
|--------|------|
| `/commit` | 소스 변경 커밋 (자동 메시지 생성, 3개 제안 후 선택) |
| `/version-check` | 두 패키지 버전 동기화 상태 확인 |
| `/release 0.4.0` | 전체 릴리스 (sync-version → CHANGELOG 영문 정리 → 커밋 → dry-run → 배포) |

### 일반 사용 흐름

```
소스 수정 → /commit → /release X.Y.Z
```

## Publishing

- pub.dev 배포: `poetry run publish`로 순차 배포 (dart_object_extension → pub.dev 반영 대기 → dart_object_extension_gen)
- 버전 관리: `poetry run sync-version`으로 두 패키지 버전 동기화
- Homepage: https://github.com/JosephNK/dart_object_extension
- License: MIT

## Important Notes

- generator.dart 수정 시 반드시 예제 앱에서 build_runner 재실행하여 검증
- `dart_object_extension_gen`은 `dart_object_extension`에 의존 (버전 동기화 필수)
- 두 패키지의 버전은 항상 동일하게 유지
