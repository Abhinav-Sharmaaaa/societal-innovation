import 'package:geolocator/geolocator.dart';

/// GPS accuracy above this threshold (meters) triggers the manual pin
/// adjustment fallback in the UI rather than silently trusting a bad fix.
const double kPoorAccuracyThresholdMeters = 50;

class LocationService {
  Future<Position> getCurrentLocation() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw StateError(
        'Location services are turned off on this device. On the emulator: '
        'open the Settings app (not just Extended Controls) -> Location -> '
        'turn the toggle on.',
      );
    }

    final permission = await _ensurePermission();
    if (permission == LocationPermission.denied) {
      throw StateError(
        'Location permission was denied. Try again and tap Allow on the '
        'system prompt, or enable it manually: Settings -> Apps -> '
        'civic_report_app -> Permissions -> Location.',
      );
    }
    if (permission == LocationPermission.deniedForever) {
      throw StateError(
        'Location permission is permanently denied for this app. Enable it '
        'manually: Settings -> Apps -> civic_report_app -> Permissions -> '
        'Location -> Allow.',
      );
    }

    try {
      return await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 10),
        ),
      );
    } on LocationServiceDisabledException {
      throw StateError('Location services were turned off while waiting for a fix.');
    } catch (e) {
      // Surface whatever geolocator actually threw instead of a generic
      // wrapper -- on the emulator this is almost always either a
      // timeout (no mock location ever set/sent) or a missing
      // Google Play Services fused-location provider on the AVD image.
      throw StateError(
        'Could not get a GPS fix ($e). On the emulator, make sure you sent a '
        'location via Extended Controls -> Location -> Send, and that this '
        'AVD uses a system image with Google Play Services (not a plain '
        'AOSP image).',
      );
    }
  }

  bool isAccuracyPoor(Position position) {
    return position.accuracy > kPoorAccuracyThresholdMeters;
  }

  Future<LocationPermission> _ensurePermission() async {
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    return permission;
  }
}
