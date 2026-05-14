class SearchResult {
  final String filename;
  final String type;
  final String date;
  final String snippet;
  final double score;

  SearchResult({
    required this.filename,
    required this.type,
    required this.date,
    required this.snippet,
    required this.score,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      filename: json['filename'] ?? '',
      type: json['fileType'] ?? json['file_type'] ?? json['type'] ?? '',
      date: json['date'] ?? json['modifiedAt'] ?? json['created_at'] ?? '',
      snippet: json['snippet'] ?? '',
      score: (json['score'] ?? json['rank'] ?? 0.0).toDouble(),
    );
  }
}
