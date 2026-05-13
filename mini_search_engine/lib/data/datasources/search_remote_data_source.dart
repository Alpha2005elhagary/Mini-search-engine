import 'dart:convert';
import 'dart:typed_data';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:path/path.dart' as p;
import 'package:syncfusion_flutter_pdf/pdf.dart';
import 'package:excel/excel.dart' as ex;

class SearchRemoteDataSource {
  final SupabaseClient _supabase = Supabase.instance.client;

  /// Perform search using Supabase Edge Functions (with direct fallback)
  Future<Map<String, dynamic>> search(String query, {String? dateFrom, String? dateTo, String? fileType}) async {
    try {
      // 1. Try calling the Edge Function first
      final response = await _supabase.functions.invoke(
        'search',
        body: {'query': query},
      );

      if (response.status == 200) {
        // Save search to history automatically
        _saveSearchToHistory(query);

        final data = response.data;
        final List<dynamic> resultsJson = data['results'] ?? [];
        final results = resultsJson.map((doc) => {
          'filename': doc['filename'],
          'type': doc['file_type'],
          'score': 1.0,
          'date': doc['created_at'],
          'snippet': _generateSnippet(doc['content'], query),
        }).toList();

        return {'results': results, 'suggestion': data['suggestion']};
      }
      return _searchDirect(query);
    } catch (e) {
      print('Edge Function Error, falling back to direct search: $e');
      return _searchDirect(query);
    }
  }

  Future<void> _saveSearchToHistory(String query) async {
    try {
      await _supabase.from('search_history').insert({'query': query});
    } catch (e) {
      print('History saving failed: $e');
    }
  }

  /// Direct fallback search using Supabase RPC
  Future<Map<String, dynamic>> _searchDirect(String query) async {
    try {
      // Save history even in fallback mode
      _saveSearchToHistory(query);

      final List<dynamic> response = await _supabase.rpc(
        'search_documents',
        params: {'query_text': query},
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
      final response = await _supabase.from('documents').select('file_type');
      final typeCounts = <String, int>{};
      for (var row in response) {
        final type = (row['file_type'] as String).toUpperCase();
        typeCounts[type] = (typeCounts[type] ?? 0) + 1;
      }

      return {
        'total_docs': response.length,
        'type_breakdown': typeCounts,
        'unique_terms': 0,
        'top_terms': [],
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
      final content = await _extractText(name, uint8Bytes);

      // 4. Upsert into Supabase Database
      await _supabase.from('documents').upsert({
        'filename': name,
        'file_path': storagePath,
        'content': content,
        'file_type': extension.replaceFirst('.', '').toUpperCase(),
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
