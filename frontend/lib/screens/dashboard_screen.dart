import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../widgets/chat_panel.dart';
import '../widgets/url_input_card.dart';
import '../widgets/metrics_dashboard.dart';
import '../widgets/reasoning_report.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final TextEditingController _urlAController = TextEditingController();
  final TextEditingController _urlBController = TextEditingController();

  bool _isLoading = false;
  String? _reportMarkdown;
  Map<String, dynamic>? _metrics;
  String? _errorMessage;
  bool _isChatExpanded = false;

  final String _backendUrl = 'http://127.0.0.1:8000/api/compare';

  Future<void> _analyzeVideos() async {
    if (_urlAController.text.isEmpty || _urlBController.text.isEmpty) {
      setState(() => _errorMessage = 'Please provide both Video URLs.');
      return;
    }

    setState(() {
      _isLoading = true;
      _reportMarkdown = null;
      _metrics = null;
      _errorMessage = null;
      _isChatExpanded = false;
    });

    try {
      final response = await http.post(
        Uri.parse(_backendUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'video_url_a': _urlAController.text.trim(),
          'video_url_b': _urlBController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _reportMarkdown = data['report'];
          _metrics = data['metrics'];
          _isLoading = false;
        });
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Connection Error: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool hasData = _metrics != null;

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'CompareAI',
          style: TextStyle(fontWeight: FontWeight.w700, fontSize: 18, color: Colors.white),
        ),
        backgroundColor: const Color(0xFF09090B),
        elevation: 0,
        centerTitle: false,
        bottom: _isLoading 
            ? const PreferredSize(
                preferredSize: Size.fromHeight(2),
                child: LinearProgressIndicator(
                  backgroundColor: Colors.transparent, 
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : null,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            UrlInputCard(
              controllerA: _urlAController,
              controllerB: _urlBController,
              isLoading: _isLoading,
              onPressed: _analyzeVideos,
            ),
            
            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withOpacity(0.3)),
                ),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(color: Colors.redAccent),
                  textAlign: TextAlign.center,
                ),
              ),
            ],

            const SizedBox(height: 24),
            
            Expanded(
              child: !hasData
                  ? const Center(
                      child: Text(
                        'Awaiting Video Context...',
                        style: TextStyle(color: Color(0xFFA1A1AA), fontSize: 16),
                      ),
                    )
                  : Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // FIX: Left panel uses AnimatedContainer. The tree structure is NEVER broken.
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 250),
                          curve: Curves.easeInOut,
                          width: _isChatExpanded ? 0 : MediaQuery.of(context).size.width * 0.45,
                          child: SingleChildScrollView(
                            scrollDirection: Axis.horizontal,
                            physics: const NeverScrollableScrollPhysics(),
                            child: SizedBox(
                              // Lock the width to prevent layout wrapping artifacts while collapsing
                              width: MediaQuery.of(context).size.width * 0.45,
                              child: Padding(
                                padding: const EdgeInsets.only(right: 24),
                                child: ListView(
                                  physics: const BouncingScrollPhysics(),
                                  children: [
                                    MetricsDashboard(metrics: _metrics!),
                                    const SizedBox(height: 24),
                                    if (_reportMarkdown != null)
                                      ReasoningReport(markdownData: _reportMarkdown!),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                        
                        // Right Panel: Chatbot occupies remaining layout space safely
                        Expanded(
                          child: ChatPanel(
                            metrics: _metrics!,
                            isExpanded: _isChatExpanded,
                            onExpandToggle: () {
                              setState(() {
                                _isChatExpanded = !_isChatExpanded;
                              });
                            },
                          ),
                        ),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }
}