import '../../domain/repositories/search_repository.dart';
import '../datasources/search_remote_data_source.dart';

class SearchRepositoryImpl implements SearchRepository {
  final SearchRemoteDataSource remoteDataSource;

  SearchRepositoryImpl(this.remoteDataSource);

  @override
  Future<Map<String, dynamic>> search(String query, {String? dateFrom, String? dateTo, String? fileType, int page = 1, int limit = 5}) async {
    return await remoteDataSource.search(query, dateFrom: dateFrom, dateTo: dateTo, fileType: fileType, page: page, limit: limit);
  }

  @override
  Future<Map<String, dynamic>> getStats() async {
    return await remoteDataSource.getStats();
  }

  @override
  Future<Map<String, dynamic>> buildIndex(List<String> formats, String folder) async {
    return await remoteDataSource.buildIndex(formats, folder);
  }

  @override
  Future<Map<String, dynamic>> uploadFile(String name, List<int> bytes) async {
    return await remoteDataSource.uploadFile(name, bytes);
  }
}
