import 'package:flutter/material.dart';

class MetricsDashboard extends StatelessWidget {
  final Map<String, dynamic> metrics;

  const MetricsDashboard({super.key, required this.metrics});

  @override
  Widget build(BuildContext context) {
    final videoA = metrics['video_a'] ?? {};
    final videoB = metrics['video_b'] ?? {};

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF18181B), 
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF27272A)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Quantitative Baseline',
            style: TextStyle(fontWeight: FontWeight.w600, fontSize: 18, color: Colors.white),
          ),
          const SizedBox(height: 24),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: _buildVideoColumn(videoA, 'Video A')),
              Container(width: 1, height: 300, color: const Color(0xFF27272A)),
              Expanded(child: _buildVideoColumn(videoB, 'Video B')),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildVideoColumn(Map<String, dynamic> data, String label) {
    // 1. Determine Platform Styling Dynamically
    final String platform = data['platform']?.toString().toLowerCase() ?? 'unknown';
    Color platformColor = const Color(0xFFA1A1AA); // Default Zinc
    IconData platformIcon = Icons.link;
    String platformName = 'WEB';

    if (platform == 'youtube') {
      platformColor = const Color(0xFFFF0000); // YouTube Red
      platformIcon = Icons.play_circle_fill;
      platformName = 'YOUTUBE';
    } else if (platform == 'instagram') {
      platformColor = const Color(0xFFE1306C); // Instagram Pink
      platformIcon = Icons.camera_alt;
      platformName = 'INSTAGRAM';
    }

    // 2. Safely extract hashtags
    final List<dynamic> rawTags = data['hashtags'] ?? [];
    final List<String> tags = rawTags.map((e) => e.toString()).take(4).toList(); // Show max 4 tags to prevent UI overflow

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Platform Badge Row
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  label,
                  style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(width: 12),
              Icon(platformIcon, color: platformColor, size: 14),
              const SizedBox(width: 4),
              Text(
                platformName,
                style: TextStyle(color: platformColor, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1.0),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          Text(
            data['creator'] ?? 'Unknown',
            style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            'Followers: ${_formatNumber(data['follower_count'] ?? 0)}',
            style: const TextStyle(color: Color(0xFF71717A), fontSize: 13),
          ),
          const SizedBox(height: 24),
          
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStatItem('Views', _formatNumber(data['views'] ?? 0)),
              _buildStatItem('Eng. Rate', '${data['engagement_rate'] ?? 0}%', highlight: true),
              _buildStatItem('Duration', '${data['duration'] ?? 0}s'),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStatItem('Likes', _formatNumber(data['likes'] ?? 0)),
              _buildStatItem('Comments', _formatNumber(data['comments'] ?? 0)),
              const SizedBox(width: 40), 
            ],
          ),
          
          const SizedBox(height: 24),
          
          // Hashtag Chips Display
          if (tags.isNotEmpty) ...[
            Wrap(
              spacing: 8.0,
              runSpacing: 8.0,
              children: tags.map((tag) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF09090B),
                  border: Border.all(color: const Color(0xFF27272A)),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '#$tag',
                  style: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 11),
                ),
              )).toList(),
            ),
          ] else ...[
             const Text(
              'No hashtags detected.',
              style: TextStyle(color: Color(0xFF3F3F46), fontSize: 11, fontStyle: FontStyle.italic),
            ),
          ]
        ],
      ),
    );
  }

  Widget _buildStatItem(String title, String value, {bool highlight = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 12)),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: highlight ? const Color(0xFF3B82F6) : Colors.white, 
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  String _formatNumber(dynamic num) {
    if (num == null) return '0';
    int value = num is int ? num : double.tryParse(num.toString())?.toInt() ?? 0;
    if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(1)}M';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}K';
    }
    return value.toString();
  }
}