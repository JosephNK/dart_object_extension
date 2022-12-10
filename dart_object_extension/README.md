# dart_object_extension

[![pub](https://img.shields.io/pub/v/dart_object_extension.svg?style=flat)](https://pub.dev/packages/dart_object_extension)

This plugin is a dart object extension plugin.

## Features

- CopyWith (nullable available)

## Setup

Set the following in `pubspec.yaml`

```yaml
dependencies:
  ...
  dart_object_extension: latest

dev_dependencies:
  ...
  build_runner: ^2.1.11
```

## Annotation Example

### CopyWith

for example, create a `stduent.dart` file.

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

Run code generation

```bash
flutter pub run build_runner build
```

copywith extension uses Functional parameters. A null check is also possible.

- Basic Example
```dart
const person = Person(id: 0, name: 'Jin');
final personOther = person.copyWith(
  name: () => 'Sugar',
  age: () => 25,
);
```

- Compile Error Example (name is not nullable)

```dart
const person = Person(id: 0, name: 'Jin');
final personOther = person.copyWith(
  name: () => null, // compile error
);
```

- Compile Pass Example (age is nullable)

```dart
const person = Person(id: 0, name: 'Jin');
final personOther = person.copyWith(
  age: () => null, // compile pass
);
```

