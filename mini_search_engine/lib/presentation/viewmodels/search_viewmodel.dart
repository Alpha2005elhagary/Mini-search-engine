import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../domain/repositories/search_repository.dart';
import '../../domain/entities/search_result.dart';

class SearchViewModel extends ChangeNotifier {
  final SearchRepository repository;

  SearchViewModel(this.repository);

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  bool _isBuilding = false;
  bool get isBuilding => _isBuilding;

  String? _buildMessage;
  String? get buildMessage => _buildMessage;

  List<SearchResult> _results = [];
  List<SearchResult> get results => _results;

  String? _suggestion;
  String? get suggestion => _suggestion;

  Map<String, dynamic>? _stats;
  Map<String, dynamic>? get stats => _stats;

  Future<void> search(String query, {String? dateFrom, String? dateTo, String? fileType}) async {
    if (query.isEmpty) return;
    _isLoading = true;
    notifyListeners();

    try {
      final response = await repository.search(query, dateFrom: dateFrom, dateTo: dateTo, fileType: fileType);
      _suggestion = response['suggestion'];
      final List<dynamic> resultsJson = response['results'] ?? [];
      _results = resultsJson.map((json) => SearchResult.fromJson(json)).toList();
      
      // Save to Supabase (non-blocking)
      _saveSearchToSupabase(query);
      
    } catch (e) {
      if (kDebugMode) {
        print('Search error: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchStats() async {
    try {
      _stats = await repository.getStats();
      notifyListeners();
    } catch (e) {
      if (kDebugMode) {
        print('Stats error: $e');
      }
    }
  }

  Future<void> buildIndex(List<String> formats, String folder) async {
    _isBuilding = true;
    _buildMessage = "Building index... please wait";
    notifyListeners();

    try {
      final response = await repository.buildIndex(formats, folder);
      _buildMessage = response['message'];
      await fetchStats(); // Refresh stats
    } catch (e) {
      _buildMessage = "Error building index: $e";
      if (kDebugMode) print('Build index error: $e');
    } finally {
      _isBuilding = false;
      notifyListeners();
    }
  }

  void clearBuildMessage() {
    _buildMessage = null;
    notifyListeners();
  }

  Future<void> _saveSearchToSupabase(String query) async {
    try {
      await Supabase.instance.client.from('search_history').insert({
        'query': query,
        'created_at': DateTime.now().toUtc().toIso8601String(),
      });
    } catch (e) {
      if (kDebugMode) print('Failed to save search to Supabase: $e');
    }
  }
}
