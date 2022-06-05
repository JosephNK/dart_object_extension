import 'package:flutter_test/flutter_test.dart';

import 'objects/person.dart';

void main() {
  test('Test01', () {
    const person = Person(id: 0, name: 'Jin');
    final personCopy = person.copyWith(
      name: () => 'Sugar',
    );
    expect(person.name, 'Jin');
    expect(personCopy.name, 'Sugar');
  });
}
