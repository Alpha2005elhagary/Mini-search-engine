import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/constants/api_constants.dart';
import 'data/datasources/search_remote_data_source.dart';
import 'data/repositories/search_repository_impl.dart';
import 'presentation/viewmodels/search_viewmodel.dart';
import 'presentation/views/splash_view.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase (Ensure you replace YOUR_SUPABASE_URL_HERE and KEY in api_constants.dart)
  try {
    await Supabase.initialize(
      url: ApiConstants.supabaseUrl,
      anonKey: ApiConstants.supabaseAnonKey,
    );
  } catch (e) {
    debugPrint('Supabase initialization failed or keys are missing: $e');
  }

  final remoteDataSource = SearchRemoteDataSource();
  final searchRepository = SearchRepositoryImpl(remoteDataSource);

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => SearchViewModel(searchRepository)),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mini Search Engine',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        textTheme: GoogleFonts.interTextTheme(Theme.of(context).textTheme),
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.cyan,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const SplashView(),
    );
  }
}
