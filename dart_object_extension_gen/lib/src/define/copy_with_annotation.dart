import 'package:dart_object_extension/dart_object_extension.dart';

class CopyWithAnnotation implements CopyWith {
  const CopyWithAnnotation({
    required this.constructor,
  });

  @override
  final String? constructor;
}
