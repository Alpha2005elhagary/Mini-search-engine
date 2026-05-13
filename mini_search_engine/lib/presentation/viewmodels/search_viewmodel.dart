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

  bool _statsHasError = false;
  bool get statsHasError => _statsHasError;

  // New: Global navigation and filtering
  int _activeTabIndex = 0;
  int get activeTabIndex => _activeTabIndex;

  String? _predefinedFileType;
  String? get predefinedFileType => _predefinedFileType;

  void setTab(int index, {String? filterType}) {
    _activeTabIndex = index;
    _predefinedFileType = filterType;
    notifyListeners();
  }

  Future<void> search(String query, {String? dateFrom, String? dateTo, String? fileType}) async {
    if (query.isEmpty) return;
    _isLoading = true;
    notifyListeners();

    try {
      _saveSearchToSupabase(query);
      final response = await repository.search(query, dateFrom: dateFrom, dateTo: dateTo, fileType: fileType);
      _suggestion = response['suggestion'];
      
      // Filter out low-quality suggestions (especially for very short queries like 'if')
      if (_suggestion != null) {
        final q = query.toLowerCase().trim();
        final s = _suggestion!.toLowerCase().trim();
        
        // 1. Calculate similarity
        int dist = _levenshtein(q, s);
        int maxLen = q.length > s.length ? q.length : s.length;
        double similarity = 1.0 - (dist / maxLen);
        
        // 2. Suppress if similarity is too low OR it's just noise
        if (similarity < 0.4 || s.length < 3) {
          _suggestion = null;
        }
      }
      final List<dynamic> resultsJson = response['results'] ?? [];
      _results = resultsJson.map((json) => SearchResult.fromJson(json)).toList();
      
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
    _statsHasError = false;
    try {
      _stats = await repository.getStats();
      notifyListeners();
    } catch (e) {
      _statsHasError = true;
      if (kDebugMode) {
        print('Stats error: $e');
      }
      notifyListeners();
    }
  }

  // Alias for UI consistency
  Future<void> getStats() => fetchStats();

  Future<void> buildIndex(List<String> formats, String folder) async {
    _isBuilding = true;
    _buildMessage = "Indexing files... please wait";
    notifyListeners();

    try {
      final response = await repository.buildIndex(formats, folder);
      _buildMessage = response['message'];
      await fetchStats(); // Refresh stats
    } catch (e) {
      _buildMessage = "Error: $e";
      if (kDebugMode) print('Build index error: $e');
    } finally {
      _isBuilding = false;
      notifyListeners();
    }
  }

  Future<void> uploadFile(String name, List<int> bytes) async {
    _isBuilding = true;
    _buildMessage = "Uploading $name... please wait";
    notifyListeners();

    try {
      final response = await repository.uploadFile(name, bytes);
      _buildMessage = response['message'];
      await fetchStats(); // Automatically refresh stats after indexing
    } catch (e) {
      _buildMessage = "Error uploading file: $e";
      if (kDebugMode) print('Upload file error: $e');
    } finally {
      _isBuilding = false;
      notifyListeners();
    }
  }

  void clearBuildMessage() {
    _buildMessage = null;
    notifyListeners();
  }

  void reset() {
    _results = [];
    _stats = null;
    _suggestion = null;
    _statsHasError = false;
    _predefinedFileType = null;
    _activeTabIndex = 0;
    _buildMessage = null;
    notifyListeners();
  }

  Future<void> _saveSearchToSupabase(String query) async {
    try {
      final userId = Supabase.instance.client.auth.currentUser?.id;
      await Supabase.instance.client.from('search_history').insert({
        'query': query,
        'user_id': userId,
        'created_at': DateTime.now().toUtc().toIso8601String(),
      });
    } catch (e) {
      if (kDebugMode) print('Failed to save search to Supabase: $e');
    }
  }

  int _levenshtein(String s, String t) {
    if (s == t) return 0;
    if (s.isEmpty) return t.length;
    if (t.isEmpty) return s.length;
    final d = List.generate(s.length + 1, (i) => List.generate(t.length + 1, (j) => j == 0 ? i : (i == 0 ? j : 0)));
    for (int i = 1; i <= s.length; i++) {
      for (int j = 1; j <= t.length; j++) {
        final cost = s[i - 1] == t[j - 1] ? 0 : 1;
        d[i][j] = [d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost].reduce((a, b) => a < b ? a : b);
      }
    }
    return d[s.length][t.length];
  }
}
