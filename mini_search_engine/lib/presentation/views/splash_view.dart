import 'package:flutter/material.dart';
import 'package:animate_do/animate_do.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'onboarding_view.dart';
import 'auth_view.dart';
import 'home_view.dart';

class SplashView extends StatefulWidget {
  const SplashView({super.key});

  @override
  State<SplashView> createState() => _SplashViewState();
}

class _SplashViewState extends State<SplashView> {
  @override
  void initState() {
    super.initState();
    _checkAppState();
  }

  Future<void> _checkAppState() async {
    await Future.delayed(const Duration(seconds: 3)); // Show splash for 3s
    
    final prefs = await SharedPreferences.getInstance();
    final seenOnboard = prefs.getBool('seenOnboard') ?? false;

    if (!mounted) return;

    if (!seenOnboard) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const OnboardingView()));
    } else {
      final session = Supabase.instance.client.auth.currentSession;
      if (session != null) {
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeView()));
      } else {
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const AuthView()));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF0F2027), Color(0xFF203A43), Color(0xFF2C5364)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ZoomIn(
                duration: const Duration(milliseconds: 1000),
                child: const Icon(Icons.rocket_launch, size: 100, color: Colors.cyanAccent),
              ),
              const SizedBox(height: 20),
              FadeInUp(
                duration: const Duration(milliseconds: 1000),
                delay: const Duration(milliseconds: 500),
                child: const Text(
                  'Mini Search Engine',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
              ),
              const SizedBox(height: 40),
              FadeIn(
                delay: const Duration(milliseconds: 1500),
                child: const CircularProgressIndicator(color: Colors.cyanAccent),
              )
            ],
          ),
        ),
      ),
    );
  }
}
