import 'package:flutter/material.dart';

class UrlInputCard extends StatelessWidget {
  final TextEditingController controllerA;
  final TextEditingController controllerB;
  final bool isLoading;
  final VoidCallback onPressed;

  const UrlInputCard({
    super.key,
    required this.controllerA,
    required this.controllerB,
    required this.isLoading,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF18181B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF27272A)),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controllerA,
              decoration: InputDecoration(
                hintText: 'Video A URL...',
                hintStyle: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 14),
                filled: true,
                fillColor: const Color(0xFF09090B),
                prefixIcon: const Icon(Icons.link, color: Color(0xFFA1A1AA), size: 20),
                contentPadding: const EdgeInsets.symmetric(vertical: 0),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: TextField(
              controller: controllerB,
              decoration: InputDecoration(
                hintText: 'Video B URL...',
                hintStyle: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 14),
                filled: true,
                fillColor: const Color(0xFF09090B),
                prefixIcon: const Icon(Icons.link, color: Color(0xFFA1A1AA), size: 20),
                contentPadding: const EdgeInsets.symmetric(vertical: 0),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
              ),
            ),
          ),
          const SizedBox(width: 16),
          ElevatedButton(
            onPressed: isLoading ? null : onPressed,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: Colors.black,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              elevation: 0,
            ),
            child: isLoading
                ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(color: Colors.black, strokeWidth: 2))
                : const Text('Analyze', style: TextStyle(fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }
}