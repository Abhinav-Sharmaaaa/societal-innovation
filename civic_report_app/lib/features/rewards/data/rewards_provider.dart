import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';

class Reward {
  Reward({
    required this.id,
    required this.business,
    required this.title,
    required this.pointsCost,
  });

  final String id;
  final String business;
  final String title;
  final int pointsCost;

  factory Reward.fromJson(Map<String, dynamic> json) {
    return Reward(
      id: json['id'].toString(),
      business: json['business'] as String? ?? '',
      title: json['title'] as String? ?? '',
      pointsCost: (json['points_cost'] as num?)?.toInt() ?? 0,
    );
  }
}

/// ASSUMPTION: GET /rewards/catalog returns
///   [{ id, business, title, points_cost }]
final rewardsCatalogProvider = FutureProvider<List<Reward>>((ref) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/rewards/catalog');
  final list = (response.data as List).cast<Map<String, dynamic>>();
  return list.map(Reward.fromJson).toList();
});

/// ASSUMPTION: POST /rewards/redeem accepts { reward_id } and returns
/// { id, reward_id, points_spent, remaining_points, redeemed_at } on
/// success, or a 400 with an error message if the user can't afford it.
class RewardsRepository {
  RewardsRepository(this._dio);
  final Dio _dio;

  Future<void> redeem(String rewardId) {
    return _dio.post('/rewards/redeem', data: {'reward_id': rewardId});
  }
}

final rewardsRepositoryProvider = Provider<RewardsRepository>((ref) {
  return RewardsRepository(ref.watch(dioProvider));
});
