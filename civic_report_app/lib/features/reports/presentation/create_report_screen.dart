import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart' as latlong;
import 'package:uuid/uuid.dart';

import '../../../core/background/sync_worker.dart';
import '../../../core/providers/core_providers.dart';
import '../data/camera_service.dart';
import '../data/categories_provider.dart';
import '../data/image_compression_service.dart';
import '../data/location_service.dart';
import '../data/report_sync_service.dart';

/// The highest-risk flow in the app: camera capture -> geotag -> client
/// compression -> local offline queue -> background upload with retry.
/// Submission NEVER blocks on network — everything past "Submit" happens
/// against local storage, and the actual upload is handed to
/// [ReportSyncService] (attempted immediately if online, otherwise left
/// for Workmanager).
class CreateReportScreen extends ConsumerStatefulWidget {
  const CreateReportScreen({super.key});

  @override
  ConsumerState<CreateReportScreen> createState() => _CreateReportScreenState();
}

class _CreateReportScreenState extends ConsumerState<CreateReportScreen> {
  final _cameraService = CameraService();
  final _locationService = LocationService();
  final _compressionService = ImageCompressionService();
  final _descriptionController = TextEditingController();

  CameraController? _cameraController;
  final List<File> _capturedPhotos = [];

  Position? _position;
  double? _manualLat;
  double? _manualLng;
  bool _locationLoading = false;
  bool _poorAccuracy = false;

  String? _selectedCategoryId;
  bool _isAnonymous = false;
  bool _submitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initCamera();
    _fetchLocation();
  }

  Future<void> _initCamera() async {
    try {
      final controller = await _cameraService.initialize();
      if (!mounted) return;
      setState(() => _cameraController = controller);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = 'Camera unavailable: $e');
    }
  }

  Future<void> _fetchLocation() async {
    setState(() => _locationLoading = true);
    try {
      final position = await _locationService.getCurrentLocation();
      if (!mounted) return;
      setState(() {
        _position = position;
        _poorAccuracy = _locationService.isAccuracyPoor(position);
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = 'Could not get location: $e');
    } finally {
      if (mounted) setState(() => _locationLoading = false);
    }
  }

  Future<void> _capturePhoto() async {
    try {
      final xFile = await _cameraService.capture();
      final compressed = await _compressionService.compress(xFile.path);
      HapticFeedback.lightImpact();
      setState(() => _capturedPhotos.add(compressed));
    } catch (e) {
      setState(() => _error = 'Capture failed: $e');
    }
  }

  double? get _effectiveLat => _manualLat ?? _position?.latitude;
  double? get _effectiveLng => _manualLng ?? _position?.longitude;

  Future<void> _openManualPinAdjustment() async {
    // "Choose location on map" -- defaults the picker to the current
    // GPS fix (or the map's fallback center if GPS hasn't resolved
    // yet), and lets the user tap anywhere to move the pin before
    // confirming. This is also the fallback path for poor GPS accuracy.
    final result = await showModalBottomSheet<LatLngResult>(
      context: context,
      isScrollControlled: true,
      builder: (context) => LocationPickerSheet(
        initialLat: _effectiveLat,
        initialLng: _effectiveLng,
      ),
    );
    if (result != null) {
      setState(() {
        _manualLat = result.lat;
        _manualLng = result.lng;
      });
    }
  }

  Future<void> _submit() async {
    final lat = _effectiveLat;
    final lng = _effectiveLng;
    if (lat == null || lng == null) {
      setState(() => _error = 'Location is required — wait for GPS or set a pin manually.');
      return;
    }
    if (_capturedPhotos.isEmpty) {
      setState(() => _error = 'Add at least one photo.');
      return;
    }
    final description = _descriptionController.text.trim();
    if (description.isEmpty) {
      setState(() => _error = 'Add a short description.');
      return;
    }
    // Backend requires description >= 20 chars (and derives a title from
    // it that must be >= 5 chars) -- reject early with a clear message
    // instead of letting this queue locally and fail silently in sync.
    if (description.length < 20) {
      setState(() => _error =
          'Description must be at least 20 characters (currently ${description.length}).');
      return;
    }

    setState(() {
      _submitting = true;
      _error = null;
    });

    try {
      final db = ref.read(appDatabaseProvider);
      final uuid = const Uuid().v4();

      await db.insertPendingReport(
        uuid: uuid,
        description: description,
        categoryId: _selectedCategoryId, // optional — never blocks submit
        latitude: lat,
        longitude: lng,
        manuallyAdjustedPin: _manualLat != null,
        isAnonymous: _isAnonymous,
      );
      for (var i = 0; i < _capturedPhotos.length; i++) {
        await db.addMediaToReport(uuid, _capturedPhotos[i].path, i);
      }

      if (!mounted) return;

      // Best-effort immediate attempt (fast path when online); the
      // Workmanager one-off is a fallback for offline/backgrounded/killed
      // cases only. Firing both when online raced two syncs against the
      // same pending report and produced duplicate submissions -- so
      // these are now mutually exclusive.
      final isOnline = ref.read(isOnlineProvider);
      if (isOnline) {
        // Fire and forget — UI already shows "pending sync" via the
        // My Reports stream regardless of how long this takes.
        ReportSyncService().drainQueue();
      } else {
        unawaited(BackgroundSync.scheduleOneOff());
      }

      if (!mounted) return;
      HapticFeedback.mediumImpact();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Report queued — check My Reports for sync status.')),
      );
      context.pop();
    } catch (e) {
      setState(() => _error = 'Could not queue report: $e');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  void dispose() {
    _cameraService.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final categoriesAsync = ref.watch(categoriesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Report an issue')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildCameraPreview(),
          const SizedBox(height: 8),
          if (_capturedPhotos.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: Text(
                'Tap the camera button to add at least one photo',
                style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant, fontSize: 13),
              ),
            )
          else
            _buildPhotoStrip(),
          const SizedBox(height: 16),
          _buildLocationCard(),
          const SizedBox(height: 16),
          TextField(
            controller: _descriptionController,
            maxLines: 3,
            maxLength: 280,
            decoration: const InputDecoration(
              labelText: 'What\'s wrong?',
              hintText: 'e.g. Large pothole blocking the right lane',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          categoriesAsync.when(
            data: (categories) => categories.isEmpty
                ? const SizedBox.shrink()
                : DropdownButtonFormField<String>(
                    initialValue: _selectedCategoryId,
                    decoration: const InputDecoration(labelText: 'Category (optional)', border: OutlineInputBorder()),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('None')),
                      ...categories.map((c) => DropdownMenuItem(value: c.id, child: Text(c.label))),
                    ],
                    onChanged: (v) => setState(() => _selectedCategoryId = v),
                  ),
            loading: () => const LinearProgressIndicator(),
            // Category fetch failing must never block the form — repo
            // already swallows the error and returns [], so this branch
            // is effectively unreachable, kept only for completeness.
            error: (_, __) => const SizedBox.shrink(),
          ),
          const SizedBox(height: 8),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Report anonymously'),
            subtitle: const Text('Your identity is hidden from other citizens on this report.'),
            value: _isAnonymous,
            onChanged: (v) => setState(() => _isAnonymous = v),
          ),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: _submitting ? null : _submit,
            icon: _submitting
                ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.send),
            label: const Text('Submit report'),
          ),
        ],
      ),
    );
  }

  Widget _buildCameraPreview() {
    final controller = _cameraController;
    if (controller == null || !controller.value.isInitialized) {
      return AspectRatio(
        aspectRatio: 4 / 3,
        child: Container(
          color: Colors.black12,
          child: const Center(child: CircularProgressIndicator()),
        ),
      );
    }

    // controller.value.aspectRatio is width/height as reported by the
    // sensor, which is usually landscape-oriented (e.g. 16/9) even though
    // we're displaying in portrait -- so the box itself needs the inverse
    // ratio. The old code hard-coded 4/3 and stretched CameraPreview to
    // fill it with StackFit.expand, which squished the live feed on any
    // device whose sensor isn't actually 4:3. FittedBox + BoxFit.cover
    // below preserves the real aspect ratio and crops instead of
    // stretching, matching what takePicture() actually captures.
    final previewAspectRatio = 1 / controller.value.aspectRatio;

    return AspectRatio(
      aspectRatio: previewAspectRatio,
      child: Container(
        color: Colors.black12,
        child: Stack(
          fit: StackFit.expand,
          children: [
            ClipRect(
              child: FittedBox(
                fit: BoxFit.cover,
                child: SizedBox(
                  width: controller.value.previewSize?.height ?? 1,
                  height: controller.value.previewSize?.width ?? 1,
                  child: CameraPreview(controller),
                ),
              ),
            ),
            Positioned(
              bottom: 12,
              left: 0,
              right: 0,
              child: Center(
                child: FloatingActionButton(
                  heroTag: 'capture',
                  onPressed: _capturePhoto,
                  child: const Icon(Icons.camera_alt),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPhotoStrip() {
    return SizedBox(
      height: 80,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _capturedPhotos.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final file = _capturedPhotos[index];
          return Stack(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.file(file, width: 80, height: 80, fit: BoxFit.cover),
              ),
              Positioned(
                top: 0,
                right: 0,
                child: GestureDetector(
                  onTap: () => setState(() => _capturedPhotos.removeAt(index)),
                  child: const CircleAvatar(
                    radius: 10,
                    backgroundColor: Colors.black54,
                    child: Icon(Icons.close, size: 14, color: Colors.white),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildLocationCard() {
    final lat = _effectiveLat;
    final lng = _effectiveLng;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            const Icon(Icons.location_on_outlined),
            const SizedBox(width: 8),
            Expanded(
              child: _locationLoading
                  ? const Text('Getting location…')
                  : Text(
                      lat != null && lng != null
                          ? '${lat.toStringAsFixed(5)}, ${lng.toStringAsFixed(5)}'
                              '${_manualLat != null ? " (manually adjusted)" : ""}'
                              '${_poorAccuracy && _manualLat == null ? " — low accuracy" : ""}'
                          : 'Location unavailable',
                    ),
            ),
            TextButton(
              onPressed: _openManualPinAdjustment,
              child: const Text('Choose on map'),
            ),
          ],
        ),
      ),
    );
  }
}

class LatLngResult {
  LatLngResult(this.lat, this.lng);
  final double lat;
  final double lng;
}

/// Interactive tap-to-place location picker. Opens centered on the
/// current GPS fix by default (per the "by default it would just put
/// the current location" requirement); tapping anywhere on the map
/// moves the pin. This doubles as the fallback for correcting poor GPS
/// accuracy before submitting.
class LocationPickerSheet extends StatefulWidget {
  const LocationPickerSheet({super.key, this.initialLat, this.initialLng});
  final double? initialLat;
  final double? initialLng;

  @override
  State<LocationPickerSheet> createState() => _LocationPickerSheetState();
}

class _LocationPickerSheetState extends State<LocationPickerSheet> {
  late latlong.LatLng _picked = latlong.LatLng(
    widget.initialLat ?? 0,
    widget.initialLng ?? 0,
  );

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: MediaQuery.of(context).size.height * 0.75,
      child: Column(
        children: [
          const Padding(
            padding: EdgeInsets.all(12),
            child: Text('Tap the map to place the pin', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          Expanded(
            child: Stack(
              children: [
                FlutterMap(
                  options: MapOptions(
                    initialCenter: _picked,
                    initialZoom: 16,
                    onTap: (tapPosition, point) => setState(() => _picked = point),
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.example.civic_report_app',
                    ),
                    MarkerLayer(
                      markers: [
                        Marker(
                          point: _picked,
                          width: 40,
                          height: 40,
                          child: const Icon(Icons.location_on, color: Colors.red, size: 40),
                        ),
                      ],
                    ),
                  ],
                ),
                Positioned(
                  right: 12,
                  bottom: 12,
                  child: FloatingActionButton.small(
                    heroTag: 'recenter',
                    onPressed: widget.initialLat == null
                        ? null
                        : () => setState(
                              () => _picked = latlong.LatLng(widget.initialLat!, widget.initialLng!),
                            ),
                    child: const Icon(Icons.my_location),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: EdgeInsets.only(
              left: 16, right: 16, top: 12,
              bottom: MediaQuery.of(context).viewInsets.bottom + 16,
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    '${_picked.latitude.toStringAsFixed(5)}, ${_picked.longitude.toStringAsFixed(5)}',
                  ),
                ),
                FilledButton(
                  onPressed: () => Navigator.of(context).pop(
                    LatLngResult(_picked.latitude, _picked.longitude),
                  ),
                  child: const Text('Use this location'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Small local helper so we don't need to import dart:async just for this.
void unawaited(Future<void> future) {}