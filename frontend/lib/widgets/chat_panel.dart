import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_markdown/flutter_markdown.dart';

class ChatPanel extends StatefulWidget {
  final Map<String, dynamic> metrics;
  final bool isExpanded;
  final VoidCallback onExpandToggle;

  const ChatPanel({
    super.key, 
    required this.metrics, 
    required this.isExpanded, 
    required this.onExpandToggle
  });

  @override
  State<ChatPanel> createState() => _ChatPanelState();
}

class _ChatPanelState extends State<ChatPanel> with AutomaticKeepAliveClientMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<Map<String, String>> _chatHistory = [];
  bool _isStreaming = false;

  @override
  bool get wantKeepAlive => true;

  Future<void> _sendMessage() async {
    final query = _messageController.text.trim();
    if (query.isEmpty) return;

    setState(() {
      _chatHistory.add({'role': 'user', 'content': query});
      _chatHistory.add({'role': 'assistant', 'content': ''});
      _isStreaming = true;
    });

    _messageController.clear();
    _scrollToBottom();

    try {
      final request = http.Request('POST', Uri.parse('https://swapnilsalunke-compare-ai-backend.hf.space/api/chat/stream'));
      request.headers['Content-Type'] = 'application/json';
      request.body = jsonEncode({
        'query': query,
        'history': _chatHistory.length > 2 ? _chatHistory.sublist(0, _chatHistory.length - 2) : [],
        'metrics': widget.metrics,
      });

      final response = await http.Client().send(request);
      response.stream.transform(utf8.decoder).listen(
        (token) {
          if (!mounted) return;
          setState(() {
            _chatHistory.last['content'] = _chatHistory.last['content']! + token;
          });
          _scrollToBottom();
        },
        onDone: () {
          if (mounted) setState(() => _isStreaming = false);
        },
      );
    } catch (e) {
      if (mounted) setState(() { _isStreaming = false; });
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF18181B), // Elevated Zinc surface
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF27272A)), // Subtle border
      ),
      child: Column(
        children: [
          // Clean Header with Expand Button
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: Color(0xFF27272A))),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Analysis Chat',
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 16),
                ),
                IconButton(
                  icon: Icon(widget.isExpanded ? Icons.fullscreen_exit : Icons.fullscreen),
                  color: const Color(0xFFA1A1AA),
                  tooltip: widget.isExpanded ? "Collapse" : "Expand to Full Screen",
                  onPressed: widget.onExpandToggle,
                )
              ],
            ),
          ),
          
          // Chat Timeline
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(24),
              itemCount: _chatHistory.length,
              itemBuilder: (context, index) {
                final isUser = _chatHistory[index]['role'] == 'user';
                return Padding(
                  padding: const EdgeInsets.only(bottom: 24.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                    children: [
                      if (!isUser) ...[
                        const Icon(Icons.blur_on, color: Colors.white, size: 24),
                        const SizedBox(width: 12),
                      ],
                      Flexible(
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                          decoration: BoxDecoration(
                            color: isUser ? Colors.white.withOpacity(0.1) : Colors.transparent,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: MarkdownBody(
                            data: _chatHistory[index]['content']!,
                            styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(
                              p: const TextStyle(color: Color(0xFFFAFAFA), fontSize: 15, height: 1.6),
                              code: const TextStyle(backgroundColor: Colors.black26, color: Colors.white),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),

          // Minimalist Input Box
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    enabled: !_isStreaming,
                    onSubmitted: (_) => _sendMessage(),
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Ask a question...',
                      hintStyle: const TextStyle(color: Color(0xFFA1A1AA)),
                      filled: true,
                      fillColor: const Color(0xFF09090B),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                CircleAvatar(
                  backgroundColor: Colors.white,
                  radius: 24,
                  child: IconButton(
                    onPressed: _isStreaming ? null : _sendMessage,
                    icon: _isStreaming 
                        ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(color: Colors.black, strokeWidth: 2))
                        : const Icon(Icons.arrow_upward, color: Colors.black, size: 20),
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