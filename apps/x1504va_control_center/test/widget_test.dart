import 'package:flutter_test/flutter_test.dart';
import 'package:x1504va_control_center/main.dart';

void main() {
  testWidgets('renders X1504VA control center', (tester) async {
    await tester.pumpWidget(const X1504VAApp());
    expect(find.text('X1504VA Research Control Center'), findsOneWidget);
    expect(find.text('Storage · VMD 09AB/A77F'), findsOneWidget);
    expect(find.text('GPU · Intel UHD 8086:A7A9'), findsOneWidget);
  });
}
