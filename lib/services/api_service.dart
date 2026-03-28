import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/env_data.dart';
import '../models/history_item.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:5000';

  static Future<EnvData> fetchEnvironment() async {
    final response = await http.get(Uri.parse('$baseUrl/api/environment'));

    if (response.statusCode != 200) {
      throw Exception('Failed to load environment data');
    }

    final decoded = json.decode(response.body) as Map<String, dynamic>;

    if (decoded['status'] != 'success' || decoded['data'] == null) {
      throw Exception('Invalid environment response');
    }

    return EnvData.fromJson(decoded['data'] as Map<String, dynamic>);
  }

  static Future<List<HistoryItem>> fetchAqiHistory() async {
    final response = await http.get(Uri.parse('$baseUrl/api/history/aqi'));

    if (response.statusCode != 200) {
      throw Exception('Failed to load AQI history');
    }

    final decoded = json.decode(response.body) as Map<String, dynamic>;

    if (decoded['status'] != 'success' || decoded['data'] == null) {
      throw Exception('Invalid history response');
    }

    final rawList = decoded['data'] as List<dynamic>;

    return rawList
        .map((item) => HistoryItem.fromJson(item as Map<String, dynamic>))
        .toList()
        .reversed
        .toList();
  }
}
