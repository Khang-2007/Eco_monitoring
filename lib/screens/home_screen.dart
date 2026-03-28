import 'package:flutter/material.dart';
import '../models/env_data.dart';
import '../models/history_item.dart';
import '../services/api_service.dart';
import '../widgets/stat_card.dart';
import '../widgets/aqi_chart.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  EnvData? envData;
  List<HistoryItem> history = [];
  bool isLoading = true;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    loadAllData();
  }

  Future<void> loadAllData() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final environment = await ApiService.fetchEnvironment();
      final aqiHistory = await ApiService.fetchAqiHistory();

      setState(() {
        envData = environment;
        history = aqiHistory;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = e.toString();
        isLoading = false;
      });
    }
  }

  String getAqiStatus(int aqi) {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for sensitive groups';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very unhealthy';
    return 'Hazardous';
  }

  String getActionTip(int aqi) {
    if (aqi <= 50) {
      return 'Không khí tốt. Phù hợp cho hoạt động ngoài trời.';
    }
    if (aqi <= 100) {
      return 'Không khí ở mức trung bình. Vẫn ổn, nhưng nên theo dõi nếu ở ngoài lâu.';
    }
    if (aqi <= 150) {
      return 'Nhóm nhạy cảm nên hạn chế vận động mạnh ngoài trời.';
    }
    if (aqi <= 200) {
      return 'Chất lượng không khí không tốt. Nên giảm thời gian hoạt động ngoài trời.';
    }
    return 'AQI cao. Nên ở trong nhà hoặc đeo khẩu trang khi ra ngoài.';
  }

  Widget buildHistorySection() {
    if (history.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('Chưa có dữ liệu lịch sử'),
        ),
      );
    }

    final latestItems = history.reversed.take(5).toList().reversed.toList();

    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Recent Records',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...latestItems.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: Text(
                        item.timestamp.length >= 16
                            ? item.timestamp.substring(0, 16)
                            : item.timestamp,
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                    Expanded(
                      child: Text('AQI ${item.aqi}', textAlign: TextAlign.end),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildBody() {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 42),
              const SizedBox(height: 12),
              Text(errorMessage!, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: loadAllData,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (envData == null) {
      return const Center(child: Text('Không có dữ liệu'));
    }

    final data = envData!;

    return RefreshIndicator(
      onRefresh: loadAllData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            elevation: 1,
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  const Text(
                    'Air Quality Index',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${data.aqi}',
                    style: const TextStyle(
                      fontSize: 46,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    getAqiStatus(data.aqi),
                    style: const TextStyle(fontSize: 15),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    data.city,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          StatCard(
            title: 'Temperature',
            value: '${data.temp.toStringAsFixed(1)} °C',
            icon: Icons.thermostat_outlined,
          ),
          StatCard(
            title: 'Humidity',
            value: '${data.humidity.toStringAsFixed(1)} %',
            icon: Icons.water_drop_outlined,
          ),
          StatCard(
            title: 'Last Update',
            value: data.timestamp,
            icon: Icons.access_time,
            subtitle: 'Synced from backend API',
          ),
          const SizedBox(height: 12),
          AqiChart(history: history),
          const SizedBox(height: 12),
          Card(
            elevation: 1,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Action Tips',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    getActionTip(data.aqi),
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          buildHistorySection(),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: loadAllData,
            icon: const Icon(Icons.refresh),
            label: const Text('Refresh Data'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('EcoMonitor App'), centerTitle: true),
      body: buildBody(),
    );
  }
}
