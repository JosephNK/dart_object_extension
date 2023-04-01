import 'package:analyzer/dart/element/element.dart';
import 'package:build/build.dart';
import 'package:dart_object_extension/dart_object_extension.dart';
import 'package:source_gen/source_gen.dart';

import 'helper.dart';

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
    final typeParametersAnnotation = typeParametersString(classElement, false);
    final typeParametersNames = typeParametersString(classElement, true);

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

    String classResult =
        'return $className$typeParametersAnnotation($copyParamsResult);';

    return '''
    extension \$${className}CopyWith$typeParametersAnnotation on $className$typeParametersNames {
      ${"$className copyWith({$paramsResult}){$classResult}"}
    }
    ''';
  }
}
