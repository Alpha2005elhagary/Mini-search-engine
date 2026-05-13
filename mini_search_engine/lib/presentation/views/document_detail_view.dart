import 'package:flutter/material.dart';
import 'package:animate_do/animate_do.dart';
import '../widgets/glass_card.dart';

class DocumentDetailView extends StatelessWidget {
  final String filename;
  final String content;
  final String query;

  const DocumentDetailView({
    super.key,
    required this.filename,
    required this.content,
    required this.query,
  });

  bool _isArabic(String text) {
    return RegExp(r'[\u0600-\u06FF]').hasMatch(text);
  }

  List<TextSpan> _buildHighlightedContent() {
    if (query.isEmpty) return [TextSpan(text: content)];

    final List<TextSpan> spans = [];
    final String lowerContent = content.toLowerCase();
    final String lowerQuery = query.toLowerCase();
    
    int start = 0;
    int index = lowerContent.indexOf(lowerQuery);

    while (index != -1) {
      if (index > start) {
        spans.add(TextSpan(text: content.substring(start, index)));
      }
      spans.add(TextSpan(
        text: content.substring(index, index + query.length),
        style: const TextStyle(
          color: Colors.cyanAccent, 
          fontWeight: FontWeight.bold, 
          backgroundColor: Colors.white12,
          fontSize: 18,
        ),
      ));
      start = index + query.length;
      index = lowerContent.indexOf(lowerQuery, start);
    }

    if (start < content.length) {
      spans.add(TextSpan(text: content.substring(start)));
    }

    return spans;
  }

  @override
  Widget build(BuildContext context) {
    final bool isRtl = _isArabic(content);

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
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                    Expanded(
                      child: FadeInDown(
                        child: Text(
                          filename,
                          style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              
              // Content Area
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20.0),
                  child: FadeInUp(
                    child: GlassCard(
                      padding: const EdgeInsets.all(20),
                      child: SingleChildScrollView(
                        physics: const BouncingScrollPhysics(),
                        child: Directionality(
                          textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
                          child: RichText(
                            textAlign: TextAlign.start,
                            text: TextSpan(
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.9),
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
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
