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

      // 1. Call the Supabase Edge Function for advanced search
      final response = await _supabase.functions.invoke(
        'search',
        body: {
          'query': query,
          'fileType': fileType,
          'fromDate': dateFrom,
          'toDate': dateTo,
        },
      );

      if (response.status != 200) {
        print('Edge Function error: ${response.data}');
        return _searchDirect(query); // Fallback to RPC
      }

      return {
        'results': response.data['results'],
        'suggestion': response.data['suggestion'],
      };
    } catch (e) {
      print('Search error: $e');
      return _searchDirect(query); // Fallback to RPC
    }
  }

  /// Build a "Did you mean?" suggestion purely from the user's OWN document words
  String? _localSuggest(String query, List<dynamic> userDocs) {
    // 1. Clean the query from special operators for better matching
    final cleanQuery = query.toLowerCase()
        .replaceAll(RegExp(r'~\d*'), '')
        .replaceAll(RegExp(r'[*?]'), '')
        .replaceAll(RegExp(r'\b(AND|OR|NOT)\b', caseSensitive: false), '')
        .trim();
        
    if (cleanQuery.isEmpty) return null;

    // 2. Collect all words from this user's documents
    final Set<String> vocabulary = {};
    for (final doc in userDocs) {
      final content = (doc['content'] as String? ?? '').toLowerCase();
      final words = content.split(RegExp(r'\W+')).where((w) => w.length > 3);
      vocabulary.addAll(words);
      
      final filename = (doc['filename'] as String? ?? '').toLowerCase();
      vocabulary.addAll(filename.split(RegExp(r'[\W_]+')).where((w) => w.length > 2));
    }

    if (vocabulary.isEmpty) return null;

    // 3. Find the closest word using Levenshtein distance
    String? best;
    double bestSimilarity = -1.0;
    
    for (final word in vocabulary) {
      final dist = _levenshtein(cleanQuery, word);
      final maxLength = cleanQuery.length > word.length ? cleanQuery.length : word.length;
      final similarity = 1.0 - (dist / maxLength);
      
      // Much stricter matching for suggestions
      if (similarity > bestSimilarity && similarity >= 0.6) {
        bestSimilarity = similarity;
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
      final userId = _supabase.auth.currentUser?.id;
      if (userId == null) return {'results': [], 'suggestion': null};

      // 1. Save history
      _saveSearchToHistory(query);

      // 2. Direct search via RPC
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
        'score': doc['rank'] ?? 1.0,
        'date': doc['modified_at'] ?? doc['created_at'],
        'snippet': doc['snippet'] ?? _generateSnippet(doc['content'] ?? '', query),
      }).toList();

      // 3. Fallback suggestion logic if no results
      String? suggestion;
      if (results.isEmpty) {
        final List<dynamic> allDocs = await _supabase
            .from('documents')
            .select('filename, content')
            .eq('user_id', userId);
        suggestion = _localSuggest(query, allDocs);
      }

      return {'results': results, 'suggestion': suggestion};
    } catch (e) {
      print('Database fallback search failed: $e');
      return {'results': [], 'suggestion': null};
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
