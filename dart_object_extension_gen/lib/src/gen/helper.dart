import 'package:analyzer/dart/element/element.dart';

String typeParametersString(ClassElement classElement, bool nameOnly) {
  final names = classElement.typeParameters
      .map((e) => nameOnly ? e.displayName : e.displayString())
      .join(',');
  return names.isNotEmpty ? '<$names>' : '';
}
