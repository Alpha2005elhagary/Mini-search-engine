import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:animate_do/animate_do.dart';
import 'package:shimmer/shimmer.dart';
import '../../viewmodels/search_viewmodel.dart';
import '../../widgets/glass_card.dart';
import '../document_detail_view.dart';
import '../../../domain/entities/search_result.dart';

class SearchTab extends StatefulWidget {
  const SearchTab({super.key});

  @override
  State<SearchTab> createState() => _SearchTabState();
}

class _SearchTabState extends State<SearchTab> {
  final TextEditingController _searchController = TextEditingController();
  String? _selectedFileType;
  DateTime? _dateFrom;
  DateTime? _dateTo;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();
    super.initState();
  }

  void _onSearchChanged() {
    context.read<SearchViewModel>().fetchLiveSuggestions(_searchController.text);
  }

  void _performSearch({int page = 1}) {
    context.read<SearchViewModel>().search(
      _searchController.text,
      fileType: _selectedFileType,
      dateFrom: _dateFrom?.toIso8601String(),
      dateTo: _dateTo?.toIso8601String(),
      page: page,
    );
  }

  void _showDocumentDetail(SearchResult result) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DocumentDetailView(
          result: result,
          query: _searchController.text,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<SearchViewModel>();
    final results = vm.results;
    final totalPages = (vm.totalResults / vm.pageSize).ceil();

    if (vm.predefinedFileType != null && _selectedFileType != vm.predefinedFileType) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        setState(() => _selectedFileType = vm.predefinedFileType);
        _performSearch();
      });
    }

    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
        child: Column(
          children: [
            FadeInDown(
              child: GlassCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    _buildSearchBar(vm),
                    if (vm.liveSuggestions.isNotEmpty) _buildLiveSuggestions(vm),
                    const SizedBox(height: 12),
                    _buildFilters(),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            
            if (vm.suggestion != null && results.isEmpty) _buildSuggestionTile(vm),
            
            if (vm.isLoading) 
              _buildShimmerResults()
            else if (results.isEmpty && _searchController.text.isEmpty)
              _buildEmptyState(vm)
            else if (results.isEmpty)
              const Center(child: Text('No results found.', style: TextStyle(color: Colors.white70, fontSize: 18)))
            else
              _buildResultsList(vm, results, totalPages),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchBar(SearchViewModel vm) {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _searchController,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Search anything...',
              hintStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
              filled: true,
              fillColor: Colors.white.withOpacity(0.1),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: BorderSide.none),
              prefixIcon: const Icon(Icons.search, color: Colors.cyanAccent),
            ),
            onSubmitted: (_) => _performSearch(),
          ),
        ),
        const SizedBox(width: 12),
        ElevatedButton(
          onPressed: () => _performSearch(),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            backgroundColor: Colors.cyan,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
          ),
          child: const Text('Search', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget _buildLiveSuggestions(SearchViewModel vm) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        children: vm.liveSuggestions.map((s) => ListTile(
          title: Text(s, style: const TextStyle(color: Colors.white70)),
          leading: const Icon(Icons.history, color: Colors.white38, size: 18),
          onTap: () {
            _searchController.text = s;
            _performSearch();
          },
        )).toList(),
      ),
    );
  }

  Widget _buildShimmerResults() {
    return Shimmer.fromColors(
      baseColor: Colors.white10,
      highlightColor: Colors.white24,
      child: ListView.builder(
        shrinkWrap: true,
        itemCount: 3,
        itemBuilder: (_, __) => Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Container(height: 120, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16))),
        ),
      ),
    );
  }

  Widget _buildEmptyState(SearchViewModel vm) {
    return Column(
      children: [
        const Icon(Icons.search_off, size: 80, color: Colors.white10),
        const SizedBox(height: 16),
        const Text('Start your research...', style: TextStyle(color: Colors.white24, fontSize: 18)),
        if (vm.history.isNotEmpty) ...[
          const SizedBox(height: 30),
          const Text('Recent Searches', style: TextStyle(color: Colors.white70, fontSize: 14)),
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            children: vm.history.map((h) => ActionChip(
              label: Text(h),
              backgroundColor: Colors.white10,
              labelStyle: const TextStyle(color: Colors.cyanAccent),
              onPressed: () {
                _searchController.text = h;
                _performSearch();
              },
            )).toList(),
          ),
        ]
      ],
    );
  }

  Widget _buildResultsList(SearchViewModel vm, List<SearchResult> results, int totalPages) {
    return Column(
      children: [
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: results.length,
          itemBuilder: (context, index) => _buildResultCard(results[index], index),
        ),
        if (totalPages > 1) _buildPagination(vm, totalPages),
      ],
    );
  }

  Widget _buildResultCard(SearchResult result, int index) {
    return FadeInUp(
      delay: Duration(milliseconds: 100 * index),
      child: Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: GlassCard(
          onTap: () => _showDocumentDetail(result),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(child: Text(result.filename, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16))),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(color: Colors.cyanAccent.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                    child: Text('${(result.score * 100).toInt()}%', style: const TextStyle(color: Colors.cyanAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              RichText(
                text: _buildSnippetText(result.snippet),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(result.type.toUpperCase(), style: const TextStyle(color: Colors.cyanAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                  Text(result.date.split('T')[0], style: const TextStyle(color: Colors.white38, fontSize: 12)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFilters() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _buildTypeDropdown(),
          const SizedBox(width: 10),
          _buildDateButton('From', _dateFrom, (d) => setState(() => _dateFrom = d)),
          const SizedBox(width: 10),
          _buildDateButton('To', _dateTo, (d) => setState(() => _dateTo = d)),
        ],
      ),
    );
  }

  Widget _buildTypeDropdown() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(color: Colors.white.withOpacity(0.05), borderRadius: BorderRadius.circular(12)),
      child: DropdownButton<String>(
        value: _selectedFileType,
        hint: const Text('Type', style: TextStyle(color: Colors.white70, fontSize: 14)),
        dropdownColor: const Color(0xFF0F172A),
        underline: const SizedBox(),
        items: ['PDF', 'TXT', 'JSON', 'XLSX', 'CSV'].map((t) => DropdownMenuItem(value: t, child: Text(t, style: const TextStyle(color: Colors.white)))).toList(),
        onChanged: (v) => setState(() => _selectedFileType = v),
      ),
    );
  }

  Widget _buildDateButton(String label, DateTime? date, Function(DateTime?) onSelected) {
    return ActionChip(
      avatar: const Icon(Icons.calendar_today, size: 14, color: Colors.cyanAccent),
      label: Text(date != null ? date.toIso8601String().split('T')[0] : label, style: const TextStyle(color: Colors.white70)),
      backgroundColor: Colors.white.withOpacity(0.05),
      onPressed: () async {
        final d = await showDatePicker(context: context, initialDate: DateTime.now(), firstDate: DateTime(2000), lastDate: DateTime.now());
        if (d != null) onSelected(d);
      },
    );
  }

  Widget _buildPagination(SearchViewModel vm, int total) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(icon: const Icon(Icons.chevron_left, color: Colors.cyanAccent), onPressed: vm.currentPage > 1 ? () => _performSearch(page: vm.currentPage - 1) : null),
        Text('Page ${vm.currentPage} of $total', style: const TextStyle(color: Colors.white70)),
        IconButton(icon: const Icon(Icons.chevron_right, color: Colors.cyanAccent), onPressed: vm.currentPage < total ? () => _performSearch(page: vm.currentPage + 1) : null),
      ],
    );
  }

  Widget _buildSuggestionTile(SearchViewModel vm) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: ActionChip(
        avatar: const Icon(Icons.lightbulb_outline, size: 16, color: Colors.amberAccent),
        label: Text('Did you mean: ${vm.suggestion}?', style: const TextStyle(color: Colors.amberAccent)),
        backgroundColor: Colors.amberAccent.withOpacity(0.1),
        onPressed: () {
          _searchController.text = vm.suggestion!;
          _performSearch();
        },
      ),
    );
  }

  TextSpan _buildSnippetText(String snippet) {
    final List<TextSpan> spans = [];
    final regExp = RegExp(r'<mark>(.*?)</mark>');
    int lastIndex = 0;

    for (final match in regExp.allMatches(snippet)) {
      if (match.start > lastIndex) {
        spans.add(TextSpan(
          text: snippet.substring(lastIndex, match.start),
          style: const TextStyle(color: Colors.white70, fontSize: 14),
        ));
      }
      spans.add(TextSpan(
        text: match.group(1),
        style: const TextStyle(
          color: Colors.cyanAccent,
          fontWeight: FontWeight.bold,
          fontSize: 15,
          backgroundColor: Colors.white10,
        ),
      ));
      lastIndex = match.end;
    }

    if (lastIndex < snippet.length) {
      spans.add(TextSpan(
        text: snippet.substring(lastIndex),
        style: const TextStyle(color: Colors.white70, fontSize: 14),
      ));
    }

    return TextSpan(children: spans);
  }
}
