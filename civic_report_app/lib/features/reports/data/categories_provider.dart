import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';

/// ASSUMPTION: GET /categories returns a flat array of
/// { "id": "...", "label": "..." }. Category selection is optional
/// end-to-end per spec — this provider failing or returning empty must
/// never block report submission (handled in the UI, not here).
class ReportCategory {
  ReportCategory({required this.id, required this.label});
  final String id;
  final String label;

  factory ReportCategory.fromJson(Map<String, dynamic> json) {
    return ReportCategory(id: json['id'].toString(), label: json['label'] as String);
  }
}

final categoriesProvider = FutureProvider<List<ReportCategory>>((ref) async {
  final dio = ref.watch(dioProvider);
  try {
    final response = await dio.get('/categories');
    final list = (response.data as List).cast<Map<String, dynamic>>();
    return list.map(ReportCategory.fromJson).toList();
  } catch (_) {
    // Never surface this as a blocking error — category is optional.
    return <ReportCategory>[];
  }
});
