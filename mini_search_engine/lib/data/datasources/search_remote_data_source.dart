import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../core/constants/api_constants.dart';

class SearchRemoteDataSource {
  Future<Map<String, dynamic>> search(String query, {String? dateFrom, String? dateTo, String? fileType}) async {
    final response = await http.post(
      Uri.parse('${ApiConstants.baseUrl}/search'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'query': query,
        'date_from': dateFrom ?? '',
        'date_to': dateTo ?? '',
        'file_type': fileType ?? ''
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load search results');
    }
  }

  Future<Map<String, dynamic>> getStats() async {
    final response = await http.get(Uri.parse('${ApiConstants.baseUrl}/stats'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load stats');
    }
  }

  Future<Map<String, dynamic>> buildIndex(List<String> formats, String folder) async {
    final response = await http.post(
      Uri.parse('${ApiConstants.baseUrl}/build'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'formats': formats,
        'folder': folder
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to build index');
    }
  }

  /// Step 1: Upload to Supabase Storage
  /// Step 2: Notify PythonAnywhere to download + save the file from the public URL
  Future<Map<String, dynamic>> uploadFile(String name, List<int> bytes) async {
    final supabase = Supabase.instance.client;
    final storagePath = 'documents/$name';

    // 1. Upload to Supabase Storage bucket 'search-files'
    await supabase.storage.from('search-files').uploadBinary(
      storagePath,
      bytes,
      fileOptions: const FileOptions(upsert: true),
    );

    // 2. Get the public URL of the uploaded file
    final publicUrl = supabase.storage.from('search-files').getPublicUrl(storagePath);

    // 3. Tell PythonAnywhere to download the file from Supabase and save it
    final response = await http.post(
      Uri.parse('${ApiConstants.baseUrl}/index-url'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'url': publicUrl,
        'filename': name,
      }),
    );

    final responseBody = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return responseBody;
    } else {
      throw Exception('File uploaded to Supabase but server could not fetch it: ${responseBody['message'] ?? response.statusCode}');
    }
  }
}
