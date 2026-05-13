import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:animate_do/animate_do.dart';
import '../../viewmodels/search_viewmodel.dart';
import '../../widgets/glass_card.dart';

class StatsTab extends StatelessWidget {
  const StatsTab({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<SearchViewModel>();
    final stats = vm.stats;

    if (stats == null) return const Center(child: CircularProgressIndicator(color: Colors.cyanAccent));
    if (stats['total_docs'] == 0) return const Center(child: Text('No documents indexed yet.', style: TextStyle(color: Colors.white, fontSize: 18)));

    final typeBreakdown = stats['type_breakdown'] as Map<String, dynamic>? ?? {};
    final topTerms = stats['top_terms'] as List<dynamic>? ?? [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          FadeInDown(
            child: Row(
              children: [
                Expanded(child: _buildStatCard(stats['total_docs'].toString(), 'Total Documents', Icons.file_copy)),
                const SizedBox(width: 16),
                Expanded(child: _buildStatCard(stats['unique_terms'].toString(), 'Unique Terms', Icons.text_fields)),
              ],
            ),
          ),
          const SizedBox(height: 30),
          
          FadeInLeft(
            child: const Text('Documents by Type', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 16),
          FadeIn(
            child: Wrap(
              spacing: 16,
              runSpacing: 16,
              children: typeBreakdown.entries.map((e) => SizedBox(width: 140, child: _buildStatCard(e.value.toString(), e.key.toUpperCase(), Icons.insert_drive_file))).toList(),
            ),
          ),
          const SizedBox(height: 30),
          
          FadeInLeft(
            child: const Text('Top Frequent Terms', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 16),
          FadeIn(
            child: Wrap(
              spacing: 16,
              runSpacing: 16,
              children: topTerms.map((e) => SizedBox(width: 140, child: _buildStatCard(e[1].toString(), '"${e[0]}"', Icons.trending_up, isTerm: true))).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String value, String label, IconData icon, {bool isTerm = false}) {
    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          Icon(icon, color: isTerm ? Colors.amberAccent : Colors.cyanAccent, size: 32),
          const SizedBox(height: 12),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(color: Colors.white70, fontSize: 14, fontWeight: FontWeight.w500), textAlign: TextAlign.center),
        ],
      ),
    );
  }
}
