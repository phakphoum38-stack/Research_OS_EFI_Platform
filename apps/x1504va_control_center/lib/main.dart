import 'package:flutter/material.dart';

void main() => runApp(const X1504VAApp());

class X1504VAApp extends StatelessWidget {
  const X1504VAApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'X1504VA Control Center',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.indigo),
      home: const ControlCenterPage(),
    );
  }
}

class ControlCenterPage extends StatelessWidget {
  const ControlCenterPage({super.key});

  static const components = <Map<String, String>>[
    {'name': 'CPU · Core i3-1315U', 'state': 'OS_PROVEN'},
    {'name': 'GPU · Intel UHD 8086:A7A9', 'state': 'BLOCKED'},
    {'name': 'Storage · VMD 09AB/A77F', 'state': 'RESEARCH'},
    {'name': 'Audio · Realtek ALC256', 'state': 'PARTIAL'},
    {'name': 'Wi-Fi · MediaTek MT7902', 'state': 'UNKNOWN'},
    {'name': 'Touchpad · ASUF1300', 'state': 'FIRMWARE_PROVEN'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('X1504VA Research Control Center')),
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: 0,
            onDestinationSelected: (_) {},
            labelType: NavigationRailLabelType.all,
            destinations: const [
              NavigationRailDestination(icon: Icon(Icons.dashboard), label: Text('Overview')),
              NavigationRailDestination(icon: Icon(Icons.account_tree), label: Text('ACPI')),
              NavigationRailDestination(icon: Icon(Icons.fact_check), label: Text('Evidence')),
              NavigationRailDestination(icon: Icon(Icons.build), label: Text('EFI')),
            ],
          ),
          const VerticalDivider(width: 1),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                Text('ASUS Vivobook X1504VA', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 8),
                const Text('Evidence-first platform. Generation and boot actions remain gated.'),
                const SizedBox(height: 24),
                ...components.map((item) => Card(
                  child: ListTile(
                    leading: const Icon(Icons.memory),
                    title: Text(item['name']!),
                    subtitle: Text(item['state']!),
                    trailing: const Icon(Icons.chevron_right),
                  ),
                )),
                const Card(
                  child: ListTile(
                    leading: Icon(Icons.account_tree),
                    title: Text('Known ACPI topology'),
                    subtitle: Text('PC00 → GFX0 · VMD0 → NVD1 · I2C1 → ETPD'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
