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
  final TextEditingController _folderController = TextEditingController(text: 'data');
  final Map<String, bool> _buildFormats = {
    '.txt': true, '.pdf': true, '.json': true, '.csv': true, '.xlsx': true,
  };

  @override
  void dispose() {
    _folderController.dispose();
    super.dispose();
  }

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
                  Icon(Icons.rocket_launch, color: Colors.cyanAccent, size: 28),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Build Document Index', 
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
                  child: Row(
                    children: [
                      Expanded(child: Text(vm.buildMessage!, style: const TextStyle(color: Colors.white))),
                      IconButton(icon: const Icon(Icons.close, color: Colors.white), onPressed: () => vm.clearBuildMessage()),
                    ],
                  ),
                ),
                
              const Text('Select file formats:', style: TextStyle(color: Colors.white70, fontSize: 16)),
              const SizedBox(height: 12),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: _buildFormats.keys.map((format) {
                  final isSelected = _buildFormats[format]!;
                  return InkWell(
                    onTap: () => setState(() => _buildFormats[format] = !isSelected),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: isSelected ? Colors.cyanAccent.withOpacity(0.2) : Colors.white.withOpacity(0.05),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: isSelected ? Colors.cyanAccent : Colors.white24),
                      ),
                      child: Text(format.toUpperCase(), style: TextStyle(color: isSelected ? Colors.cyanAccent : Colors.white70, fontWeight: FontWeight.bold)),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 30),
              
              const Text('Folder path:', style: TextStyle(color: Colors.white70, fontSize: 16)),
              const SizedBox(height: 12),
              TextField(
                controller: _folderController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'e.g., data',
                  hintStyle: const TextStyle(color: Colors.white38),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: const BorderSide(color: Colors.white24)),
                  enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: const BorderSide(color: Colors.white24)),
                  focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: const BorderSide(color: Colors.cyanAccent)),
                  prefixIcon: const Icon(Icons.folder, color: Colors.white54),
                ),
              ),
              const SizedBox(height: 30),
              
              SizedBox(
                width: double.infinity,
                height: 55,
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
                      gradient: const LinearGradient(colors: [Colors.purpleAccent, Colors.deepPurple]),
                      borderRadius: BorderRadius.circular(15),
                      boxShadow: [BoxShadow(color: Colors.purple.withOpacity(0.4), blurRadius: 10, offset: const Offset(0, 4))],
                    ),
                    child: Center(
                      child: vm.isBuilding 
                          ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Text('UPLOAD A FILE', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                    padding: EdgeInsets.zero,
                  ),
                  onPressed: vm.isBuilding ? null : () {
                    final formats = _buildFormats.entries.where((e) => e.value).map((e) => e.key).toList();
                    if (formats.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please select at least one format')));
                      return;
                    }
                    vm.buildIndex(formats, _folderController.text);
                  },
                  child: Ink(
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(colors: [Colors.cyan, Colors.blueAccent]),
                      borderRadius: BorderRadius.circular(15),
                      boxShadow: [BoxShadow(color: Colors.cyan.withOpacity(0.4), blurRadius: 10, offset: const Offset(0, 4))],
                    ),
                    child: Center(
                      child: vm.isBuilding 
                          ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Text('START INDEXING', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                    ),
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
