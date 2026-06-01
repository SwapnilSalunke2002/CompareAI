import 'package:flutter/material.dart';

class SkeletonLoader extends StatefulWidget {
  const SkeletonLoader({super.key});

  @override
  State<SkeletonLoader> createState() => _SkeletonLoaderState();
}

class _SkeletonLoaderState extends State<SkeletonLoader> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _gradientPosition;

  @override
  void handleStart() {
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();

    _gradientPosition = Tween<double>(begin: -1.0, end: 2.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void initState() {
    super.initState();
    handleStart();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Left Content Pipeline Loader
            Expanded(
              flex: 5,
              child: ListView(
                physics: const NeverScrollableScrollPhysics(),
                padding: const EdgeInsets.only(right: 24),
                children: [
                  _buildShimmerCard(height: 180, child: _buildMetricsSkeleton()),
                  const SizedBox(height: 24),
                  _buildShimmerCard(height: 350, child: _buildReportSkeleton()),
                ],
              ),
            ),
            // Right Chat Panel Placeholder
            Expanded(
              flex: 5,
              child: _buildShimmerCard(height: double.infinity, child: _buildChatSkeleton()),
            ),
          ],
        );
      },
    );
  }

  Widget _buildShimmerCard({required double height, required Widget child}) {
    return Container(
      height: height,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF18181B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF27272A)),
      ),
      child: ShaderMask(
        blendMode: BlendMode.srcIn,
        shaderCallback: (bounds) {
          return LinearGradient(
            begin: Alignment(_gradientPosition.value, -0.3),
            end: Alignment(_gradientPosition.value + 1.0, 0.3),
            colors: const [
              Color(0xFF27272A),
              Color(0xFF3F3F46),
              Color(0xFF27272A),
            ],
            stops: const [0.0, 0.5, 1.0],
          ).createShader(bounds);
        },
        child: child,
      ),
    );
  }

  Widget _buildMetricsSkeleton() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // FIX: Color moved INSIDE the BoxDecoration
        Container(width: 140, height: 20, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(4))),
        const SizedBox(height: 24),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: List.generate(3, (index) => Container(width: 100, height: 60, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8)))),
        )
      ],
    );
  }

  Widget _buildReportSkeleton() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // FIX: Color moved INSIDE the BoxDecoration
        Container(width: 180, height: 22, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(4))),
        const SizedBox(height: 32),
        ...List.generate(5, (index) => Padding(
          padding: const EdgeInsets.only(bottom: 14.0),
          child: Container(width: double.infinity - (index * 40), height: 14, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(4))),
        )),
      ],
    );
  }

  Widget _buildChatSkeleton() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // FIX: Color moved INSIDE the BoxDecoration
        Container(width: 110, height: 18, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(4))),
        const Spacer(),
        Align(
          alignment: Alignment.centerRight,
          child: Container(width: 200, height: 45, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12))),
        ),
        const SizedBox(height: 16),
        Container(width: 260, height: 60, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12))),
        const SizedBox(height: 32),
        Container(width: double.infinity, height: 48, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24))),
      ],
    );
  }
}