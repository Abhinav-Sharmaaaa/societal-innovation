import 'dart:io';

import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import '../../../core/config/app_config.dart';

/// Compresses a freshly captured photo before it ever touches local
/// queue storage or the network, per the bandwidth/storage requirement.
class ImageCompressionService {
  Future<File> compress(String sourcePath) async {
    final dir = await getApplicationDocumentsDirectory();
    final targetPath = p.join(
      dir.path,
      'report_media',
      '${DateTime.now().microsecondsSinceEpoch}.jpg',
    );
    await Directory(p.dirname(targetPath)).create(recursive: true);

    final result = await FlutterImageCompress.compressAndGetFile(
      sourcePath,
      targetPath,
      minWidth: AppConfig.imageMaxWidth,
      minHeight: AppConfig.imageMaxHeight,
      quality: AppConfig.imageQuality,
      keepExif: true, // preserve geotag/EXIF for backend fraud checks
    );

    if (result == null) {
      // Fall back to the original if compression fails for any reason —
      // never block report submission on this step.
      final fallback = File(targetPath);
      await File(sourcePath).copy(fallback.path);
      return fallback;
    }
    return File(result.path);
  }
}
