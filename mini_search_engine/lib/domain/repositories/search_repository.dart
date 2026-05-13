abstract class SearchRepository {
  Future<Map<String, dynamic>> search(String query, {String? dateFrom, String? dateTo, String? fileType});
  Future<Map<String, dynamic>> getStats();
  Future<Map<String, dynamic>> buildIndex(List<String> formats, String folder);
}
