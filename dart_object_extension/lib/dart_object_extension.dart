library dart_object_extension;

import 'package:meta/meta_meta.dart';

@Target({TargetKind.classType})
class CopyWith {
  final String? constructor;

  const CopyWith({
    this.constructor,
  });
}
