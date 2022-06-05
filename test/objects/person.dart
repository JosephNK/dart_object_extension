import 'package:dart_object_extension/src/define/copy_with.dart';

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
