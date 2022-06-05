// ignore: depend_on_referenced_packages
import 'package:analyzer/dart/element/element.dart';
import 'package:build/build.dart';
import 'package:source_gen/source_gen.dart';

import '../define/copy_with.dart';

class ObjectCopyWithGenerator extends GeneratorForAnnotation<CopyWith> {
  @override
  String generateForAnnotatedElement(
    Element element,
    ConstantReader annotation,
    BuildStep buildStep,
  ) {
    if (element is! ClassElement) {
      throw InvalidGenerationSourceError('"$element" is not a ClassElement.',
          element: element);
    }

    final ClassElement classElement = element;
    final String className = classElement.name;
    final ConstructorElement? constructor = classElement.unnamedConstructor;
    final List<ParameterElement> parameters = constructor?.parameters ?? [];

    List<String> params = [];
    List<String> copyParams = [];
    if (constructor != null) {
      for (var parameter in parameters) {
        final type = parameter.type;
        final name = parameter.name;
        params.add('$type Function()? $name');
        copyParams.add('$name: $name != null ? $name() : this.$name');
      }
    }
    final paramsResult = params.join(',');
    final copyParamsResult = copyParams.join(',');

    String classResult = 'return $className($copyParamsResult);';

    return '''
    extension \$${className}CopyWith on $className {
      ${"$className copyWith({$paramsResult}){$classResult}"}
    }
    ''';
  }
}
