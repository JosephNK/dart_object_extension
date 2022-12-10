import 'package:test/test.dart' show test, expect;

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
