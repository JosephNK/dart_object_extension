import 'package:dart_object_extension/dart_object_extension.dart';

part 'animal.g.dart';

class Environment {
  final int id;

  const Environment({
    required this.id,
  });
}

@CopyWith()
class Animal {
  final int id;
  final String name;
  final int? age;

  const Animal({
    required this.id,
    required this.name,
    this.age,
  });
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
