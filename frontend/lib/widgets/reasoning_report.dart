import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class ReasoningReport extends StatelessWidget {
  final String markdownData;

  const ReasoningReport({super.key, required this.markdownData});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: const Color(0xFF18181B), // Elevated Zinc
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF27272A)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Executive Analysis',
            style: TextStyle(fontWeight: FontWeight.w600, fontSize: 18, color: Colors.white),
          ),
          const SizedBox(height: 24),
          MarkdownBody(
            data: markdownData,
            styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(
              p: const TextStyle(fontSize: 15, height: 1.7, color: Color(0xFFD4D4D8)), // Zinc 300
              h1: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white, height: 2),
              h2: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.white, height: 1.8),
              h3: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Colors.white),
              listBullet: const TextStyle(color: Colors.white, fontSize: 16),
              blockquoteDecoration: const BoxDecoration(
                border: Border(left: BorderSide(color: Colors.white, width: 3)),
              ),
              blockquotePadding: const EdgeInsets.only(left: 16, top: 8, bottom: 8),
              blockquote: const TextStyle(fontSize: 15, fontStyle: FontStyle.italic, color: Color(0xFFA1A1AA)),
            ),
          ),
        ],
      ),
    );
  }
}