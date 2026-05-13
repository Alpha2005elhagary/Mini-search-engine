import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../viewmodels/search_viewmodel.dart';
import 'auth_view.dart';
import 'tabs/search_tab.dart';
import 'tabs/index_tab.dart';
import 'tabs/stats_tab.dart';

class HomeView extends StatefulWidget {
  const HomeView({super.key});

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<SearchViewModel>().fetchStats();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _handleLogout() async {
    await Supabase.instance.client.auth.signOut();
    if (mounted) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const AuthView()));
    }
  }
  @override
  Widget build(BuildContext context) {
    final vm = context.watch<SearchViewModel>();
    
    // Sync tab controller when VM state changes
    if (_tabController.index != vm.activeTabIndex) {
      _tabController.animateTo(vm.activeTabIndex);
    }

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text(
          'Mini Search Engine',
          style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: 1.2, color: Colors.white),
        ),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.cyanAccent),
            onPressed: _handleLogout,
            tooltip: 'Logout',
          )
        ],
        flexibleSpace: ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(color: Colors.black.withOpacity(0.2)),
          ),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.cyanAccent,
          indicatorWeight: 3,
          labelColor: Colors.cyanAccent,
          unselectedLabelColor: Colors.white70,
          onTap: (index) => context.read<SearchViewModel>().setTab(index),
          tabs: const [
            Tab(icon: Icon(Icons.search_rounded), text: 'Search'),
            Tab(icon: Icon(Icons.auto_awesome_mosaic_rounded), text: 'Index'),
            Tab(icon: Icon(Icons.bar_chart_rounded), text: 'Stats'),
          ],
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF0F2027), Color(0xFF203A43), Color(0xFF2C5364)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: TabBarView(
            controller: _tabController,
            children: [
              SearchTab(),
              IndexTab(),
              StatsTab(),
            ],
          ),
        ),
      ),
    );
  }
}
