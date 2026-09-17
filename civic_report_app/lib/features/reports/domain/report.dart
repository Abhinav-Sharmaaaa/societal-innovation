class Report {
  Report({
    required this.id,
    required this.description,
    this.categoryId,
    required this.latitude,
    required this.longitude,
    required this.isAnonymous,
    required this.mediaUrls,
    required this.status,
    this.statusReason,
    required this.upvotes,
    required this.createdAt,
    this.reporterId,
    this.isOwn = false,
    this.upvotedByMe = false,
  });

  final String id;
  final String description;
  final String? categoryId;
  final double latitude;
  final double longitude;
  final bool isAnonymous;
  final List<String> mediaUrls;
  final String status; // submitted | under_review | in_progress | resolved | rejected
  final String? statusReason;
  final int upvotes;
  final DateTime createdAt;
  final String? reporterId; // null when is_anonymous, or when viewed by others
  final bool isOwn; // true when the current user created this report
  final bool upvotedByMe; // true if the current user already upvoted this

  /// Whether the upvote button should be tappable at all for this
  /// report from the current user's perspective.
  bool get canUpvote => !isOwn && !upvotedByMe;

  factory Report.fromJson(Map<String, dynamic> json) {
    return Report(
      id: json['id'].toString(),
      description: json['description'] as String? ?? '',
      categoryId: json['category'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      isAnonymous: json['is_anonymous'] as bool? ?? false,
      mediaUrls: (json['media_urls'] as List?)?.map((e) => e.toString()).toList() ?? const [],
      status: json['status'] as String? ?? 'submitted',
      statusReason: json['status_reason'] as String?,
      upvotes: (json['upvotes'] as num?)?.toInt() ?? 0,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ?? DateTime.now(),
      reporterId: json['reporter_id']?.toString(),
      isOwn: json['is_own'] as bool? ?? false,
      upvotedByMe: json['upvoted_by_me'] as bool? ?? false,
    );
  }

  static const statusLabels = {
    'submitted': 'Submitted',
    'under_review': 'Under Review',
    'in_progress': 'In Progress',
    'resolved': 'Resolved',
    'rejected': 'Rejected',
  };

  String get statusLabel => statusLabels[status] ?? status;

  static const statusOrder = ['submitted', 'under_review', 'in_progress', 'resolved'];
}
