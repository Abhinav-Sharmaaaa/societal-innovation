import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart' as latlong;

import '../../../core/config/app_config.dart';
import '../../../core/router/app_router.dart';
import '../../../core/widgets/notifications_button.dart';
import '../../../core/widgets/state_views.dart';
import '../../../core/widgets/status_chip.dart';
import '../data/categories_provider.dart';
import '../data/location_service.dart';
import '../data/reports_providers.dart';
import '../domain/report.dart';

String _timeOfDayGreeting() {
  final hour = DateTime.now().hour;
  if (hour < 12) return 'Good Morning';
  if (hour < 17) return 'Good Afternoon';
  return 'Good Evening';
}

class HomeFeedScreen extends ConsumerStatefulWidget {
  const HomeFeedScreen({super.key});

  @override
  ConsumerState<HomeFeedScreen> createState() => _HomeFeedScreenState();
}

class _HomeFeedScreenState extends ConsumerState<HomeFeedScreen> {
  final _locationService = LocationService();

  // The viewport currently being queried -- starts at the user's GPS
  // fix, then follows wherever they pan/zoom the map (see _MiniMap's
  // onViewportChanged). This is deliberately separate from the raw GPS
  // position: "only the current area, unless the user moves the map."
  double? _viewLat;
  double? _viewLng;
  double _viewRadiusKm = 2;

  String? _locationError;
  String? _selectedCategory;
  bool _locating = true;

  @override
  void initState() {
    super.initState();
    _loadLocation();
  }

  Future<void> _loadLocation() async {
    try {
      final position = await _locationService.getCurrentLocation();
      if (!mounted) return;
      setState(() {
        _viewLat = position.latitude;
        _viewLng = position.longitude;
        _locating = false;
        _locationError = null;
      });
    } catch (e) {
      // Feed still works without location -- the map falls back to a
      // default center and the list just shows whatever the backend
      // returns for an unfiltered query -- but show the real reason so
      // it's actually debuggable instead of silently degrading.
      if (mounted) {
        setState(() {
          _locating = false;
          _locationError = e.toString();
        });
      }
    }
  }

  ReportsFilter get _filter => ReportsFilter(
        latitude: _viewLat,
        longitude: _viewLng,
        radiusKm: _viewRadiusKm,
        category: _selectedCategory,
      );

  void _onViewportChanged(latlong.LatLng center, double radiusKm) {
    setState(() {
      _viewLat = center.latitude;
      _viewLng = center.longitude;
      _viewRadiusKm = radiusKm;
    });
  }

  Future<void> _upvote(Report report) async {
    final repo = ref.read(reportsRepositoryProvider);
    try {
      await repo.upvote(report.id);
      HapticFeedback.selectionClick();
      ref.invalidate(nearbyReportsProvider);
    } on DioException catch (e) {
      if (!mounted) return;
      final message = e.response?.data is Map ? e.response?.data['error'] as String? : null;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message ?? 'Could not upvote -- check your connection.')),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not upvote -- check your connection.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final categoriesAsync = ref.watch(categoriesProvider);
    final reportsAsync = _locating ? null : ref.watch(nearbyReportsProvider(_filter));

    return Scaffold(
      appBar: AppBar(
        title: Text(_timeOfDayGreeting()),
        actions: const [NotificationsButton()],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(24),
          child: Padding(
            padding: const EdgeInsets.only(left: 16, bottom: 8),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                reportsAsync?.maybeWhen(
                      data: (list) => '${list.length} report${list.length == 1 ? '' : 's'} near you',
                      orElse: () => null,
                    ) ??
                    'Here\'s what\'s happening nearby',
                style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant, fontSize: 13),
              ),
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          if (_locationError != null)
            MaterialBanner(
              content: Text(_locationError!, style: const TextStyle(fontSize: 12)),
              leading: const Icon(Icons.location_off_outlined),
              actions: [
                TextButton(
                  onPressed: () {
                    setState(() {
                      _locationError = null;
                      _locating = true;
                    });
                    _loadLocation();
                  },
                  child: const Text('Retry'),
                ),
                TextButton(
                  onPressed: () => setState(() => _locationError = null),
                  child: const Text('Dismiss'),
                ),
              ],
            ),
          categoriesAsync.when(
            data: (categories) {
              if (categories.isEmpty) return const SizedBox.shrink();
              return SizedBox(
                height: 48,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: const Text('All'),
                        selected: _selectedCategory == null,
                        onSelected: (_) => setState(() => _selectedCategory = null),
                      ),
                    ),
                    ...categories.map(
                      (c) => Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(c.label),
                          selected: _selectedCategory == c.id,
                          onSelected: (_) => setState(
                            () => _selectedCategory = _selectedCategory == c.id ? null : c.id,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          Expanded(
            child: _locating
                ? const Center(child: CircularProgressIndicator())
                : reportsAsync!.when(
                    data: (reports) {
                      return RefreshIndicator(
                        onRefresh: () async => ref.invalidate(nearbyReportsProvider),
                        child: ListView(
                          padding: const EdgeInsets.all(12),
                          children: [
                            _MiniMap(
                              initialCenter: latlong.LatLng(_viewLat ?? 0, _viewLng ?? 0),
                              reports: reports,
                              onMarkerTap: (r) => context.push(AppRoutes.reportDetailPath(r.id)),
                              onViewportChanged: _onViewportChanged,
                            ),
                            const SizedBox(height: 12),
                            if (reports.isEmpty)
                              const Padding(
                                padding: EdgeInsets.symmetric(vertical: 24),
                                child: EmptyStateView(
                                  icon: Icons.map_outlined,
                                  message: 'No reports in this area yet.\nBe the first to flag something.',
                                ),
                              )
                            else
                              ...reports.map(
                                (report) => Padding(
                                  padding: const EdgeInsets.only(bottom: 8),
                                  child: _ReportCard(
                                    report: report,
                                    onTap: () => context.push(AppRoutes.reportDetailPath(report.id)),
                                    onUpvote: report.canUpvote ? () => _upvote(report) : null,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      );
                    },
                    loading: () => const Center(child: CircularProgressIndicator()),
                    error: (error, __) => ErrorRetryView(
                      message: '$error',
                      onRetry: () => ref.invalidate(nearbyReportsProvider),
                    ),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push(AppRoutes.createReport),
        icon: const Icon(Icons.add_a_photo_outlined),
        label: const Text('Report issue'),
      ),
    );
  }
}

/// Map showing pins for whatever's currently loaded (both the viewer's
/// own reports and others') within the visible area. Panning or zooming
/// re-queries the backend for that new area once the gesture ends --
/// this does NOT auto-follow GPS after the first load, matching "only
/// the current area, unless the user moves the map."
class _MiniMap extends StatefulWidget {
  const _MiniMap({
    required this.initialCenter,
    required this.reports,
    required this.onMarkerTap,
    required this.onViewportChanged,
  });

  final latlong.LatLng initialCenter;
  final List<Report> reports;
  final void Function(Report) onMarkerTap;
  final void Function(latlong.LatLng center, double radiusKm) onViewportChanged;

  @override
  State<_MiniMap> createState() => _MiniMapState();
}

class _MiniMapState extends State<_MiniMap> {
  final _mapController = MapController();
  static const _distance = latlong.Distance();

  @override
  void initState() {
    super.initState();
    // Only react once a pan/zoom gesture actually finishes -- avoids
    // firing a new query on every intermediate frame while dragging.
    _mapController.mapEventStream.listen((event) {
      if (event is MapEventMoveEnd || event is MapEventFlingAnimationEnd) {
        final camera = _mapController.camera;
        final bounds = camera.visibleBounds;
        final radiusKm = _distance.as(
          latlong.LengthUnit.Kilometer,
          camera.center,
          bounds.northEast,
        );
        widget.onViewportChanged(camera.center, radiusKm.clamp(0.2, 50));
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: SizedBox(
        height: 260,
        child: FlutterMap(
          mapController: _mapController,
          options: MapOptions(initialCenter: widget.initialCenter, initialZoom: 15),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.example.civic_report_app',
            ),
            MarkerLayer(
              markers: widget.reports
                  .map(
                    (r) => Marker(
                      point: latlong.LatLng(r.latitude, r.longitude),
                      width: 36,
                      height: 36,
                      child: GestureDetector(
                        onTap: () => widget.onMarkerTap(r),
                        child: Icon(
                          Icons.location_on,
                          color: r.isOwn ? Colors.blue : Colors.red,
                          size: 32,
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _ReportCard extends StatelessWidget {
  const _ReportCard({required this.report, required this.onTap, required this.onUpvote});

  final Report report;
  final VoidCallback onTap;
  final VoidCallback? onUpvote;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (report.mediaUrls.isNotEmpty)
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    AppConfig.resolveMediaUrl(report.mediaUrls.first),
                    width: 64,
                    height: 64,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => _placeholderThumb(context),
                  ),
                )
              else
                _placeholderThumb(context),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      report.description,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      children: [
                        StatusChip(status: report.status),
                        if (report.isOwn)
                          Chip(
                            label: const Text('Yours', style: TextStyle(fontSize: 11)),
                            visualDensity: VisualDensity.compact,
                            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              Column(
                children: [
                  IconButton(
                    icon: Icon(
                      Icons.arrow_upward,
                      color: report.upvotedByMe ? Theme.of(context).colorScheme.primary : null,
                    ),
                    onPressed: onUpvote,
                  ),
                  Text('${report.upvotes}'),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _placeholderThumb(BuildContext context) {
    return Container(
      width: 64,
      height: 64,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Icon(Icons.image_not_supported_outlined),
    );
  }
}
