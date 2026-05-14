import 'dart:convert';
import 'dart:typed_data';
import 'dart:io';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:path/path.dart' as path;
import 'package:syncfusion_flutter_pdf/pdf.dart';
import 'package:excel/excel.dart';

class SearchRemoteDataSource {
  final SupabaseClient _supabase = Supabase.instance.client;

  /// CORE: Unified Search through Edge Function
  Future<Map<String, dynamic>> search(String query, {
    String? dateFrom, 
    String? dateTo, 
    String? fileType, 
    int page = 1, 
    int limit = 5
  }) async {
    try {
      final response = await _supabase.functions.invoke('search', body: {
        'query': query,
        'fileType': fileType,
        'fromDate': dateFrom,
        'toDate': dateTo,
        'page': page,
        'limit': limit,
      });

      if (response.status != 200) throw Exception('Search failed: ${response.data}');

      return {
        'results': response.data['results'] ?? [],
        'totalCount': response.data['totalCount'] ?? 0,
        'suggestion': null, // Suggestion logic handled by fallback or separate RPC
      };
    } catch (e) {
      print('Search error: $e');
      return {'results': [], 'totalCount': 0};
    }
  }

  /// CORE: Unified File Indexing (Single File or Bulk)
  Future<Map<String, dynamic>> uploadFile(String filePath, List<int> bytes) async {
    try {
      final userId = _supabase.auth.currentUser?.id;
      if (userId == null) throw Exception('Unauthorized');

      final file = File(filePath);
      final filename = path.basename(filePath);
      final ext = path.extension(filePath).toLowerCase().replaceAll('.', '');
      final stat = await file.stat();

      // 1. Extract Text
      final content = await _extractText(file);

      // 2. Database Sync
      final dbResponse = await _supabase.from('documents').upsert({
        'user_id': userId,
        'filename': filename,
        'content': content.replaceAll('\u0000', ''),
        'file_type': ext.toUpperCase(),
        'modified_at': stat.modified.toUtc().toIso8601String(),
      }, onConflict: 'user_id, filename').select();

      print('Sync success: $filename');
      return {'message': 'Successfully indexed $filename'};
    } catch (e) {
      print('Indexing error: $e');
      return {'message': 'Error: $e'};
    }
  }

  /// REBUILD: Bulk Index Folder
  Future<Map<String, dynamic>> buildIndex(List<String> formats, String folderPath) async {
    final dir = Directory(folderPath);
    if (!await dir.exists()) throw Exception('Folder not found');

    int count = 0;
    await for (final entity in dir.list(recursive: true)) {
      if (entity is File) {
        final ext = path.extension(entity.path).toLowerCase().replaceAll('.', '');
        if (formats.contains(ext.toUpperCase())) {
          await uploadFile(entity.path, await entity.readAsBytes());
          count++;
        }
      }
    }
    return {'message': 'Indexed $count files from $folderPath'};
  }

  /// STATS: Get Database Overview
  Future<Map<String, dynamic>> getStats() async {
    final userId = _supabase.auth.currentUser?.id;
    if (userId == null) return {'total_docs': 0, 'type_breakdown': {}, 'unique_terms': 0, 'top_terms': []};
    
    // 1. Fetch only this user's data (Strict Isolation)
    final response = await _supabase.from('documents')
        .select('file_type, content')
        .eq('user_id', userId);
    
    final types = <String, int>{};
    final wordCounts = <String, int>{};
    
    for (var r in response) {
      // Type breakdown
      final t = r['file_type'].toString().toUpperCase();
      types[t] = (types[t] ?? 0) + 1;

      // Word frequency analysis
      final content = r['content']?.toString().toLowerCase() ?? '';
      final words = content.split(RegExp(r'\W+')).where((w) => w.length > 3); // Ignore short words/stops
      for (var word in words) {
        wordCounts[word] = (wordCounts[word] ?? 0) + 1;
      }
    }

    // Sort to find top 10
    final sortedTerms = wordCounts.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    
    final topTerms = sortedTerms.take(10).map((e) => [e.key, e.value]).toList();

    return {
      'total_docs': response.length,
      'type_breakdown': types,
      'unique_terms': wordCounts.length,
      'top_terms': topTerms,
    };
  }

  Future<String> _extractText(File file) async {
    final ext = path.extension(file.path).toLowerCase();
    try {
      // Background processing would ideally use 'compute' here
      // For now, we optimize the bytes reading and extraction flow
      if (ext == '.pdf') {
        final bytes = await file.readAsBytes();
        final doc = PdfDocument(inputBytes: bytes);
        final text = PdfTextExtractor(doc).extractText();
        doc.dispose();
        return text;
      } else if (ext == '.xlsx' || ext == '.xls') {
        final bytes = await file.readAsBytes();
        final excel = Excel.decodeBytes(bytes);
        final sb = StringBuffer();
        for (var t in excel.tables.keys) {
          for (var r in excel.tables[t]!.rows) {
            for (var c in r) {
              if (c?.value != null) sb.write('${c!.value} ');
            }
          }
        }
        return sb.toString();
      } else {
        return await file.readAsString();
      }
    } catch (e) {
      print('Extraction error for ${file.path}: $e');
      return '';
    }
  }
}
