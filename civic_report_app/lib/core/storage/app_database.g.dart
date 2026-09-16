// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $PendingReportsTable extends PendingReports
    with TableInfo<$PendingReportsTable, PendingReport> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PendingReportsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
      'uuid', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _descriptionMeta =
      const VerificationMeta('description');
  @override
  late final GeneratedColumn<String> description = GeneratedColumn<String>(
      'description', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _categoryIdMeta =
      const VerificationMeta('categoryId');
  @override
  late final GeneratedColumn<String> categoryId = GeneratedColumn<String>(
      'category_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _latitudeMeta =
      const VerificationMeta('latitude');
  @override
  late final GeneratedColumn<double> latitude = GeneratedColumn<double>(
      'latitude', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _longitudeMeta =
      const VerificationMeta('longitude');
  @override
  late final GeneratedColumn<double> longitude = GeneratedColumn<double>(
      'longitude', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _manuallyAdjustedPinMeta =
      const VerificationMeta('manuallyAdjustedPin');
  @override
  late final GeneratedColumn<bool> manuallyAdjustedPin = GeneratedColumn<bool>(
      'manually_adjusted_pin', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'CHECK ("manually_adjusted_pin" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _isAnonymousMeta =
      const VerificationMeta('isAnonymous');
  @override
  late final GeneratedColumn<bool> isAnonymous = GeneratedColumn<bool>(
      'is_anonymous', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'CHECK ("is_anonymous" IN (0, 1))'),
      defaultValue: const Constant(false));
  @override
  late final GeneratedColumnWithTypeConverter<QueueStatus, int> status =
      GeneratedColumn<int>('status', aliasedName, false,
              type: DriftSqlType.int,
              requiredDuringInsert: false,
              defaultValue: const Constant(0))
          .withConverter<QueueStatus>($PendingReportsTable.$converterstatus);
  static const VerificationMeta _attemptCountMeta =
      const VerificationMeta('attemptCount');
  @override
  late final GeneratedColumn<int> attemptCount = GeneratedColumn<int>(
      'attempt_count', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _lastErrorMeta =
      const VerificationMeta('lastError');
  @override
  late final GeneratedColumn<String> lastError = GeneratedColumn<String>(
      'last_error', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        uuid,
        description,
        categoryId,
        latitude,
        longitude,
        manuallyAdjustedPin,
        isAnonymous,
        status,
        attemptCount,
        lastError,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'pending_reports';
  @override
  VerificationContext validateIntegrity(Insertable<PendingReport> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
          _uuidMeta, uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta));
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('description')) {
      context.handle(
          _descriptionMeta,
          description.isAcceptableOrUnknown(
              data['description']!, _descriptionMeta));
    } else if (isInserting) {
      context.missing(_descriptionMeta);
    }
    if (data.containsKey('category_id')) {
      context.handle(
          _categoryIdMeta,
          categoryId.isAcceptableOrUnknown(
              data['category_id']!, _categoryIdMeta));
    }
    if (data.containsKey('latitude')) {
      context.handle(_latitudeMeta,
          latitude.isAcceptableOrUnknown(data['latitude']!, _latitudeMeta));
    } else if (isInserting) {
      context.missing(_latitudeMeta);
    }
    if (data.containsKey('longitude')) {
      context.handle(_longitudeMeta,
          longitude.isAcceptableOrUnknown(data['longitude']!, _longitudeMeta));
    } else if (isInserting) {
      context.missing(_longitudeMeta);
    }
    if (data.containsKey('manually_adjusted_pin')) {
      context.handle(
          _manuallyAdjustedPinMeta,
          manuallyAdjustedPin.isAcceptableOrUnknown(
              data['manually_adjusted_pin']!, _manuallyAdjustedPinMeta));
    }
    if (data.containsKey('is_anonymous')) {
      context.handle(
          _isAnonymousMeta,
          isAnonymous.isAcceptableOrUnknown(
              data['is_anonymous']!, _isAnonymousMeta));
    }
    if (data.containsKey('attempt_count')) {
      context.handle(
          _attemptCountMeta,
          attemptCount.isAcceptableOrUnknown(
              data['attempt_count']!, _attemptCountMeta));
    }
    if (data.containsKey('last_error')) {
      context.handle(_lastErrorMeta,
          lastError.isAcceptableOrUnknown(data['last_error']!, _lastErrorMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  PendingReport map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PendingReport(
      uuid: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}uuid'])!,
      description: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}description'])!,
      categoryId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}category_id']),
      latitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}latitude'])!,
      longitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}longitude'])!,
      manuallyAdjustedPin: attachedDatabase.typeMapping.read(
          DriftSqlType.bool, data['${effectivePrefix}manually_adjusted_pin'])!,
      isAnonymous: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_anonymous'])!,
      status: $PendingReportsTable.$converterstatus.fromSql(attachedDatabase
          .typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}status'])!),
      attemptCount: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}attempt_count'])!,
      lastError: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}last_error']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $PendingReportsTable createAlias(String alias) {
    return $PendingReportsTable(attachedDatabase, alias);
  }

  static JsonTypeConverter2<QueueStatus, int, int> $converterstatus =
      const EnumIndexConverter<QueueStatus>(QueueStatus.values);
}

class PendingReport extends DataClass implements Insertable<PendingReport> {
  final String uuid;
  final String description;
  final String? categoryId;
  final double latitude;
  final double longitude;
  final bool manuallyAdjustedPin;
  final bool isAnonymous;
  final QueueStatus status;
  final int attemptCount;
  final String? lastError;
  final DateTime createdAt;
  final DateTime updatedAt;
  const PendingReport(
      {required this.uuid,
      required this.description,
      this.categoryId,
      required this.latitude,
      required this.longitude,
      required this.manuallyAdjustedPin,
      required this.isAnonymous,
      required this.status,
      required this.attemptCount,
      this.lastError,
      required this.createdAt,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['description'] = Variable<String>(description);
    if (!nullToAbsent || categoryId != null) {
      map['category_id'] = Variable<String>(categoryId);
    }
    map['latitude'] = Variable<double>(latitude);
    map['longitude'] = Variable<double>(longitude);
    map['manually_adjusted_pin'] = Variable<bool>(manuallyAdjustedPin);
    map['is_anonymous'] = Variable<bool>(isAnonymous);
    {
      map['status'] =
          Variable<int>($PendingReportsTable.$converterstatus.toSql(status));
    }
    map['attempt_count'] = Variable<int>(attemptCount);
    if (!nullToAbsent || lastError != null) {
      map['last_error'] = Variable<String>(lastError);
    }
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  PendingReportsCompanion toCompanion(bool nullToAbsent) {
    return PendingReportsCompanion(
      uuid: Value(uuid),
      description: Value(description),
      categoryId: categoryId == null && nullToAbsent
          ? const Value.absent()
          : Value(categoryId),
      latitude: Value(latitude),
      longitude: Value(longitude),
      manuallyAdjustedPin: Value(manuallyAdjustedPin),
      isAnonymous: Value(isAnonymous),
      status: Value(status),
      attemptCount: Value(attemptCount),
      lastError: lastError == null && nullToAbsent
          ? const Value.absent()
          : Value(lastError),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory PendingReport.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PendingReport(
      uuid: serializer.fromJson<String>(json['uuid']),
      description: serializer.fromJson<String>(json['description']),
      categoryId: serializer.fromJson<String?>(json['categoryId']),
      latitude: serializer.fromJson<double>(json['latitude']),
      longitude: serializer.fromJson<double>(json['longitude']),
      manuallyAdjustedPin:
          serializer.fromJson<bool>(json['manuallyAdjustedPin']),
      isAnonymous: serializer.fromJson<bool>(json['isAnonymous']),
      status: $PendingReportsTable.$converterstatus
          .fromJson(serializer.fromJson<int>(json['status'])),
      attemptCount: serializer.fromJson<int>(json['attemptCount']),
      lastError: serializer.fromJson<String?>(json['lastError']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'description': serializer.toJson<String>(description),
      'categoryId': serializer.toJson<String?>(categoryId),
      'latitude': serializer.toJson<double>(latitude),
      'longitude': serializer.toJson<double>(longitude),
      'manuallyAdjustedPin': serializer.toJson<bool>(manuallyAdjustedPin),
      'isAnonymous': serializer.toJson<bool>(isAnonymous),
      'status': serializer
          .toJson<int>($PendingReportsTable.$converterstatus.toJson(status)),
      'attemptCount': serializer.toJson<int>(attemptCount),
      'lastError': serializer.toJson<String?>(lastError),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  PendingReport copyWith(
          {String? uuid,
          String? description,
          Value<String?> categoryId = const Value.absent(),
          double? latitude,
          double? longitude,
          bool? manuallyAdjustedPin,
          bool? isAnonymous,
          QueueStatus? status,
          int? attemptCount,
          Value<String?> lastError = const Value.absent(),
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      PendingReport(
        uuid: uuid ?? this.uuid,
        description: description ?? this.description,
        categoryId: categoryId.present ? categoryId.value : this.categoryId,
        latitude: latitude ?? this.latitude,
        longitude: longitude ?? this.longitude,
        manuallyAdjustedPin: manuallyAdjustedPin ?? this.manuallyAdjustedPin,
        isAnonymous: isAnonymous ?? this.isAnonymous,
        status: status ?? this.status,
        attemptCount: attemptCount ?? this.attemptCount,
        lastError: lastError.present ? lastError.value : this.lastError,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  PendingReport copyWithCompanion(PendingReportsCompanion data) {
    return PendingReport(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      description:
          data.description.present ? data.description.value : this.description,
      categoryId:
          data.categoryId.present ? data.categoryId.value : this.categoryId,
      latitude: data.latitude.present ? data.latitude.value : this.latitude,
      longitude: data.longitude.present ? data.longitude.value : this.longitude,
      manuallyAdjustedPin: data.manuallyAdjustedPin.present
          ? data.manuallyAdjustedPin.value
          : this.manuallyAdjustedPin,
      isAnonymous:
          data.isAnonymous.present ? data.isAnonymous.value : this.isAnonymous,
      status: data.status.present ? data.status.value : this.status,
      attemptCount: data.attemptCount.present
          ? data.attemptCount.value
          : this.attemptCount,
      lastError: data.lastError.present ? data.lastError.value : this.lastError,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PendingReport(')
          ..write('uuid: $uuid, ')
          ..write('description: $description, ')
          ..write('categoryId: $categoryId, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('manuallyAdjustedPin: $manuallyAdjustedPin, ')
          ..write('isAnonymous: $isAnonymous, ')
          ..write('status: $status, ')
          ..write('attemptCount: $attemptCount, ')
          ..write('lastError: $lastError, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      uuid,
      description,
      categoryId,
      latitude,
      longitude,
      manuallyAdjustedPin,
      isAnonymous,
      status,
      attemptCount,
      lastError,
      createdAt,
      updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PendingReport &&
          other.uuid == this.uuid &&
          other.description == this.description &&
          other.categoryId == this.categoryId &&
          other.latitude == this.latitude &&
          other.longitude == this.longitude &&
          other.manuallyAdjustedPin == this.manuallyAdjustedPin &&
          other.isAnonymous == this.isAnonymous &&
          other.status == this.status &&
          other.attemptCount == this.attemptCount &&
          other.lastError == this.lastError &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class PendingReportsCompanion extends UpdateCompanion<PendingReport> {
  final Value<String> uuid;
  final Value<String> description;
  final Value<String?> categoryId;
  final Value<double> latitude;
  final Value<double> longitude;
  final Value<bool> manuallyAdjustedPin;
  final Value<bool> isAnonymous;
  final Value<QueueStatus> status;
  final Value<int> attemptCount;
  final Value<String?> lastError;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const PendingReportsCompanion({
    this.uuid = const Value.absent(),
    this.description = const Value.absent(),
    this.categoryId = const Value.absent(),
    this.latitude = const Value.absent(),
    this.longitude = const Value.absent(),
    this.manuallyAdjustedPin = const Value.absent(),
    this.isAnonymous = const Value.absent(),
    this.status = const Value.absent(),
    this.attemptCount = const Value.absent(),
    this.lastError = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PendingReportsCompanion.insert({
    required String uuid,
    required String description,
    this.categoryId = const Value.absent(),
    required double latitude,
    required double longitude,
    this.manuallyAdjustedPin = const Value.absent(),
    this.isAnonymous = const Value.absent(),
    this.status = const Value.absent(),
    this.attemptCount = const Value.absent(),
    this.lastError = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : uuid = Value(uuid),
        description = Value(description),
        latitude = Value(latitude),
        longitude = Value(longitude);
  static Insertable<PendingReport> custom({
    Expression<String>? uuid,
    Expression<String>? description,
    Expression<String>? categoryId,
    Expression<double>? latitude,
    Expression<double>? longitude,
    Expression<bool>? manuallyAdjustedPin,
    Expression<bool>? isAnonymous,
    Expression<int>? status,
    Expression<int>? attemptCount,
    Expression<String>? lastError,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (description != null) 'description': description,
      if (categoryId != null) 'category_id': categoryId,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      if (manuallyAdjustedPin != null)
        'manually_adjusted_pin': manuallyAdjustedPin,
      if (isAnonymous != null) 'is_anonymous': isAnonymous,
      if (status != null) 'status': status,
      if (attemptCount != null) 'attempt_count': attemptCount,
      if (lastError != null) 'last_error': lastError,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PendingReportsCompanion copyWith(
      {Value<String>? uuid,
      Value<String>? description,
      Value<String?>? categoryId,
      Value<double>? latitude,
      Value<double>? longitude,
      Value<bool>? manuallyAdjustedPin,
      Value<bool>? isAnonymous,
      Value<QueueStatus>? status,
      Value<int>? attemptCount,
      Value<String?>? lastError,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return PendingReportsCompanion(
      uuid: uuid ?? this.uuid,
      description: description ?? this.description,
      categoryId: categoryId ?? this.categoryId,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      manuallyAdjustedPin: manuallyAdjustedPin ?? this.manuallyAdjustedPin,
      isAnonymous: isAnonymous ?? this.isAnonymous,
      status: status ?? this.status,
      attemptCount: attemptCount ?? this.attemptCount,
      lastError: lastError ?? this.lastError,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (description.present) {
      map['description'] = Variable<String>(description.value);
    }
    if (categoryId.present) {
      map['category_id'] = Variable<String>(categoryId.value);
    }
    if (latitude.present) {
      map['latitude'] = Variable<double>(latitude.value);
    }
    if (longitude.present) {
      map['longitude'] = Variable<double>(longitude.value);
    }
    if (manuallyAdjustedPin.present) {
      map['manually_adjusted_pin'] = Variable<bool>(manuallyAdjustedPin.value);
    }
    if (isAnonymous.present) {
      map['is_anonymous'] = Variable<bool>(isAnonymous.value);
    }
    if (status.present) {
      map['status'] = Variable<int>(
          $PendingReportsTable.$converterstatus.toSql(status.value));
    }
    if (attemptCount.present) {
      map['attempt_count'] = Variable<int>(attemptCount.value);
    }
    if (lastError.present) {
      map['last_error'] = Variable<String>(lastError.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PendingReportsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('description: $description, ')
          ..write('categoryId: $categoryId, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('manuallyAdjustedPin: $manuallyAdjustedPin, ')
          ..write('isAnonymous: $isAnonymous, ')
          ..write('status: $status, ')
          ..write('attemptCount: $attemptCount, ')
          ..write('lastError: $lastError, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PendingReportMediaTable extends PendingReportMedia
    with TableInfo<$PendingReportMediaTable, PendingReportMediaData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PendingReportMediaTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _pendingReportUuidMeta =
      const VerificationMeta('pendingReportUuid');
  @override
  late final GeneratedColumn<String> pendingReportUuid =
      GeneratedColumn<String>('pending_report_uuid', aliasedName, false,
          type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _localFilePathMeta =
      const VerificationMeta('localFilePath');
  @override
  late final GeneratedColumn<String> localFilePath = GeneratedColumn<String>(
      'local_file_path', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _remoteMediaIdMeta =
      const VerificationMeta('remoteMediaId');
  @override
  late final GeneratedColumn<String> remoteMediaId = GeneratedColumn<String>(
      'remote_media_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _sortOrderMeta =
      const VerificationMeta('sortOrder');
  @override
  late final GeneratedColumn<int> sortOrder = GeneratedColumn<int>(
      'sort_order', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  @override
  List<GeneratedColumn> get $columns =>
      [id, pendingReportUuid, localFilePath, remoteMediaId, sortOrder];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'pending_report_media';
  @override
  VerificationContext validateIntegrity(
      Insertable<PendingReportMediaData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('pending_report_uuid')) {
      context.handle(
          _pendingReportUuidMeta,
          pendingReportUuid.isAcceptableOrUnknown(
              data['pending_report_uuid']!, _pendingReportUuidMeta));
    } else if (isInserting) {
      context.missing(_pendingReportUuidMeta);
    }
    if (data.containsKey('local_file_path')) {
      context.handle(
          _localFilePathMeta,
          localFilePath.isAcceptableOrUnknown(
              data['local_file_path']!, _localFilePathMeta));
    } else if (isInserting) {
      context.missing(_localFilePathMeta);
    }
    if (data.containsKey('remote_media_id')) {
      context.handle(
          _remoteMediaIdMeta,
          remoteMediaId.isAcceptableOrUnknown(
              data['remote_media_id']!, _remoteMediaIdMeta));
    }
    if (data.containsKey('sort_order')) {
      context.handle(_sortOrderMeta,
          sortOrder.isAcceptableOrUnknown(data['sort_order']!, _sortOrderMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  PendingReportMediaData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PendingReportMediaData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      pendingReportUuid: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}pending_report_uuid'])!,
      localFilePath: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}local_file_path'])!,
      remoteMediaId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}remote_media_id']),
      sortOrder: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}sort_order'])!,
    );
  }

  @override
  $PendingReportMediaTable createAlias(String alias) {
    return $PendingReportMediaTable(attachedDatabase, alias);
  }
}

class PendingReportMediaData extends DataClass
    implements Insertable<PendingReportMediaData> {
  final int id;
  final String pendingReportUuid;
  final String localFilePath;
  final String? remoteMediaId;
  final int sortOrder;
  const PendingReportMediaData(
      {required this.id,
      required this.pendingReportUuid,
      required this.localFilePath,
      this.remoteMediaId,
      required this.sortOrder});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['pending_report_uuid'] = Variable<String>(pendingReportUuid);
    map['local_file_path'] = Variable<String>(localFilePath);
    if (!nullToAbsent || remoteMediaId != null) {
      map['remote_media_id'] = Variable<String>(remoteMediaId);
    }
    map['sort_order'] = Variable<int>(sortOrder);
    return map;
  }

  PendingReportMediaCompanion toCompanion(bool nullToAbsent) {
    return PendingReportMediaCompanion(
      id: Value(id),
      pendingReportUuid: Value(pendingReportUuid),
      localFilePath: Value(localFilePath),
      remoteMediaId: remoteMediaId == null && nullToAbsent
          ? const Value.absent()
          : Value(remoteMediaId),
      sortOrder: Value(sortOrder),
    );
  }

  factory PendingReportMediaData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PendingReportMediaData(
      id: serializer.fromJson<int>(json['id']),
      pendingReportUuid: serializer.fromJson<String>(json['pendingReportUuid']),
      localFilePath: serializer.fromJson<String>(json['localFilePath']),
      remoteMediaId: serializer.fromJson<String?>(json['remoteMediaId']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'pendingReportUuid': serializer.toJson<String>(pendingReportUuid),
      'localFilePath': serializer.toJson<String>(localFilePath),
      'remoteMediaId': serializer.toJson<String?>(remoteMediaId),
      'sortOrder': serializer.toJson<int>(sortOrder),
    };
  }

  PendingReportMediaData copyWith(
          {int? id,
          String? pendingReportUuid,
          String? localFilePath,
          Value<String?> remoteMediaId = const Value.absent(),
          int? sortOrder}) =>
      PendingReportMediaData(
        id: id ?? this.id,
        pendingReportUuid: pendingReportUuid ?? this.pendingReportUuid,
        localFilePath: localFilePath ?? this.localFilePath,
        remoteMediaId:
            remoteMediaId.present ? remoteMediaId.value : this.remoteMediaId,
        sortOrder: sortOrder ?? this.sortOrder,
      );
  PendingReportMediaData copyWithCompanion(PendingReportMediaCompanion data) {
    return PendingReportMediaData(
      id: data.id.present ? data.id.value : this.id,
      pendingReportUuid: data.pendingReportUuid.present
          ? data.pendingReportUuid.value
          : this.pendingReportUuid,
      localFilePath: data.localFilePath.present
          ? data.localFilePath.value
          : this.localFilePath,
      remoteMediaId: data.remoteMediaId.present
          ? data.remoteMediaId.value
          : this.remoteMediaId,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PendingReportMediaData(')
          ..write('id: $id, ')
          ..write('pendingReportUuid: $pendingReportUuid, ')
          ..write('localFilePath: $localFilePath, ')
          ..write('remoteMediaId: $remoteMediaId, ')
          ..write('sortOrder: $sortOrder')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id, pendingReportUuid, localFilePath, remoteMediaId, sortOrder);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PendingReportMediaData &&
          other.id == this.id &&
          other.pendingReportUuid == this.pendingReportUuid &&
          other.localFilePath == this.localFilePath &&
          other.remoteMediaId == this.remoteMediaId &&
          other.sortOrder == this.sortOrder);
}

class PendingReportMediaCompanion
    extends UpdateCompanion<PendingReportMediaData> {
  final Value<int> id;
  final Value<String> pendingReportUuid;
  final Value<String> localFilePath;
  final Value<String?> remoteMediaId;
  final Value<int> sortOrder;
  const PendingReportMediaCompanion({
    this.id = const Value.absent(),
    this.pendingReportUuid = const Value.absent(),
    this.localFilePath = const Value.absent(),
    this.remoteMediaId = const Value.absent(),
    this.sortOrder = const Value.absent(),
  });
  PendingReportMediaCompanion.insert({
    this.id = const Value.absent(),
    required String pendingReportUuid,
    required String localFilePath,
    this.remoteMediaId = const Value.absent(),
    this.sortOrder = const Value.absent(),
  })  : pendingReportUuid = Value(pendingReportUuid),
        localFilePath = Value(localFilePath);
  static Insertable<PendingReportMediaData> custom({
    Expression<int>? id,
    Expression<String>? pendingReportUuid,
    Expression<String>? localFilePath,
    Expression<String>? remoteMediaId,
    Expression<int>? sortOrder,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (pendingReportUuid != null) 'pending_report_uuid': pendingReportUuid,
      if (localFilePath != null) 'local_file_path': localFilePath,
      if (remoteMediaId != null) 'remote_media_id': remoteMediaId,
      if (sortOrder != null) 'sort_order': sortOrder,
    });
  }

  PendingReportMediaCompanion copyWith(
      {Value<int>? id,
      Value<String>? pendingReportUuid,
      Value<String>? localFilePath,
      Value<String?>? remoteMediaId,
      Value<int>? sortOrder}) {
    return PendingReportMediaCompanion(
      id: id ?? this.id,
      pendingReportUuid: pendingReportUuid ?? this.pendingReportUuid,
      localFilePath: localFilePath ?? this.localFilePath,
      remoteMediaId: remoteMediaId ?? this.remoteMediaId,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (pendingReportUuid.present) {
      map['pending_report_uuid'] = Variable<String>(pendingReportUuid.value);
    }
    if (localFilePath.present) {
      map['local_file_path'] = Variable<String>(localFilePath.value);
    }
    if (remoteMediaId.present) {
      map['remote_media_id'] = Variable<String>(remoteMediaId.value);
    }
    if (sortOrder.present) {
      map['sort_order'] = Variable<int>(sortOrder.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PendingReportMediaCompanion(')
          ..write('id: $id, ')
          ..write('pendingReportUuid: $pendingReportUuid, ')
          ..write('localFilePath: $localFilePath, ')
          ..write('remoteMediaId: $remoteMediaId, ')
          ..write('sortOrder: $sortOrder')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $PendingReportsTable pendingReports = $PendingReportsTable(this);
  late final $PendingReportMediaTable pendingReportMedia =
      $PendingReportMediaTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities =>
      [pendingReports, pendingReportMedia];
}

typedef $$PendingReportsTableCreateCompanionBuilder = PendingReportsCompanion
    Function({
  required String uuid,
  required String description,
  Value<String?> categoryId,
  required double latitude,
  required double longitude,
  Value<bool> manuallyAdjustedPin,
  Value<bool> isAnonymous,
  Value<QueueStatus> status,
  Value<int> attemptCount,
  Value<String?> lastError,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$PendingReportsTableUpdateCompanionBuilder = PendingReportsCompanion
    Function({
  Value<String> uuid,
  Value<String> description,
  Value<String?> categoryId,
  Value<double> latitude,
  Value<double> longitude,
  Value<bool> manuallyAdjustedPin,
  Value<bool> isAnonymous,
  Value<QueueStatus> status,
  Value<int> attemptCount,
  Value<String?> lastError,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

class $$PendingReportsTableFilterComposer
    extends Composer<_$AppDatabase, $PendingReportsTable> {
  $$PendingReportsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
      column: $table.uuid, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get categoryId => $composableBuilder(
      column: $table.categoryId, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get manuallyAdjustedPin => $composableBuilder(
      column: $table.manuallyAdjustedPin,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isAnonymous => $composableBuilder(
      column: $table.isAnonymous, builder: (column) => ColumnFilters(column));

  ColumnWithTypeConverterFilters<QueueStatus, QueueStatus, int> get status =>
      $composableBuilder(
          column: $table.status,
          builder: (column) => ColumnWithTypeConverterFilters(column));

  ColumnFilters<int> get attemptCount => $composableBuilder(
      column: $table.attemptCount, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get lastError => $composableBuilder(
      column: $table.lastError, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));
}

class $$PendingReportsTableOrderingComposer
    extends Composer<_$AppDatabase, $PendingReportsTable> {
  $$PendingReportsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
      column: $table.uuid, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get categoryId => $composableBuilder(
      column: $table.categoryId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get manuallyAdjustedPin => $composableBuilder(
      column: $table.manuallyAdjustedPin,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isAnonymous => $composableBuilder(
      column: $table.isAnonymous, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get attemptCount => $composableBuilder(
      column: $table.attemptCount,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get lastError => $composableBuilder(
      column: $table.lastError, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));
}

class $$PendingReportsTableAnnotationComposer
    extends Composer<_$AppDatabase, $PendingReportsTable> {
  $$PendingReportsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => column);

  GeneratedColumn<String> get categoryId => $composableBuilder(
      column: $table.categoryId, builder: (column) => column);

  GeneratedColumn<double> get latitude =>
      $composableBuilder(column: $table.latitude, builder: (column) => column);

  GeneratedColumn<double> get longitude =>
      $composableBuilder(column: $table.longitude, builder: (column) => column);

  GeneratedColumn<bool> get manuallyAdjustedPin => $composableBuilder(
      column: $table.manuallyAdjustedPin, builder: (column) => column);

  GeneratedColumn<bool> get isAnonymous => $composableBuilder(
      column: $table.isAnonymous, builder: (column) => column);

  GeneratedColumnWithTypeConverter<QueueStatus, int> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<int> get attemptCount => $composableBuilder(
      column: $table.attemptCount, builder: (column) => column);

  GeneratedColumn<String> get lastError =>
      $composableBuilder(column: $table.lastError, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);
}

class $$PendingReportsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $PendingReportsTable,
    PendingReport,
    $$PendingReportsTableFilterComposer,
    $$PendingReportsTableOrderingComposer,
    $$PendingReportsTableAnnotationComposer,
    $$PendingReportsTableCreateCompanionBuilder,
    $$PendingReportsTableUpdateCompanionBuilder,
    (
      PendingReport,
      BaseReferences<_$AppDatabase, $PendingReportsTable, PendingReport>
    ),
    PendingReport,
    PrefetchHooks Function()> {
  $$PendingReportsTableTableManager(
      _$AppDatabase db, $PendingReportsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PendingReportsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PendingReportsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PendingReportsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> uuid = const Value.absent(),
            Value<String> description = const Value.absent(),
            Value<String?> categoryId = const Value.absent(),
            Value<double> latitude = const Value.absent(),
            Value<double> longitude = const Value.absent(),
            Value<bool> manuallyAdjustedPin = const Value.absent(),
            Value<bool> isAnonymous = const Value.absent(),
            Value<QueueStatus> status = const Value.absent(),
            Value<int> attemptCount = const Value.absent(),
            Value<String?> lastError = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              PendingReportsCompanion(
            uuid: uuid,
            description: description,
            categoryId: categoryId,
            latitude: latitude,
            longitude: longitude,
            manuallyAdjustedPin: manuallyAdjustedPin,
            isAnonymous: isAnonymous,
            status: status,
            attemptCount: attemptCount,
            lastError: lastError,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String uuid,
            required String description,
            Value<String?> categoryId = const Value.absent(),
            required double latitude,
            required double longitude,
            Value<bool> manuallyAdjustedPin = const Value.absent(),
            Value<bool> isAnonymous = const Value.absent(),
            Value<QueueStatus> status = const Value.absent(),
            Value<int> attemptCount = const Value.absent(),
            Value<String?> lastError = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              PendingReportsCompanion.insert(
            uuid: uuid,
            description: description,
            categoryId: categoryId,
            latitude: latitude,
            longitude: longitude,
            manuallyAdjustedPin: manuallyAdjustedPin,
            isAnonymous: isAnonymous,
            status: status,
            attemptCount: attemptCount,
            lastError: lastError,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable<$PendingReportsTable, PendingReport>(table),
                    BaseReferences<_$AppDatabase, $PendingReportsTable,
                        PendingReport>(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$PendingReportsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $PendingReportsTable,
    PendingReport,
    $$PendingReportsTableFilterComposer,
    $$PendingReportsTableOrderingComposer,
    $$PendingReportsTableAnnotationComposer,
    $$PendingReportsTableCreateCompanionBuilder,
    $$PendingReportsTableUpdateCompanionBuilder,
    (
      PendingReport,
      BaseReferences<_$AppDatabase, $PendingReportsTable, PendingReport>
    ),
    PendingReport,
    PrefetchHooks Function()>;
typedef $$PendingReportMediaTableCreateCompanionBuilder
    = PendingReportMediaCompanion Function({
  Value<int> id,
  required String pendingReportUuid,
  required String localFilePath,
  Value<String?> remoteMediaId,
  Value<int> sortOrder,
});
typedef $$PendingReportMediaTableUpdateCompanionBuilder
    = PendingReportMediaCompanion Function({
  Value<int> id,
  Value<String> pendingReportUuid,
  Value<String> localFilePath,
  Value<String?> remoteMediaId,
  Value<int> sortOrder,
});

class $$PendingReportMediaTableFilterComposer
    extends Composer<_$AppDatabase, $PendingReportMediaTable> {
  $$PendingReportMediaTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get pendingReportUuid => $composableBuilder(
      column: $table.pendingReportUuid,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get localFilePath => $composableBuilder(
      column: $table.localFilePath, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get remoteMediaId => $composableBuilder(
      column: $table.remoteMediaId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get sortOrder => $composableBuilder(
      column: $table.sortOrder, builder: (column) => ColumnFilters(column));
}

class $$PendingReportMediaTableOrderingComposer
    extends Composer<_$AppDatabase, $PendingReportMediaTable> {
  $$PendingReportMediaTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get pendingReportUuid => $composableBuilder(
      column: $table.pendingReportUuid,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get localFilePath => $composableBuilder(
      column: $table.localFilePath,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get remoteMediaId => $composableBuilder(
      column: $table.remoteMediaId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get sortOrder => $composableBuilder(
      column: $table.sortOrder, builder: (column) => ColumnOrderings(column));
}

class $$PendingReportMediaTableAnnotationComposer
    extends Composer<_$AppDatabase, $PendingReportMediaTable> {
  $$PendingReportMediaTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get pendingReportUuid => $composableBuilder(
      column: $table.pendingReportUuid, builder: (column) => column);

  GeneratedColumn<String> get localFilePath => $composableBuilder(
      column: $table.localFilePath, builder: (column) => column);

  GeneratedColumn<String> get remoteMediaId => $composableBuilder(
      column: $table.remoteMediaId, builder: (column) => column);

  GeneratedColumn<int> get sortOrder =>
      $composableBuilder(column: $table.sortOrder, builder: (column) => column);
}

class $$PendingReportMediaTableTableManager extends RootTableManager<
    _$AppDatabase,
    $PendingReportMediaTable,
    PendingReportMediaData,
    $$PendingReportMediaTableFilterComposer,
    $$PendingReportMediaTableOrderingComposer,
    $$PendingReportMediaTableAnnotationComposer,
    $$PendingReportMediaTableCreateCompanionBuilder,
    $$PendingReportMediaTableUpdateCompanionBuilder,
    (
      PendingReportMediaData,
      BaseReferences<_$AppDatabase, $PendingReportMediaTable,
          PendingReportMediaData>
    ),
    PendingReportMediaData,
    PrefetchHooks Function()> {
  $$PendingReportMediaTableTableManager(
      _$AppDatabase db, $PendingReportMediaTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PendingReportMediaTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PendingReportMediaTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PendingReportMediaTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> pendingReportUuid = const Value.absent(),
            Value<String> localFilePath = const Value.absent(),
            Value<String?> remoteMediaId = const Value.absent(),
            Value<int> sortOrder = const Value.absent(),
          }) =>
              PendingReportMediaCompanion(
            id: id,
            pendingReportUuid: pendingReportUuid,
            localFilePath: localFilePath,
            remoteMediaId: remoteMediaId,
            sortOrder: sortOrder,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String pendingReportUuid,
            required String localFilePath,
            Value<String?> remoteMediaId = const Value.absent(),
            Value<int> sortOrder = const Value.absent(),
          }) =>
              PendingReportMediaCompanion.insert(
            id: id,
            pendingReportUuid: pendingReportUuid,
            localFilePath: localFilePath,
            remoteMediaId: remoteMediaId,
            sortOrder: sortOrder,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable<$PendingReportMediaTable,
                        PendingReportMediaData>(table),
                    BaseReferences<_$AppDatabase, $PendingReportMediaTable,
                        PendingReportMediaData>(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$PendingReportMediaTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $PendingReportMediaTable,
    PendingReportMediaData,
    $$PendingReportMediaTableFilterComposer,
    $$PendingReportMediaTableOrderingComposer,
    $$PendingReportMediaTableAnnotationComposer,
    $$PendingReportMediaTableCreateCompanionBuilder,
    $$PendingReportMediaTableUpdateCompanionBuilder,
    (
      PendingReportMediaData,
      BaseReferences<_$AppDatabase, $PendingReportMediaTable,
          PendingReportMediaData>
    ),
    PendingReportMediaData,
    PrefetchHooks Function()>;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$PendingReportsTableTableManager get pendingReports =>
      $$PendingReportsTableTableManager(_db, _db.pendingReports);
  $$PendingReportMediaTableTableManager get pendingReportMedia =>
      $$PendingReportMediaTableTableManager(_db, _db.pendingReportMedia);
}
