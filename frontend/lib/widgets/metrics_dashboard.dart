import 'package:flutter/material.dart';

class MetricsDashboard extends StatelessWidget {
  final Map<String, dynamic> metrics;

  const MetricsDashboard({super.key, required this.metrics});

  @override
  Widget build(BuildContext context) {
    final videoA = metrics['video_a'] ?? {};
    final videoB = metrics['video_b'] ?? {};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(left: 4.0, bottom: 12),
          child: Text(
            'CROSS-EXAMINATION METRICS',
            style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.5, color: Colors.grey, fontSize: 13),
          ),
        ),
        Row(
          children: [
            Expanded(child: _buildMetricPanel('VIDEO A', videoA, const Color(0xFF00FF66))),
            const SizedBox(width: 16),
            Expanded(child: _buildMetricPanel('VIDEO B', videoB, const Color(0xFF00E5FF))),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricPanel(String title, Map<String, dynamic> data, Color accentColor) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF11111A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1E1E2C)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: TextStyle(fontWeight: FontWeight.bold, color: accentColor, letterSpacing: 1.0)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: accentColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  (data['platform'] ?? 'UNKNOWN').toString().toUpperCase(),
                  style: TextStyle(color: accentColor, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const Divider(color: Color(0xFF222232), height: 24),
          _buildMetricRow('Creator', data['creator']?.toString() ?? 'N/A'),
          const SizedBox(height: 12),
          _buildMetricRow('Views', data['views']?.toString() ?? '0'),
          const SizedBox(height: 12),
          _buildMetricRow('Engagement', '${data['engagement_rate'] ?? '0'}%'),
        ],
      ),
    );
  }

  Widget _buildMetricRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 14)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
      ],
    );
  }
}