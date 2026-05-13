class SearchResult {
  final String filename;
  final String type;
  final String date;
  final String snippet;

  SearchResult({
    required this.filename,
    required this.type,
    required this.date,
    required this.snippet,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      filename: json['filename'] ?? '',
      type: json['fileType'] ?? json['file_type'] ?? json['type'] ?? '',
      date: json['date'] ?? json['modifiedAt'] ?? json['created_at'] ?? '',
      snippet: json['snippet'] ?? '',
    );
  }
}
