class SearchResult {
  final String filename;
  final String type;
  final double score;
  final String date;
  final String snippet;

  SearchResult({
    required this.filename,
    required this.type,
    required this.score,
    required this.date,
    required this.snippet,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      filename: json['filename'] ?? '',
      type: json['type'] ?? '',
      score: (json['score'] ?? 0).toDouble(),
      date: json['date'] ?? '',
      snippet: json['snippet'] ?? '',
    );
  }
}
