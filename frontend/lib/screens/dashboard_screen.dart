import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../widgets/chat_panel.dart';
import '../widgets/url_input_card.dart';
import '../widgets/metrics_dashboard.dart';
import '../widgets/reasoning_report.dart';
import '../widgets/skeleton_loader.dart';

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

  final String _backendUrl = 'https://swapnilsalunke-compare-ai-backend.hf.space/api/compare';

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
    // We are in the "Idle" state if we have no data AND we aren't currently loading it.
    final bool isIdleState = _metrics == null && !_isLoading;

    return Scaffold(
      // appBar: AppBar(
      //   title: const Text(
      //     'CompareAI',
      //     style: TextStyle(fontWeight: FontWeight.w700, fontSize: 18, color: Colors.white),
      //   ),
      //   backgroundColor: const Color(0xFF09090B),
      //   elevation: 0,
      //   centerTitle: false,
      // ),
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 600),
        switchInCurve: Curves.easeOutCirc,
        switchOutCurve: Curves.easeInCirc,
        child: isIdleState 
            ? _buildHeroLandingState() 
            : _buildActiveWorkspaceState(context),
      ),
    );
  }

  // --- STATE 1: THE CENTERED HERO LANDING ---
  Widget _buildHeroLandingState() {
    return Center(
      key: const ValueKey('HeroState'), // Key required for AnimatedSwitcher
      child: Container(
        constraints: const BoxConstraints(maxWidth: 800),
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Premium Glowing Icon
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.03),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white.withOpacity(0.05)),
              ),
              child: const Icon(Icons.analytics_rounded, size: 64, color: Colors.white),
            ),
            const SizedBox(height: 24),
            const Text(
              'CompareAI: Cross-Examine Content',
              style: TextStyle(color: Colors.white, fontSize: 42, fontWeight: FontWeight.bold, letterSpacing: -1.0),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            const Text(
              'Provide two video URLs to extract metrics, vector database their transcripts, and generate a competitive RAG analysis report instantly.',
              style: TextStyle(color: Color(0xFFA1A1AA), fontSize: 16, height: 1.5),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            
            // The Input Bar (Centered)
            UrlInputCard(
              controllerA: _urlAController,
              controllerB: _urlBController,
              isLoading: _isLoading,
              onPressed: _analyzeVideos,
            ),
            
            if (_errorMessage != null) ...[
              const SizedBox(height: 24),
              Text(_errorMessage!, style: const TextStyle(color: Colors.redAccent)),
            ],
          ],
        ),
      ),
    );
  }

  // --- STATE 2: THE ACTIVE WORKSPACE ---
  Widget _buildActiveWorkspaceState(BuildContext context) {
    return Padding(
      key: const ValueKey('WorkspaceState'), // Key required for AnimatedSwitcher
      padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // The Input Bar (Docked at top)
          UrlInputCard(
            controllerA: _urlAController,
            controllerB: _urlBController,
            isLoading: _isLoading,
            onPressed: _analyzeVideos,
          ),
          
          if (_errorMessage != null) ...[
            const SizedBox(height: 16),
            Text(_errorMessage!, style: const TextStyle(color: Colors.redAccent)),
          ],

          const SizedBox(height: 24),
          
          Expanded(
            child: _isLoading 
                ? const SkeletonLoader() 
                : Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 250),
                        curve: Curves.easeInOut,
                        width: _isChatExpanded ? 0 : MediaQuery.of(context).size.width * 0.45,
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          physics: const NeverScrollableScrollPhysics(),
                          child: SizedBox(
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
    );
  }
}