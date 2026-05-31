import 'package:flutter/material.dart';
import 'screens/dashboard_screen.dart';

void main() {
  runApp(const CompareAIApp());
}

class CompareAIApp extends StatelessWidget {
  const CompareAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CompareAI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF09090B), // Deep Zinc
        cardColor: const Color(0xFF18181B), // Elevated Zinc
        colorScheme: const ColorScheme.dark(
          primary: Colors.white,
          secondary: Color(0xFF3B82F6), // Subtle Blue Accent
          surface: Color(0xFF18181B),
        ),
        textTheme: Typography.material2021().white,
      ),
      home: const DashboardScreen(),
    );
  }
}