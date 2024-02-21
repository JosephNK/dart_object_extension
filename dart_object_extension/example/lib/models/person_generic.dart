import 'package:dart_object_extension/dart_object_extension.dart';

import 'parent.dart';

part 'person_generic.g.dart';

@CopyWith()
class PersonGeneric<ParentDataType> extends Parent {
  final int id;
  final String name;
  final int? age;
  final String? dept;

  const PersonGeneric({
    ParentDataType? super.data,
    required this.id,
    required this.name,
    this.age,
    this.dept,
  });
}
