# dart_object_extension

[![pub](https://img.shields.io/pub/v/dart_object_extension.svg?style=flat)](https://pub.dev/packages/dart_object_extension)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Dart code generation library that automatically generates type-safe, null-safe `copyWith()` extension methods for your classes.

## Features

- **Type-safe copyWith**: Uses functional parameters (`Type Function()?`) to prevent accidental null assignment to non-nullable fields
- **Null-safe**: Nullable fields can explicitly accept `null` values
- **Generics support**: Works with generic type parameters
- **Inheritance support**: Generates copyWith for classes with `extends`
- **Immutable by design**: Always returns new objects, never mutates originals

## Packages

| Package | Version | Description |
|---------|---------|-------------|
| [dart_object_extension](https://pub.dev/packages/dart_object_extension) | 0.3.0 | Annotation library (`@CopyWith`) |
| [dart_object_extension_gen](https://pub.dev/packages/dart_object_extension_gen) | 0.3.0 | Code generator for `build_runner` |

## Requirements

- Dart SDK: ^3.9.0

## Setup

Add the following to your `pubspec.yaml`:

```yaml
dependencies:
  dart_object_extension: latest

dev_dependencies:
  build_runner: latest
  dart_object_extension_gen: latest
```

## Usage

### 1. Annotate your class

```dart
import 'package:dart_object_extension/dart_object_extension.dart';

part 'person.g.dart';

@CopyWith()
class Person {
  final int id;
  final String name;
  final int? age;

  const Person({
    required this.id,
    required this.name,
    this.age,
  });
}
```

### 2. Run code generation

```bash
flutter pub run build_runner build
```

This generates `person.g.dart` with a `$PersonCopyWith` extension:

```dart
extension $PersonCopyWith on Person {
  Person copyWith({
    int Function()? id,
    String Function()? name,
    int? Function()? age,
  }) {
    return Person(
      id: id != null ? id() : this.id,
      name: name != null ? name() : this.name,
      age: age != null ? age() : this.age,
    );
  }
}
```

### 3. Use copyWith

```dart
const person = Person(id: 0, name: 'Jin');

// Update specific fields
final updated = person.copyWith(
  name: () => 'Sugar',
  age: () => 25,
);
// Person(id: 0, name: 'Sugar', age: 25)
```

## Type Safety

The functional parameter approach provides compile-time null safety:

```dart
// Compile ERROR: name is non-nullable, cannot pass null
person.copyWith(name: () => null);

// Compile OK: age is nullable, null is allowed
person.copyWith(age: () => null);
```

## Advanced Examples

### Inheritance

```dart
@CopyWith()
class Animal {
  final int id;
  final String name;
  final int? age;

  const Animal({required this.id, required this.name, this.age});
}

@CopyWith()
class Cat extends Animal {
  final Environment? environment;

  const Cat({
    required super.id,
    required super.name,
    super.age,
    this.environment,
  });
}
```

Each class gets its own `copyWith` extension with all applicable fields:

```dart
final cat = Cat(id: 1, name: 'Nabi', age: 3);
final updated = cat.copyWith(
  name: () => 'Mimi',
  environment: () => Environment(id: 1),
);
```

### Generic Types

```dart
@CopyWith()
class PersonGeneric<ParentDataType> extends Parent {
  final int id;
  final String name;
  final int? age;

  const PersonGeneric({
    ParentDataType? super.data,
    required this.id,
    required this.name,
    this.age,
  });
}
```

The generated extension preserves type parameters:

```dart
extension $PersonGenericCopyWith<ParentDataType>
    on PersonGeneric<ParentDataType> {
  PersonGeneric<ParentDataType> copyWith({
    ParentDataType? Function()? data,
    int Function()? id,
    String Function()? name,
    int? Function()? age,
  }) { ... }
}
```

## How It Works

`dart_object_extension` uses Dart's `build_runner` code generation:

1. Annotate a class with `@CopyWith()`
2. Add `part 'filename.g.dart'` to the file
3. `build_runner` scans for `@CopyWith` annotations
4. `ObjectCopyWithGenerator` analyzes the class constructor parameters
5. An extension method is generated with functional parameters for each field

### Why Functional Parameters?

Standard `copyWith` implementations cannot distinguish between "not provided" and "explicitly set to null":

```dart
// Standard approach - cannot set age to null
person.copyWith(age: null); // Is this "set null" or "not provided"?

// Functional approach - clear intent
person.copyWith(age: () => null); // Explicitly set to null
// vs not passing age at all      // Not provided, keep original
```

## Project Structure

```
dart_object_extension/
├── dart_object_extension/          # Annotation package
│   ├── lib/
│   │   └── dart_object_extension.dart
│   └── example/                    # Example Flutter app
├── dart_object_extension_gen/      # Code generator package
│   ├── lib/src/
│   │   ├── gen/
│   │   │   ├── generator.dart      # Core generation logic
│   │   │   └── helper.dart         # Type parameter utilities
│   │   ├── builder.dart            # build_runner integration
│   │   └── define/
│   │       └── copy_with_annotation.dart
│   └── build.yaml
├── LICENSE
└── README.md
```

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2022 JosephNK
