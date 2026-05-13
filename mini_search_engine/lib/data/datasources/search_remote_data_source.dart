import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:path/path.dart' as p;
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

  /// Upload file directly to PythonAnywhere via multipart form upload.
  Future<Map<String, dynamic>> uploadFile(String name, List<int> bytes) async {
    final uri = Uri.parse('${ApiConstants.baseUrl}/upload');
    final ext = p.extension(name).toLowerCase().replaceAll('.', '');
    
    // Determine MIME type
    final mimeType = {
      'pdf': 'application/pdf',
      'txt': 'text/plain',
      'csv': 'text/csv',
      'json': 'application/json',
      'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }[ext] ?? 'application/octet-stream';

    var request = http.MultipartRequest('POST', uri);
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      Uint8List.fromList(bytes),
      filename: name,
      contentType: MediaType.parse(mimeType),
    ));

    final streamedResponse = await request.send();
    final responseString = await streamedResponse.stream.bytesToString();

    // Detect HTML error pages (server not updated yet)
    if (responseString.trimLeft().startsWith('<!')) {
      throw Exception(
        'Server not ready (HTTP ${streamedResponse.statusCode}). '
        'Please reload your web app on PythonAnywhere.'
      );
    }

    if (streamedResponse.statusCode == 200) {
      return jsonDecode(responseString);
    } else {
      final body = jsonDecode(responseString);
      throw Exception(body['message'] ?? 'Failed to upload file (HTTP ${streamedResponse.statusCode})');
    }
  }
}
