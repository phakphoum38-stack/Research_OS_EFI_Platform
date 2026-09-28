import 'package:flutter/material.dart';
void main()=>runApp(const X1504VAApp());
class X1504VAApp extends StatelessWidget{const X1504VAApp({super.key});@override Widget build(BuildContext c)=>MaterialApp(title:'X1504VA Control Center',theme:ThemeData(useMaterial3:true,colorSchemeSeed:Colors.indigo),home:const ControlCenterPage());}
class ControlCenterPage extends StatelessWidget{
 const ControlCenterPage({super.key});
 static const components=<Map<String,String>>[
 {'name':'CPU · Core i3-1315U','state':'PROVEN'},{'name':'GPU · Intel UHD 8086:A7A9','state':'RESEARCH'},
 {'name':'Storage · VMD 09AB/A77F','state':'RESEARCH'},{'name':'Audio · Realtek ALC256','state':'PROVEN / LAYOUT RESEARCH'},
 {'name':'Wi-Fi · MediaTek MT7902','state':'RESEARCH'},{'name':'Touchpad · ASUF1300','state':'RESEARCH'}];
 @override Widget build(BuildContext c){final t=Theme.of(c);return Scaffold(appBar:AppBar(title:const Text('X1504VA Research Control Center')),body:Row(children:[
 NavigationRail(selectedIndex:0,onDestinationSelected:(_){},labelType:NavigationRailLabelType.all,destinations:const[
 NavigationRailDestination(icon:Icon(Icons.dashboard),label:Text('Overview')),NavigationRailDestination(icon:Icon(Icons.account_tree),label:Text('ACPI')),
 NavigationRailDestination(icon:Icon(Icons.fact_check),label:Text('Evidence')),NavigationRailDestination(icon:Icon(Icons.auto_awesome),label:Text('Research')),NavigationRailDestination(icon:Icon(Icons.build),label:Text('EFI'))]),
 const VerticalDivider(width:1),Expanded(child:ListView(padding:const EdgeInsets.all(24),children:[
 Text('ASUS Vivobook X1504VA',style:t.textTheme.headlineMedium),const SizedBox(height:8),
 const Text('Research OS bridge connected. Preparation is automated; hardware authority remains human-controlled.'),const SizedBox(height:20),
 const Card(child:ListTile(leading:Icon(Icons.hub),title:Text('Research OS Bridge'),subtitle:Text('Evidence manifest · wave orchestration · authority boundary · provenance tracked'))),
 const Card(child:ListTile(leading:Icon(Icons.route),title:Text('Research Lifecycle'),subtitle:Text('Collect → Reason → Candidate → Validate → Preflight → Human Experiment → Evidence → Learn'))),
 const Card(child:ListTile(leading:Icon(Icons.lock_outline),title:Text('Authority Boundary'),subtitle:Text('READY_FOR_HUMAN_BOOT is repository-side only. No BIOS / ESP / Secure Boot / VMD / disk mutation.'))),
 ...components.map((x)=>Card(child:ListTile(leading:Icon(x['state']!.contains('RESEARCH')?Icons.science:Icons.verified_outlined),title:Text(x['name']!),subtitle:Text(x['state']!),trailing:const Icon(Icons.chevron_right)))),
 const Card(child:ListTile(leading:Icon(Icons.account_tree),title:Text('Known ACPI topology'),subtitle:Text('PC00 → GFX0 · VMD0 → NVD1 · I2C1 → ETPD'))]))]));}}
