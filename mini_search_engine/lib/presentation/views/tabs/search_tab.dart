import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:animate_do/animate_do.dart';
import '../../viewmodels/search_viewmodel.dart';
import '../../widgets/glass_card.dart';

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
  
  int _currentPage = 0;
  final int _resultsPerPage = 5;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _performSearch() {
    setState(() => _currentPage = 0);
    context.read<SearchViewModel>().search(
      _searchController.text,
      fileType: _selectedFileType,
      dateFrom: _dateFrom?.toIso8601String().split('T')[0],
      dateTo: _dateTo?.toIso8601String().split('T')[0],
    );
  }

  Future<void> _selectDate(BuildContext context, bool isFrom) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime(2101),
    );
    if (picked != null) {
      setState(() {
        if (isFrom) _dateFrom = picked;
        else _dateTo = picked;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<SearchViewModel>();
    final totalResults = vm.results.length;
    final totalPages = (totalResults / _resultsPerPage).ceil();
    final startIdx = _currentPage * _resultsPerPage;
    final endIdx = (startIdx + _resultsPerPage > totalResults) ? totalResults : startIdx + _resultsPerPage;
    final paginatedResults = vm.results.sublist(startIdx, endIdx);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
      child: Column(
        children: [
          FadeInDown(
            duration: const Duration(milliseconds: 500),
            child: GlassCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
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
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(15),
                              borderSide: BorderSide.none,
                            ),
                            prefixIcon: const Icon(Icons.search, color: Colors.cyanAccent),
                          ),
                          onSubmitted: (_) => _performSearch(),
                        ),
                      ),
                      const SizedBox(width: 12),
                      GestureDetector(
                        onTap: _performSearch,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(colors: [Colors.cyan, Colors.blueAccent]),
                            borderRadius: BorderRadius.circular(15),
                            boxShadow: [BoxShadow(color: Colors.cyan.withOpacity(0.4), blurRadius: 10, offset: const Offset(0, 4))],
                          ),
                          child: const Text('Search', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _buildFilterDropdown(),
                        const SizedBox(width: 10),
                        _buildFilterButton(
                          icon: Icons.calendar_month,
                          label: _dateFrom != null ? _dateFrom!.toIso8601String().split('T')[0] : 'From',
                          onTap: () => _selectDate(context, true),
                          onClear: _dateFrom != null ? () => setState(() => _dateFrom = null) : null,
                        ),
                        const SizedBox(width: 10),
                        _buildFilterButton(
                          icon: Icons.calendar_month,
                          label: _dateTo != null ? _dateTo!.toIso8601String().split('T')[0] : 'To',
                          onTap: () => _selectDate(context, false),
                          onClear: _dateTo != null ? () => setState(() => _dateTo = null) : null,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          if (vm.suggestion != null)
            FadeInLeft(
              child: Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orangeAccent.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orangeAccent),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.lightbulb_outline, color: Colors.orangeAccent),
                    const SizedBox(width: 10),
                    const Text('Did you mean: ', style: TextStyle(color: Colors.white70)),
                    Text(vm.suggestion!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    const Spacer(),
                    TextButton(
                      onPressed: () {
                        _searchController.text = vm.suggestion!;
                        _performSearch();
                      },
                      child: const Text('Yes', style: TextStyle(color: Colors.orangeAccent, fontWeight: FontWeight.bold)),
                    )
                  ],
                ),
              ),
            ),

          if (vm.isLoading)
            const Expanded(child: Center(child: CircularProgressIndicator(color: Colors.cyanAccent)))
          else if (vm.results.isEmpty && _searchController.text.isNotEmpty)
            Expanded(child: FadeInUp(child: const Center(child: Text('No results found.', style: TextStyle(color: Colors.white70, fontSize: 18)))))
          else
            Expanded(
              child: ListView.builder(
                itemCount: paginatedResults.length,
                physics: const BouncingScrollPhysics(),
                itemBuilder: (context, index) {
                  final result = paginatedResults[index];
                  return FadeInUp(
                    delay: Duration(milliseconds: 100 * index),
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: GlassCard(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.description, color: Colors.cyanAccent, size: 20),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    result.filename,
                                    style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(color: Colors.cyanAccent.withOpacity(0.2), borderRadius: BorderRadius.circular(8)),
                                  child: Text(result.type, style: const TextStyle(color: Colors.cyanAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              result.snippet.isEmpty ? 'No preview available' : result.snippet,
                              style: TextStyle(color: Colors.white.withOpacity(0.8), height: 1.5, fontSize: 14),
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                const Icon(Icons.star_border, color: Colors.amberAccent, size: 16),
                                const SizedBox(width: 4),
                                Text('Score: ${result.score.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white54, fontSize: 12)),
                                const Spacer(),
                                Text(result.date, style: const TextStyle(color: Colors.white54, fontSize: 12)),
                              ],
                            )
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),

          if (totalPages > 1)
            Padding(
              padding: const EdgeInsets.only(top: 10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(
                    icon: const Icon(Icons.chevron_left, color: Colors.cyanAccent),
                    onPressed: _currentPage > 0 ? () => setState(() => _currentPage--) : null,
                  ),
                  Text('Page ${_currentPage + 1} of $totalPages', style: const TextStyle(color: Colors.white70)),
                  IconButton(
                    icon: const Icon(Icons.chevron_right, color: Colors.cyanAccent),
                    onPressed: _currentPage < totalPages - 1 ? () => setState(() => _currentPage++) : null,
                  ),
                ],
              ),
            )
        ],
      ),
    );
  }

  Widget _buildFilterButton({required IconData icon, required String label, required VoidCallback onTap, VoidCallback? onClear}) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  Icon(icon, color: Colors.white70, size: 16),
                  const SizedBox(width: 6),
                  Text(label, style: const TextStyle(color: Colors.white)),
                ],
              ),
            ),
          ),
          if (onClear != null)
            InkWell(
              onTap: onClear,
              child: const Padding(
                padding: EdgeInsets.only(right: 8),
                child: Icon(Icons.close, color: Colors.white54, size: 16),
              ),
            )
        ],
      ),
    );
  }

  Widget _buildFilterDropdown() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          dropdownColor: const Color(0xFF203A43),
          value: _selectedFileType,
          icon: const Icon(Icons.arrow_drop_down, color: Colors.white70),
          hint: const Text('Type', style: TextStyle(color: Colors.white)),
          style: const TextStyle(color: Colors.white),
          items: ['TXT', 'PDF', 'JSON', 'CSV', 'XLSX'].map((String value) {
            return DropdownMenuItem<String>(value: value, child: Text(value));
          }).toList(),
          onChanged: (val) => setState(() => _selectedFileType = val),
        ),
      ),
    );
  }
}
