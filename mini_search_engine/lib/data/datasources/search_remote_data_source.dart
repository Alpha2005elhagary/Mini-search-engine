import 'dart:convert';
import 'package:http/http.dart' as http;
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

  Future<Map<String, dynamic>> uploadFile(String name, List<int> bytes) async {
    final uri = Uri.parse('${ApiConstants.baseUrl}/upload');
    var request = http.MultipartRequest('POST', uri);
    
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      bytes,
      filename: name,
    ));
    
    final response = await request.send();
    final responseString = await response.stream.bytesToString();
    
    if (response.statusCode == 200) {
      return jsonDecode(responseString);
    } else {
      throw Exception('Failed to upload file');
    }
  }
}
