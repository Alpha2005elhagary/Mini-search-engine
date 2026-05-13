import 'package:flutter/material.dart';
import 'package:animate_do/animate_do.dart';
import '../widgets/glass_card.dart';

class DocumentDetailView extends StatefulWidget {
  final String filename;
  final String content;
  final String query;

  const DocumentDetailView({
    super.key,
    required this.filename,
    required this.content,
    required this.query,
  });

  @override
  State<DocumentDetailView> createState() => _DocumentDetailViewState();
}

class _DocumentDetailViewState extends State<DocumentDetailView> {
  bool _showHighlights = true;
  late List<int> _matchIndices;
  int _currentMatchIndex = -1;
  final ScrollController _scrollController = ScrollController();
  final GlobalKey _textKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    _findMatches();
  }

  void _findMatches() {
    _matchIndices = [];
    if (widget.query.isEmpty) return;
    
    final String lowerContent = widget.content.toLowerCase();
    final String lowerQuery = widget.query.toLowerCase();
    
    int index = lowerContent.indexOf(lowerQuery);
    while (index != -1) {
      _matchIndices.add(index);
      index = lowerContent.indexOf(lowerQuery, index + widget.query.length);
    }
    
    if (_matchIndices.isNotEmpty) {
      _currentMatchIndex = 0;
    }
  }

  void _nextMatch() {
    if (_matchIndices.isEmpty) return;
    setState(() {
      _currentMatchIndex = (_currentMatchIndex + 1) % _matchIndices.length;
    });
    _scrollToMatch();
  }

  void _prevMatch() {
    if (_matchIndices.isEmpty) return;
    setState(() {
      _currentMatchIndex = (_currentMatchIndex - 1 + _matchIndices.length) % _matchIndices.length;
    });
    _scrollToMatch();
  }

  void _scrollToMatch() {
    if (_currentMatchIndex == -1) return;
    // Simple estimation: scroll based on index percentage
    final double scrollTarget = (_matchIndices[_currentMatchIndex] / widget.content.length) * _scrollController.position.maxScrollExtent;
    _scrollController.animateTo(
      scrollTarget,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  bool _isArabic(String text) {
    return RegExp(r'[\u0600-\u06FF]').hasMatch(text);
  }

  List<TextSpan> _buildHighlightedContent() {
    if (widget.query.isEmpty || !_showHighlights) return [TextSpan(text: widget.content)];

    final List<TextSpan> spans = [];
    final String lowerContent = widget.content.toLowerCase();
    final String lowerQuery = widget.query.toLowerCase();
    
    int start = 0;
    int index = lowerContent.indexOf(lowerQuery);
    int matchCounter = 0;

    while (index != -1) {
      if (index > start) {
        spans.add(TextSpan(text: widget.content.substring(start, index)));
      }
      
      final bool isCurrent = _currentMatchIndex != -1 && matchCounter == _currentMatchIndex;

      spans.add(TextSpan(
        text: widget.content.substring(index, index + widget.query.length),
        style: TextStyle(
          color: isCurrent ? Colors.black : Colors.cyanAccent, 
          fontWeight: FontWeight.bold, 
          backgroundColor: isCurrent ? Colors.orangeAccent : Colors.white.withValues(alpha: 0.12),
          fontSize: 18,
        ),
      ));
      
      start = index + widget.query.length;
      index = lowerContent.indexOf(lowerQuery, start);
      matchCounter++;
    }

    if (start < widget.content.length) {
      spans.add(TextSpan(text: widget.content.substring(start)));
    }

    return spans;
  }

  @override
  Widget build(BuildContext context) {
    final bool isRtl = _isArabic(widget.content);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF0F2027), Color(0xFF203A43), Color(0xFF2C5364)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                    Expanded(
                      child: FadeInDown(
                        child: Text(
                          widget.filename,
                          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: Icon(_showHighlights ? Icons.highlight : Icons.highlight_off, 
                           color: _showHighlights ? Colors.cyanAccent : Colors.white54),
                      onPressed: () => setState(() => _showHighlights = !_showHighlights),
                    ),
                  ],
                ),
              ),
              
              // Navigation Controls
              if (widget.query.isNotEmpty && _showHighlights && _matchIndices.isNotEmpty)
                FadeIn(
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 5),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(15),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
                    ),
                    child: Row(
                      children: [
                        Text(
                          '${_currentMatchIndex + 1} of ${_matchIndices.length} matches',
                          style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.bold),
                        ),
                        const Spacer(),
                        IconButton(
                          icon: const Icon(Icons.keyboard_arrow_up, color: Colors.cyanAccent),
                          onPressed: _prevMatch,
                        ),
                        IconButton(
                          icon: const Icon(Icons.keyboard_arrow_down, color: Colors.cyanAccent),
                          onPressed: _nextMatch,
                        ),
                      ],
                    ),
                  ),
                ),

              // Content Area
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: FadeInUp(
                    child: GlassCard(
                      padding: const EdgeInsets.all(20),
                      child: SingleChildScrollView(
                        controller: _scrollController,
                        physics: const BouncingScrollPhysics(),
                        child: Directionality(
                          textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
                          child: RichText(
                            key: _textKey,
                            textAlign: TextAlign.start,
                            text: TextSpan(
                              style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.9),
                                fontSize: 16,
                                height: 1.6,
                                fontFamily: 'Inter',
                              ),
                              children: _buildHighlightedContent(),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
