class HistoryItem {
  final int id;
  final String city;
  final int aqi;
  final double temp;
  final double humidity;
  final String timestamp;

  HistoryItem({
    required this.id,
    required this.city,
    required this.aqi,
    required this.temp,
    required this.humidity,
    required this.timestamp,
  });

  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      id: json['id'] ?? 0,
      city: (json['city'] ?? 'Unknown').toString(),
      aqi: (json['aqi'] ?? 0) as int,
      temp: (json['temp'] ?? 0).toDouble(),
      humidity: (json['humidity'] ?? 0).toDouble(),
      timestamp: (json['timestamp'] ?? '').toString(),
    );
  }
}
