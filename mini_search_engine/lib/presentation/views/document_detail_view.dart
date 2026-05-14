import 'package:flutter/material.dart';
import 'package:animate_do/animate_do.dart';
import '../widgets/glass_card.dart';
import '../../domain/entities/search_result.dart';

class DocumentDetailView extends StatefulWidget {
  final SearchResult result;
  final String query;

  const DocumentDetailView({
    super.key,
    required this.result,
    required this.query,
  });

  @override
  State<DocumentDetailView> createState() => _DocumentDetailViewState();
}

class _DocumentDetailViewState extends State<DocumentDetailView> {
  final ScrollController _scrollController = ScrollController();

  bool _isArabic(String text) {
    return RegExp(r'[\u0600-\u06FF]').hasMatch(text);
  }

  TextSpan _buildHighlightedContent(String content) {
    final List<TextSpan> spans = [];
    // Parse both <mark> tags from DB and manual query matches if needed
    final regExp = RegExp(r'<mark>(.*?)</mark>');
    int lastIndex = 0;

    for (final match in regExp.allMatches(content)) {
      if (match.start > lastIndex) {
        spans.add(TextSpan(
          text: content.substring(lastIndex, match.start),
          style: const TextStyle(color: Colors.white, fontSize: 16, height: 1.6),
        ));
      }
      spans.add(TextSpan(
        text: match.group(1),
        style: const TextStyle(
          color: Colors.cyanAccent,
          fontWeight: FontWeight.bold,
          fontSize: 18,
          backgroundColor: Colors.white12,
        ),
      ));
      lastIndex = match.end;
    }

    if (lastIndex < content.length) {
      spans.add(TextSpan(
        text: content.substring(lastIndex),
        style: const TextStyle(color: Colors.white, fontSize: 16, height: 1.6),
      ));
    }

    // If no <mark> tags found, try simple substring matching for the query
    if (spans.isEmpty && widget.query.isNotEmpty) {
      final String lowerContent = content.toLowerCase();
      final String lowerQuery = widget.query.toLowerCase();
      int start = 0;
      int index = lowerContent.indexOf(lowerQuery);

      while (index != -1) {
        if (index > start) {
          spans.add(TextSpan(text: content.substring(start, index)));
        }
        spans.add(TextSpan(
          text: content.substring(index, index + widget.query.length),
          style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, backgroundColor: Colors.white12),
        ));
        start = index + widget.query.length;
        index = lowerContent.indexOf(lowerQuery, start);
      }
      if (start < content.length) {
        spans.add(TextSpan(text: content.substring(start)));
      }
    }

    return TextSpan(children: spans.isEmpty ? [TextSpan(text: content)] : spans);
  }

  @override
  Widget build(BuildContext context) {
    final String content = widget.result.snippet;
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
                          widget.result.filename,
                          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
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
                            textAlign: TextAlign.start,
                            text: _buildHighlightedContent(content),
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
