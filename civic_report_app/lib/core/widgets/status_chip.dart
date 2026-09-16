import 'package:flutter/material.dart';

import '../../features/reports/domain/report.dart';

/// Consistent, color-coded status chip -- used on Home, My Reports, and
/// Report Detail so a report's status reads the same color everywhere
/// instead of every screen picking its own flat chip color.
class StatusChip extends StatelessWidget {
  const StatusChip({super.key, required this.status, this.compact = true});

  final String status;
  final bool compact;

  static const _colors = {
    'submitted': Color(0xFF5C6BC0), // indigo
    'under_review': Color(0xFFF9A825), // amber
    'in_progress': Color(0xFF8E24AA), // purple
    'resolved': Color(0xFF2E7D32), // green
    'rejected': Color(0xFFC62828), // red
  };

  static Color colorFor(String status) => _colors[status] ?? Colors.grey;

  Color get _color => colorFor(status);

  @override
  Widget build(BuildContext context) {
    final label = Report.statusLabels[status] ?? status;
    return Chip(
      label: Text(
        label,
        style: TextStyle(fontSize: compact ? 11 : 13, color: _color, fontWeight: FontWeight.w600),
      ),
      backgroundColor: _color.withValues(alpha: 0.12),
      visualDensity: compact ? VisualDensity.compact : VisualDensity.standard,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      side: BorderSide(color: _color.withValues(alpha: 0.3)),
    );
  }
}
