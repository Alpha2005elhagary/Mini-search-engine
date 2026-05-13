import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:animate_do/animate_do.dart';
import 'package:file_picker/file_picker.dart';
import '../../viewmodels/search_viewmodel.dart';
import '../../widgets/glass_card.dart';

class IndexTab extends StatefulWidget {
  const IndexTab({super.key});

  @override
  State<IndexTab> createState() => _IndexTabState();
}

class _IndexTabState extends State<IndexTab> {
  final Map<String, bool> _buildFormats = {
    '.txt': true, '.pdf': true, '.json': true, '.csv': true, '.xlsx': true,
  };

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<SearchViewModel>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: FadeIn(
        child: GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.auto_awesome, color: Colors.cyanAccent, size: 28),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Supabase Indexing', 
                      style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              
              if (vm.buildMessage != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 20),
                  decoration: BoxDecoration(
                    color: vm.buildMessage!.contains('Error') || vm.buildMessage!.contains('Failed') 
                        ? Colors.redAccent.withOpacity(0.2) : Colors.greenAccent.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: vm.buildMessage!.contains('Error') || vm.buildMessage!.contains('Failed') 
                        ? Colors.redAccent : Colors.greenAccent),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Expanded(child: Text(vm.buildMessage!, style: const TextStyle(color: Colors.white))),
                          IconButton(icon: const Icon(Icons.close, color: Colors.white), onPressed: () => vm.clearBuildMessage()),
                        ],
                      ),
                      if (vm.buildMessage!.contains('indexed successfully'))
                        Padding(
                          padding: const EdgeInsets.only(top: 8.0),
                          child: TextButton.icon(
                            onPressed: () => vm.setTab(0),
                            icon: const Icon(Icons.search, color: Colors.greenAccent),
                            label: const Text('GO TO SEARCH', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                          ),
                        )
                    ],
                  ),
                ),
                
              const Text(
                'Upload files to automatically index them in your serverless search engine. Supported formats:', 
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: _buildFormats.keys.map((format) {
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.cyanAccent.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.cyanAccent.withOpacity(0.3)),
                    ),
                    child: Text(format.toUpperCase(), style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                  );
                }).toList(),
              ),
              const SizedBox(height: 40),
              
              SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                    padding: EdgeInsets.zero,
                  ),
                  onPressed: vm.isBuilding ? null : () async {
                    FilePickerResult? result = await FilePicker.pickFiles(withData: true);
                    if (result != null) {
                      final fileBytes = result.files.first.bytes;
                      final fileName = result.files.first.name;
                      if (fileBytes != null) {
                        vm.uploadFile(fileName, fileBytes.toList());
                      }
                    }
                  },
                  child: Ink(
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(colors: [Colors.purpleAccent, Colors.deepPurpleAccent]),
                      borderRadius: BorderRadius.circular(15),
                      boxShadow: [BoxShadow(color: Colors.purple.withOpacity(0.4), blurRadius: 10, offset: const Offset(0, 4))],
                    ),
                    child: Center(
                      child: vm.isBuilding 
                          ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.cloud_upload, color: Colors.white),
                                SizedBox(width: 10),
                                Text('UPLOAD & INDEX FILE', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                              ],
                            ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              
              SizedBox(
                width: double.infinity,
                height: 55,
                child: OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.cyanAccent),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                  ),
                  onPressed: () => vm.getStats(),
                  child: const Text('REFRESH DATABASE STATS', style: TextStyle(color: Colors.cyanAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
