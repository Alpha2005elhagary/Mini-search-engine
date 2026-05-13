import 'dart:convert';
import 'dart:typed_data';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:path/path.dart' as p;
import 'package:syncfusion_flutter_pdf/pdf.dart';
import 'package:excel/excel.dart' as ex;
import '../../core/constants/api_constants.dart';


class SearchRemoteDataSource {
  final SupabaseClient _supabase = Supabase.instance.client;

  /// Perform search using Supabase direct DB (fully local suggestion)
  Future<Map<String, dynamic>> search(String query, {String? dateFrom, String? dateTo, String? fileType}) async {
    try {
      final userId = _supabase.auth.currentUser?.id;
      if (userId == null) throw Exception('User not logged in');

      _saveSearchToHistory(query);

      // 1. Fetch user's OWN documents only (strict user_id filter)
      var dbQuery = _supabase
          .from('documents')
          .select('filename, file_type, content, created_at')
          .eq('user_id', userId);

      if (fileType != null) dbQuery = dbQuery.eq('file_type', fileType);

      final List<dynamic> allDocs = await dbQuery;

      // 2. Local search: filter documents that match the query
      final lowerQuery = query.toLowerCase()
          .replaceAll(RegExp(r'~\d*'), '') // remove fuzzy notation
          .replaceAll(RegExp(r'[*?]'), '') // remove wildcards
          .replaceAll(RegExp(r'\b(AND|OR|NOT)\b'), '') // remove boolean ops
          .trim();

      final results = allDocs.where((doc) {
        final content = (doc['content'] as String? ?? '').toLowerCase();
        final filename = (doc['filename'] as String? ?? '').toLowerCase();
        return content.contains(lowerQuery) || filename.contains(lowerQuery);
      }).map((doc) => {
        'filename': doc['filename'],
        'fileType': doc['file_type'],
        'date': doc['created_at'],
        'snippet': _generateSnippet(doc['content'] ?? '', query),
      }).toList();

      // 3. "Did you mean?" - built LOCALLY from this user's OWN words only
      // No server call. No leakage possible.
      String? suggestion;
      if (results.isEmpty && lowerQuery.isNotEmpty) {
        suggestion = _localSuggest(lowerQuery, allDocs);
      }

      return {'results': results, 'suggestion': suggestion};
    } catch (e) {
      print('Search error: $e');
      return {'results': [], 'suggestion': null};
    }
  }

  /// Build a "Did you mean?" suggestion purely from the user's OWN document words
  String? _localSuggest(String query, List<dynamic> userDocs) {
    // Collect all words from this user's documents
    final Set<String> vocabulary = {};
    for (final doc in userDocs) {
      final words = (doc['content'] as String? ?? '')
          .toLowerCase()
          .split(RegExp(r'\W+'))
          .where((w) => w.length > 3);
      vocabulary.addAll(words);
      // Also add filename words
      vocabulary.addAll(
        (doc['filename'] as String? ?? '')
            .toLowerCase()
            .split(RegExp(r'[\W_]+'))
            .where((w) => w.length > 2),
      );
    }

    if (vocabulary.isEmpty) return null;

    // Find the closest word using Levenshtein distance
    String? best;
    int bestDist = 999;
    for (final word in vocabulary) {
      final dist = _levenshtein(query, word);
      // Only suggest if similar enough (distance <= 2 or similarity > 60%)
      if (dist < bestDist && dist <= 2) {
        bestDist = dist;
        best = word;
      }
    }
    return best;
  }

  /// Levenshtein distance for local fuzzy matching
  int _levenshtein(String s, String t) {
    if (s == t) return 0;
    if (s.isEmpty) return t.length;
    if (t.isEmpty) return s.length;
    // Limit to short words for performance
    if (s.length > 20 || t.length > 20) return 999;

    final d = List.generate(s.length + 1, (i) => List.generate(t.length + 1, (j) => j == 0 ? i : (i == 0 ? j : 0)));
    for (int i = 1; i <= s.length; i++) {
      for (int j = 1; j <= t.length; j++) {
        final cost = s[i - 1] == t[j - 1] ? 0 : 1;
        d[i][j] = [d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost].reduce((a, b) => a < b ? a : b);
      }
    }
    return d[s.length][t.length];
  }

  Future<void> _saveSearchToHistory(String query) async {
    try {
      final userId = _supabase.auth.currentUser?.id;
      await _supabase.from('search_history').insert({
        'query': query,
        'user_id': userId,
      });
    } catch (e) {
      print('History saving failed: $e');
    }
  }

  /// Direct fallback search using Supabase RPC
  Future<Map<String, dynamic>> _searchDirect(String query) async {
    try {
      // Save history even in fallback mode
      _saveSearchToHistory(query);

      final userId = _supabase.auth.currentUser?.id;
      final List<dynamic> response = await _supabase.rpc(
        'search_documents',
        params: {
          'query_text': query,
          'p_user_id': userId,
        },
      );

      final results = response.map((doc) => {
        'filename': doc['filename'],
        'type': doc['file_type'],
        'score': 1.0,
        'date': doc['created_at'],
        'snippet': _generateSnippet(doc['content'], query),
      }).toList();

      return {'results': results, 'suggestion': null};
    } catch (e) {
      throw Exception('Database search failed: $e');
    }
  }

  Future<Map<String, dynamic>> getStats() async {
    try {
      final userId = _supabase.auth.currentUser?.id;
      if (userId == null) throw Exception('User not logged in');
      
      final response = await _supabase.from('documents').select('file_type, content').eq('user_id', userId);
      
      final typeCounts = <String, int>{};
      final wordCounts = <String, int>{};
      
      for (var row in response) {
        final type = (row['file_type'] as String).toUpperCase();
        typeCounts[type] = (typeCounts[type] ?? 0) + 1;
        
        final content = row['content'] as String? ?? '';
        // Basic word frequency analysis
        final words = content.toLowerCase().split(RegExp(r'\W+')).where((w) => w.length > 3);
        for (var word in words) {
          wordCounts[word] = (wordCounts[word] ?? 0) + 1;
        }
      }

      final sortedTerms = wordCounts.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      
      final topTerms = sortedTerms.take(10).map((e) => [e.key, e.value]).toList();

      return {
        'total_docs': response.length,
        'type_breakdown': typeCounts,
        'unique_terms': wordCounts.length,
        'top_terms': topTerms,
      };
    } catch (e) {
      throw Exception('Failed to load stats: $e');
    }
  }

  Future<Map<String, dynamic>> buildIndex(List<String> formats, String folder) async {
    return {'success': true, 'message': 'Supabase indexing is active!'};
  }

  /// Upload to Supabase and index locally (Serverless)
  Future<Map<String, dynamic>> uploadFile(String name, List<int> bytes) async {
    try {
      // 1. Sanitize filename for Storage
      final extension = p.extension(name);
      final baseName = p.basenameWithoutExtension(name).replaceAll(RegExp(r'[^a-zA-Z0-9]'), '_');
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final safeName = "${baseName}_$timestamp$extension";
      final storagePath = 'documents/$safeName';

      final uint8Bytes = Uint8List.fromList(bytes);

      // 2. Upload original file to Supabase Storage
      await _supabase.storage.from('search-files').uploadBinary(
        storagePath,
        uint8Bytes,
        fileOptions: const FileOptions(upsert: true),
      );

      // 3. Extract text on-device for indexing
      String content = await _extractText(name, uint8Bytes);
      
      // 3b. Sanitize content (Remove null bytes for PostgreSQL)
      content = content.replaceAll('\u0000', '');

      // 4. Upsert into Supabase Database
      await _supabase.from('documents').upsert({
        'filename': name,
        'file_path': storagePath,
        'content': content,
        'file_type': extension.replaceFirst('.', '').toUpperCase(),
        'user_id': _supabase.auth.currentUser?.id,
      }, onConflict: 'file_path');

      return {
        'success': true, 
        'message': '✅ $name uploaded and indexed successfully!'
      };
    } catch (e) {
      print('Upload Error: $e');
      throw Exception('Failed to upload and index: $e');
    }
  }

  Future<String> _extractText(String filename, Uint8List bytes) async {
    final ext = p.extension(filename).toLowerCase();
    try {
      if (ext == '.pdf') {
        final PdfDocument document = PdfDocument(inputBytes: bytes);
        final String text = PdfTextExtractor(document).extractText();
        document.dispose();
        return text;
      } else if (ext == '.xlsx' || ext == '.xls') {
        final excel = ex.Excel.decodeBytes(bytes);
        String text = '';
        for (var table in excel.tables.keys) {
          for (var row in excel.tables[table]!.rows) {
            text += row.map((c) => c?.value ?? '').join(' ') + ' ';
          }
        }
        return text;
      } else {
        return utf8.decode(bytes, allowMalformed: true);
      }
    } catch (e) {
      return utf8.decode(bytes, allowMalformed: true);
    }
  }

  String _generateSnippet(String content, String query) {
    if (content.isEmpty) return '';
    final index = content.toLowerCase().indexOf(query.toLowerCase());
    if (index == -1) return content.length > 150 ? '${content.substring(0, 150)}...' : content;
    
    final start = (index - 60).clamp(0, content.length);
    final end = (index + 90).clamp(0, content.length);
    return '...${content.substring(start, end)}...';
  }
}
