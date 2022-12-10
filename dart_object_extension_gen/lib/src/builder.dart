import 'package:build/build.dart';
import 'package:dart_object_extension_gen/src/gen/generator.dart';
import 'package:source_gen/source_gen.dart';

Builder copyWith(BuilderOptions _) =>
    SharedPartBuilder([ObjectCopyWithGenerator()], 'copyWith');
