import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../domain/repositories/search_repository.dart';
import '../../domain/entities/search_result.dart';

class SearchViewModel extends ChangeNotifier {
  final SearchRepository repository;

  SearchViewModel(this.repository);

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  List<String> _history = [];
  List<String> get history => _history;

  List<String> _liveSuggestions = [];
  List<String> get liveSuggestions => _liveSuggestions;

  bool _isBuilding = false;
  bool get isBuilding => _isBuilding;

  String? _buildMessage;
  String? get buildMessage => _buildMessage;

  List<SearchResult> _results = [];
  List<SearchResult> get results => _results;

  String? _suggestion;
  String? get suggestion => _suggestion;

  int _totalResults = 0;
  int get totalResults => _totalResults;

  int _currentPage = 1;
  int get currentPage => _currentPage;
  
  final int _pageSize = 5;
  int get pageSize => _pageSize;

  Map<String, dynamic>? _stats;
  Map<String, dynamic>? get stats => _stats;

  bool _statsHasError = false;
  bool get statsHasError => _statsHasError;

  int _activeTabIndex = 0;
  int get activeTabIndex => _activeTabIndex;

  String? _predefinedFileType;
  String? get predefinedFileType => _predefinedFileType;

  void setTab(int index, {String? filterType}) {
    _activeTabIndex = index;
    _predefinedFileType = filterType;
    notifyListeners();
  }

  Future<void> fetchLiveSuggestions(String input) async {
    if (input.length < 2) {
      _liveSuggestions = [];
      notifyListeners();
      return;
    }
    try {
      final userId = Supabase.instance.client.auth.currentUser?.id;
      final List<dynamic> data = await Supabase.instance.client.rpc('get_live_suggestions', params: {
        'p_input': input,
        'p_user_id': userId,
      });
      _liveSuggestions = data.map((e) => e['term'].toString()).toList();
      notifyListeners();
    } catch (e) {
      print('Suggestion error: $e');
    }
  }

  void addToHistory(String query) {
    if (!_history.contains(query)) {
      _history.insert(0, query);
      if (_history.length > 5) _history.removeLast();
      notifyListeners();
    }
  }

  Future<void> search(String query, {String? dateFrom, String? dateTo, String? fileType, int page = 1}) async {
    if (query.isEmpty) {
      _results = [];
      _totalResults = 0;
      notifyListeners();
      return;
    }
    _isLoading = true;
    _currentPage = page;
    _liveSuggestions = []; // Clear suggestions when searching
    notifyListeners();

    try {
      if (page == 1) {
        _saveSearchToSupabase(query);
        addToHistory(query);
      }
      
      final response = await repository.search(
        query, 
        dateFrom: dateFrom, 
        dateTo: dateTo, 
        fileType: fileType,
        page: page,
        limit: _pageSize,
      );
      
      _suggestion = response['suggestion'];
      _totalResults = response['totalCount'] ?? 0;
      
      final List<dynamic> resultsJson = response['results'] ?? [];
      _results = resultsJson.map((json) => SearchResult.fromJson(json)).toList();
      
    } catch (e) {
      print('Search error: $e');
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
      notifyListeners();
    }
  }

  Future<void> getStats() => fetchStats();

  Future<void> buildIndex(List<String> formats, String folder) async {
    _isBuilding = true;
    _buildMessage = "Indexing files... please wait";
    notifyListeners();

    try {
      final response = await repository.buildIndex(formats, folder);
      _buildMessage = response['message'];
      await fetchStats();
    } catch (e) {
      _buildMessage = "Error: $e";
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
      await fetchStats();
    } catch (e) {
      _buildMessage = "Error uploading file: $e";
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
    _totalResults = 0;
    _currentPage = 1;
    _stats = null;
    _suggestion = null;
    _statsHasError = false;
    _predefinedFileType = null;
    _activeTabIndex = 0;
    _buildMessage = null;
    _history = [];
    _liveSuggestions = [];
    notifyListeners();
  }

  Future<void> _saveSearchToSupabase(String query) async {
    try {
      final userId = Supabase.instance.client.auth.currentUser?.id;
      await Supabase.instance.client.from('search_history').insert({
        'query': query,
        'user_id': userId,
      });
    } catch (e) {
      print('Failed to save search: $e');
    }
  }
}
