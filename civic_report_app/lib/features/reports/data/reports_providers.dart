import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../domain/report.dart';
import 'reports_repository.dart';

final reportsRepositoryProvider = Provider<ReportsRepository>((ref) {
  return ReportsRepository(ref.watch(dioProvider));
});

class ReportsFilter {
  const ReportsFilter({this.latitude, this.longitude, this.radiusKm, this.category, this.status});
  final double? latitude;
  final double? longitude;
  final double? radiusKm;
  final String? category;
  final String? status;

  ReportsFilter copyWith({String? category, String? status}) => ReportsFilter(
        latitude: latitude,
        longitude: longitude,
        radiusKm: radiusKm,
        category: category,
        status: status,
      );

  @override
  bool operator ==(Object other) =>
      other is ReportsFilter &&
      other.latitude == latitude &&
      other.longitude == longitude &&
      other.radiusKm == radiusKm &&
      other.category == category &&
      other.status == status;

  @override
  int get hashCode => Object.hash(latitude, longitude, radiusKm, category, status);
}

final nearbyReportsProvider =
    FutureProvider.family<List<Report>, ReportsFilter>((ref, filter) async {
  final repo = ref.watch(reportsRepositoryProvider);
  return repo.listReports(
    lat: filter.latitude,
    lng: filter.longitude,
    radiusKm: filter.radiusKm ?? 10,
    category: filter.category,
    status: filter.status,
  );
});

final reportDetailProvider = FutureProvider.family<Report, String>((ref, id) async {
  final repo = ref.watch(reportsRepositoryProvider);
  return repo.getReport(id);
});

final myRemoteReportsProvider = FutureProvider<List<Report>>((ref) async {
  final repo = ref.watch(reportsRepositoryProvider);
  return repo.myReports();
});
