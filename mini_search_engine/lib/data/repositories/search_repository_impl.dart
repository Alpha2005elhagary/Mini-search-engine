import '../../domain/repositories/search_repository.dart';
import '../datasources/search_remote_data_source.dart';

class SearchRepositoryImpl implements SearchRepository {
  final SearchRemoteDataSource remoteDataSource;

  SearchRepositoryImpl(this.remoteDataSource);

  @override
  Future<Map<String, dynamic>> search(String query, {String? dateFrom, String? dateTo, String? fileType}) async {
    return await remoteDataSource.search(query, dateFrom: dateFrom, dateTo: dateTo, fileType: fileType);
  }

  @override
  Future<Map<String, dynamic>> getStats() async {
    return await remoteDataSource.getStats();
  }

  @override
  Future<Map<String, dynamic>> buildIndex(List<String> formats, String folder) async {
    return await remoteDataSource.buildIndex(formats, folder);
  }
}
