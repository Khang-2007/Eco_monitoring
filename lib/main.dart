import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const EcoMonitorApp());
}

class EcoMonitorApp extends StatelessWidget {
  const EcoMonitorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EcoMonitor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: Colors.grey.shade100,
      ),
      home: const HomeScreen(),
    );
  }
}