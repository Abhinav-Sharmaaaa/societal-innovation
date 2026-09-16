# Civic Report App — Flutter Client

## What's here

Feature-based scaffold + a fully wired **Create Report** flow (the
highest-risk piece), per the session brief.

```
lib/
  core/
    background/sync_worker.dart      # Workmanager entrypoint + scheduling
    config/app_config.dart           # base URL, timeouts, compression targets
    network/dio_client.dart          # auth interceptor + 401 refresh-and-retry
    network/token_storage.dart       # flutter_secure_storage wrapper
    providers/core_providers.dart    # riverpod DI: dio, db, connectivity
    router/app_router.dart           # go_router routes for all 8 screens
    router/app_shell.dart            # bottom-nav shell
    storage/app_database.dart        # drift schema: offline report queue
  features/
    auth/presentation/               # splash (session check), login
    reports/
      data/
        camera_service.dart          # in-app capture only, no gallery path
        location_service.dart        # geolocation + poor-accuracy check
        image_compression_service.dart
        categories_provider.dart     # GET /categories, optional/non-blocking
        reports_repository.dart      # POST /media/upload, POST /reports
        report_sync_service.dart     # drains offline queue, retry/backoff
      presentation/
        home_feed_screen.dart
        create_report_screen.dart    # camera -> geotag -> compress -> queue
        report_detail_screen.dart
        my_reports_screen.dart       # streams local queue, shows pending sync
    rewards/, profile/, notifications/presentation/   # placeholders
```

## Setup

1. `flutter pub get`
2. Generate Drift code: `dart run build_runner build --delete-conflicting-outputs`
3. Run with your dev backend URL:
   `flutter run --dart-define=API_BASE_URL=https://your-dev-api.example.com`
4. Android: Workmanager and camera need no extra native setup beyond
   what `flutter pub get` wires in, but you'll need to add camera/location
   permissions to `AndroidManifest.xml` / `Info.plist` (not generated here
   since this session only covers the Dart side — happy to add the native
   permission blocks next if useful).
5. Firebase (push notifications) is stubbed out — run `flutterfire configure`
   to generate `firebase_options.dart`, then uncomment the init call in
   `main.dart`.

## How the Create Report flow works end-to-end

1. **Capture** — `CameraService` opens a live camera session; there is no
   gallery-picker code path anywhere in this feature, per the
   anti-fraud requirement.
2. **Geotag** — `LocationService` fetches a fix and flags accuracy above
   50m as "poor," surfacing the **Adjust pin** fallback in the UI.
3. **Compress** — `ImageCompressionService` shrinks the photo
   (`flutter_image_compress`) before it ever touches disk-backed queue
   storage, keeping EXIF (and therefore the geotag) intact.
4. **Queue** — On Submit, a `PendingReports` + `PendingReportMedia` row
   is written to Drift immediately. This never touches the network and
   cannot fail due to connectivity — the UI's "queued" confirmation is
   always honest.
5. **Upload** — `ReportSyncService.drainQueue()` is called two ways:
   - immediately, best-effort, if the device is online (fast path), and
   - via a Workmanager one-off task with a `networkType: connected`
     constraint, so it fires as soon as the OS says connectivity is back
     even if the app is killed or backgrounded.
   A periodic 15-minute Workmanager task is also registered in `main.dart`
   as a safety net in case a one-off is dropped.
6. **Retry** — Each attempt increments `attemptCount`; failures are left
   as `failed` with the error message stored, capped at 5 attempts. A
   single bad report never blocks the rest of the queue.
7. **Visibility** — `My Reports` streams the Drift table directly, so
   "pending sync" / "uploading photos" / "submitting" / "failed, will
   retry" is always accurate, even fully offline.

## Assumptions flagged (please confirm/correct against the real API)

- **`POST /auth/refresh`** body is `{ "refresh_token": "..." }` returning
  `{ "access_token": "...", "refresh_token": "..." }`. If refresh is
  cookie-based instead, `DioClient._doRefresh()` needs rework.
- **`POST /media/upload`** is multipart with field name `file`, returning
  `{ "media_id": "..." }`. If it's actually a presigned-URL flow
  (request URL → PUT file → confirm), `ReportsRepository.uploadMedia`
  is the only place that needs to change — the queue/retry logic above
  it is agnostic to which upload strategy is used.
- **`POST /reports`** body shape: `description`, `category_id` (nullable),
  `latitude`, `longitude`, `is_anonymous`, `media_ids: []` → returns
  `{ "id": "..." }`.
- **`GET /categories`** returns a flat array of `{ "id", "label" }`.
  Any failure here degrades to an empty list rather than blocking
  report creation, matching "category is optional, never blocks submit."
- **Maps provider**: `flutter_map` (OpenStreetMap) was wired as the
  default since no Maps API key was specified; swap for
  `google_maps_flutter` by changing the map widget in the manual-pin
  sheet and the (not-yet-built) map view on Home if you have a key.
- **Manual pin adjustment** is currently a numeric lat/lng entry sheet,
  not yet an actual draggable-pin map widget — flagged in code as a
  placeholder to keep the end-to-end flow demonstrable without pulling
  in the full map dependency for this pass.
- **Login** uses email+password against `/auth/login` for now; the spec
  mentioned phone OTP as an alternative — swapping the form for a
  two-step phone→OTP flow wouldn't change anything below the token
  storage layer.
- **Push notifications**: `firebase_messaging` is a dependency but
  Firebase itself isn't initialized (needs a real project via
  `flutterfire configure`), so `main.dart` has that call commented out.

## Not yet built (next steps, in priority order)

1. Home feed wired to `GET /reports` (list + map view, filters, upvote).
2. Report detail wired to `GET /reports/{id}` with the status timeline.
3. Rewards catalog/redeem wired to `GET /rewards/catalog` /
   `POST /rewards/redeem`.
4. Real draggable-pin map for both Create Report and Home.
5. FCM foreground/background handlers + tap-through routing.
6. Android/iOS native permission manifest entries (camera, location,
   background execution) — no packages listed required me to add a
   package you hadn't approved, but the manifest edits themselves
   weren't generated in this pass.

No packages outside the ones you listed were added — every dependency in
`pubspec.yaml` maps to something the spec named directly.
