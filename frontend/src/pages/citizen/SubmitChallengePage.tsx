import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, MapPin, Upload, X } from "lucide-react";

import { api } from "../../services/api";
import {
  runChallengeTriage,
  type TriageResult,
} from "../../services/aiService.ts";
import "./SubmitChallengePage.css";

const categories = [
  "WATER",
  "SANITATION",
  "WASTE_MANAGEMENT",
  "HEALTHCARE",
  "EDUCATION",
  "AGRICULTURE",
  "TRANSPORTATION",
  "ENERGY",
  "ENVIRONMENT",
  "PUBLIC_SAFETY",
  "INFRASTRUCTURE",
  "DIGITAL_SERVICES",
  "EMPLOYMENT",
  "SOCIAL_WELFARE",
  "DISASTER_MANAGEMENT",
  "OTHER",
] as const;

const urgencyLevels = [
  "LOW",
  "MEDIUM",
  "HIGH",
  "CRITICAL",
] as const;

type LocationSource =
  | "MANUAL"
  | "GPS"
  | "GPS_VERIFIED_MANUAL"
  | "CONFLICT";

interface ChallengeForm {
  title: string;
  description: string;
  category: string;
  urgency: string;
  affected_population: string;
  estimated_economic_loss: string;

  address: string;
  district: string;
  state: string;
  locality: string;

  latitude: string;
  longitude: string;

  location_source: LocationSource;
  location_verified: boolean;
  location_accuracy_meters: string;
  location_resolution_reason: string;
}

interface ResolvedLocationResponse {
  latitude: number;
  longitude: number;
  accuracy_meters: number | null;

  state: string | null;
  district: string | null;
  locality: string | null;

  display_name: string | null;
  source: string;
  verified: boolean;
  reason: string;
}

function normalizeLocationValue(
  value: string | null | undefined
): string {
  return (value ?? "").trim().toLowerCase();
}

export default function SubmitChallengePage() {
  const navigate = useNavigate();

  const [form, setForm] = useState<ChallengeForm>({
    title: "",
    description: "",
    category: "OTHER",
    urgency: "MEDIUM",
    affected_population: "",
    estimated_economic_loss: "",

    address: "",
    district: "",
    state: "",
    locality: "",

    latitude: "",
    longitude: "",

    location_source: "MANUAL",
    location_verified: false,
    location_accuracy_meters: "",
    location_resolution_reason: "",
  });

  const [files, setFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRunningAI, setIsRunningAI] = useState(false);
  const [isResolvingLocation, setIsResolvingLocation] =
    useState(false);

  const [error, setError] = useState("");
  const [locationMessage, setLocationMessage] = useState("");
  const [success, setSuccess] = useState(false);

  function handleChange(
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    /*
     * If the citizen manually changes a location field after
     * GPS verification/conflict, the old verification state
     * is no longer trustworthy.
     */
    if (
      name === "state" ||
      name === "district" ||
      name === "locality"
    ) {
      setForm((previous) => ({
        ...previous,
        [name]: value,
        location_source: "MANUAL",
        location_verified: false,
        location_resolution_reason:
          "Location was edited manually by the citizen after GPS resolution.",
      }));

      setLocationMessage(
        "Location was edited manually. GPS verification has been cleared."
      );

      return;
    }

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function handleFiles(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    if (!event.target.files) {
      return;
    }

    const selectedFiles = Array.from(event.target.files);

    setFiles((previous) => [
      ...previous,
      ...selectedFiles,
    ]);
  }

  function removeFile(index: number) {
    setFiles((previous) =>
      previous.filter((_, i) => i !== index)
    );
  }

  async function getCurrentLocation() {
    setError("");
    setLocationMessage("");

    if (!navigator.geolocation) {
      setError(
        "Geolocation is not supported by your browser."
      );
      return;
    }

    setIsResolvingLocation(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const {
          latitude,
          longitude,
          accuracy,
        } = position.coords;

        try {
          const response =
            await api.post<ResolvedLocationResponse>(
              "/location/resolve-gps",
              {
                latitude,
                longitude,
                accuracy_meters: accuracy,
              }
            );

          const resolved = response.data;

          /*
           * Calculate everything from the latest form values.
           * This avoids relying on React state immediately
           * after setForm().
           */
          let calculatedSource: LocationSource = "GPS";
          let calculatedVerified = false;
          let calculatedReason = resolved.reason;
          let calculatedMessage = "";

          setForm((previous) => {
            const existingState =
              normalizeLocationValue(previous.state);

            const existingDistrict =
              normalizeLocationValue(previous.district);

            const existingLocality =
              normalizeLocationValue(previous.locality);

            const resolvedState =
              normalizeLocationValue(resolved.state);

            const resolvedDistrict =
              normalizeLocationValue(resolved.district);

            const resolvedLocality =
              normalizeLocationValue(resolved.locality);

            const hasManualState =
              Boolean(existingState);

            const hasManualDistrict =
              Boolean(existingDistrict);

            const hasManualLocality =
              Boolean(existingLocality);

            const hasManualLocation =
              hasManualState ||
              hasManualDistrict ||
              hasManualLocality;

            /*
             * A conflict only exists when:
             *
             * - citizen supplied the field manually
             * - GPS returned a value for that field
             * - the values differ
             */
            const stateConflict =
              hasManualState &&
              Boolean(resolvedState) &&
              existingState !== resolvedState;

            const districtConflict =
              hasManualDistrict &&
              Boolean(resolvedDistrict) &&
              existingDistrict !== resolvedDistrict;

            const localityConflict =
              hasManualLocality &&
              Boolean(resolvedLocality) &&
              existingLocality !== resolvedLocality;

            const hasConflict =
              stateConflict ||
              districtConflict ||
              localityConflict;

            /*
             * Manual + GPS is considered verified only when
             * every manually supplied field was successfully
             * resolved by GPS and no conflict exists.
             */
            const manualLocationVerified =
              hasManualLocation &&
              resolved.verified &&
              !hasConflict &&
              (!hasManualState ||
                Boolean(resolvedState)) &&
              (!hasManualDistrict ||
                Boolean(resolvedDistrict)) &&
              (!hasManualLocality ||
                Boolean(resolvedLocality));

            if (hasConflict) {
              calculatedSource = "CONFLICT";
              calculatedVerified = false;

              calculatedReason =
                "GPS-resolved location conflicts with the manually entered location. Citizen verification is required before routing.";

              calculatedMessage =
                "GPS detected a location that conflicts with your manually entered location. Please verify the State, District and Locality.";
            } else if (manualLocationVerified) {
              calculatedSource =
                "GPS_VERIFIED_MANUAL";

              calculatedVerified = true;

              calculatedReason =
                "GPS-resolved location matches the manually entered location.";

              calculatedMessage =
                "GPS location detected and verified against your manually entered location.";
            } else {
              calculatedSource = "GPS";
              calculatedVerified =
                resolved.verified;

              calculatedReason =
                resolved.reason;

              if (
                resolved.verified
              ) {
                if (accuracy != null) {
                  calculatedMessage =
                    `GPS location detected. Accuracy approximately ${Math.round(
                      accuracy
                    )} meters.`;
                } else {
                  calculatedMessage =
                    "GPS location detected and administrative location resolved.";
                }
              } else {
                calculatedMessage =
                  "GPS coordinates were captured, but the administrative jurisdiction could not be fully resolved. Please verify the State, District and Locality.";
              }
            }

            return {
              ...previous,

              latitude:
                String(latitude),

              longitude:
                String(longitude),

              /*
               * GPS values are used whenever available.
               * If GPS cannot resolve a field, preserve the
               * manually entered value.
               */
              state:
                resolved.state ??
                previous.state,

              district:
                resolved.district ??
                previous.district,

              locality:
                resolved.locality ??
                previous.locality,

              location_source:
                calculatedSource,

              location_verified:
                calculatedVerified,

              location_accuracy_meters:
                accuracy != null
                  ? String(accuracy)
                  : "",

              location_resolution_reason:
                calculatedReason,
            };
          });

          /*
           * These values were calculated using the latest
           * previous state inside setForm(), so the message
           * cannot suffer from stale React state.
           */
          setLocationMessage(
            calculatedMessage
          );
        } catch (locationError) {
          console.error(
            "GPS location resolution failed:",
            locationError
          );

          /*
           * GPS itself succeeded. Preserve coordinates even
           * if reverse geocoding failed.
           */
          setForm((previous) => ({
            ...previous,

            latitude:
              String(latitude),

            longitude:
              String(longitude),

            location_source:
              "GPS",

            location_verified:
              false,

            location_accuracy_meters:
              accuracy != null
                ? String(accuracy)
                : "",

            location_resolution_reason:
              "GPS coordinates were captured, but reverse geocoding failed. The citizen must verify the administrative location manually.",
          }));

          setLocationMessage(
            "GPS coordinates captured, but the administrative location could not be resolved. Please verify the State, District and Locality manually."
          );
        } finally {
          setIsResolvingLocation(false);
        }
      },
      (geoError) => {
        console.error(
          "Browser geolocation error:",
          geoError
        );

        setError(
          "Unable to get your location. Please allow location access or enter the location manually."
        );

        setIsResolvingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 30000,
      }
    );
  }

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setSuccess(false);

    if (form.title.trim().length < 5) {
      setError(
        "Title must contain at least 5 characters."
      );
      return;
    }

    if (form.description.trim().length < 20) {
      setError(
        "Description must contain at least 20 characters."
      );
      return;
    }

    /*
     * Never silently submit a known location conflict.
     */
    if (
      form.location_source ===
      "CONFLICT"
    ) {
      setError(
        "Please resolve the conflict between the manually entered location and GPS location before submitting."
      );
      return;
    }

    try {
      setIsSubmitting(true);

      const challengePayload = {
        title:
          form.title.trim(),

        description:
          form.description.trim(),

        category:
          form.category,

        urgency:
          form.urgency,

        affected_population:
          form.affected_population
            ? Number(
                form.affected_population
              )
            : null,

        estimated_economic_loss:
          form.estimated_economic_loss
            ? Number(
                form.estimated_economic_loss
              )
            : null,

        address:
          form.address.trim() ||
          null,

        district:
          form.district.trim() ||
          null,

        state:
          form.state.trim() ||
          null,

        locality:
          form.locality.trim() ||
          null,

        latitude:
          form.latitude
            ? Number(
                form.latitude
              )
            : null,

        longitude:
          form.longitude
            ? Number(
                form.longitude
              )
            : null,

        location_source:
          form.location_source,

        location_verified:
          form.location_verified,

        location_accuracy_meters:
          form.location_accuracy_meters
            ? Number(
                form.location_accuracy_meters
              )
            : null,

        location_resolution_reason:
          form.location_resolution_reason.trim() ||
          null,
      };

      // ------------------------------------------------------
      // 1. Persist the challenge first.
      // ------------------------------------------------------

      const response =
        await api.post(
          "/challenges",
          challengePayload
        );

      const challengeId =
        response.data.id;

      // ------------------------------------------------------
      // 2. Upload evidence.
      // ------------------------------------------------------

      for (const file of files) {
        const formData =
          new FormData();

        formData.append(
          "file",
          file
        );

        await api.post(
          `/challenges/${challengeId}/evidence`,
          formData,
          {
            headers: {
              "Content-Type":
                "multipart/form-data",
            },
          }
        );
      }

      // ------------------------------------------------------
      // 3. Run AI triage.
      // ------------------------------------------------------

      setIsRunningAI(true);

      let triage:
        TriageResult | null = null;

      try {
        triage =
          await runChallengeTriage({
            challenge_id:
              challengeId,

            title:
              challengePayload.title,

            description:
              challengePayload.description,

            category:
              challengePayload.category,

            affected_population:
              challengePayload.affected_population,

            estimated_economic_loss:
              challengePayload.estimated_economic_loss,

            address:
              challengePayload.address,

            district:
              challengePayload.district,

            state:
              challengePayload.state,
          });
      } catch (aiError) {
        console.error(
          "AI triage failed:",
          aiError
        );

        setError(
          "Challenge was submitted, but AI analysis could not be completed. The challenge itself was saved successfully."
        );
      } finally {
        setIsRunningAI(false);
      }

      setSuccess(true);

      window.setTimeout(() => {
        navigate(
          `/citizen/challenges/${challengeId}`,
          {
            state: {
              aiAnalysis:
                triage,
            },
          }
        );
      }, 800);
    } catch (err: any) {
      const message =
        err?.response?.data
          ?.detail ||
        "Unable to submit the challenge. Please try again.";

      setError(
        Array.isArray(message)
          ? message
              .map(
                (item) =>
                  item.msg
              )
              .join(", ")
          : message
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="submit-challenge-page">
      <div className="submit-challenge-container">
        <button
          type="button"
          className="back-button"
          onClick={() =>
            navigate(
              "/citizen/dashboard"
            )
          }
          disabled={
            isSubmitting ||
            isResolvingLocation
          }
        >
          <ArrowLeft size={18} />
          Back to Dashboard
        </button>

        <div className="submit-header">
          <span className="submit-eyebrow">
            CITIZEN PORTAL
          </span>

          <h1>
            Report a Societal Challenge
          </h1>

          <p>
            Describe the problem you are
            experiencing. Your challenge will
            be analyzed and routed to the
            appropriate authority, university,
            or innovation partner.
          </p>
        </div>

        {error && (
          <div className="form-alert error-alert">
            {error}
          </div>
        )}

        {locationMessage && (
          <div className="form-alert success-alert">
            {locationMessage}
          </div>
        )}

        {success && (
          <div className="form-alert success-alert">
            {isRunningAI
              ? "Challenge submitted. Running AI analysis..."
              : "Challenge submitted successfully. Redirecting..."}
          </div>
        )}

        <form
          className="challenge-form"
          onSubmit={handleSubmit}
        >
          <section className="form-section">
            <div className="section-heading">
              <h2>
                Challenge Information
              </h2>

              <p>
                Tell us clearly what problem
                needs to be solved.
              </p>
            </div>

            <div className="form-group">
              <label htmlFor="title">
                Challenge Title *
              </label>

              <input
                id="title"
                name="title"
                type="text"
                value={form.title}
                onChange={handleChange}
                placeholder="Example: Overflowing waste bins near community school"
                maxLength={255}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">
                Problem Description *
              </label>

              <textarea
                id="description"
                name="description"
                value={form.description}
                onChange={handleChange}
                placeholder="Explain the problem, its causes, who is affected, and what happens if it is not addressed."
                rows={7}
                required
              />

              <div className="field-hint">
                {form.description.length}{" "}
                characters
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="category">
                  Category *
                </label>

                <select
                  id="category"
                  name="category"
                  value={form.category}
                  onChange={handleChange}
                >
                  {categories.map(
                    (category) => (
                      <option
                        key={category}
                        value={category}
                      >
                        {category.replaceAll(
                          "_",
                          " "
                        )}
                      </option>
                    )
                  )}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="urgency">
                  Urgency *
                </label>

                <select
                  id="urgency"
                  name="urgency"
                  value={form.urgency}
                  onChange={handleChange}
                >
                  {urgencyLevels.map(
                    (urgency) => (
                      <option
                        key={urgency}
                        value={urgency}
                      >
                        {urgency}
                      </option>
                    )
                  )}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="affected_population">
                  Estimated People Affected
                </label>

                <input
                  id="affected_population"
                  name="affected_population"
                  type="number"
                  min="0"
                  value={
                    form.affected_population
                  }
                  onChange={handleChange}
                  placeholder="Example: 500"
                />
              </div>

              <div className="form-group">
                <label htmlFor="estimated_economic_loss">
                  Estimated Economic Loss
                </label>

                <input
                  id="estimated_economic_loss"
                  name="estimated_economic_loss"
                  type="number"
                  min="0"
                  step="0.01"
                  value={
                    form.estimated_economic_loss
                  }
                  onChange={handleChange}
                  placeholder="Example: 50000"
                />
              </div>
            </div>
          </section>

          <section className="form-section">
            <div className="section-heading">
              <h2>Location</h2>

              <p>
                Location helps route the
                challenge to the correct
                authority.
              </p>
            </div>

            <div className="form-group">
              <label htmlFor="address">
                Address / Area
              </label>

              <input
                id="address"
                name="address"
                type="text"
                value={form.address}
                onChange={handleChange}
                placeholder="Street, locality, village, ward, etc."
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="district">
                  District
                </label>

                <input
                  id="district"
                  name="district"
                  type="text"
                  value={form.district}
                  onChange={handleChange}
                  placeholder="Example: Dehradun"
                />
              </div>

              <div className="form-group">
                <label htmlFor="state">
                  State
                </label>

                <input
                  id="state"
                  name="state"
                  type="text"
                  value={form.state}
                  onChange={handleChange}
                  placeholder="Example: Uttarakhand"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="locality">
                Locality / City / Village
              </label>

              <input
                id="locality"
                name="locality"
                type="text"
                value={form.locality}
                onChange={handleChange}
                placeholder="Example: Dehradun"
              />
            </div>

            <button
              type="button"
              className="location-button"
              onClick={
                getCurrentLocation
              }
              disabled={
                isResolvingLocation ||
                isSubmitting
              }
            >
              <MapPin size={18} />

              {isResolvingLocation
                ? "Detecting Location..."
                : "Use My Current Location"}
            </button>

            {form.location_source ===
              "CONFLICT" && (
              <div className="form-alert error-alert">
                Your manually entered location
                differs from the GPS-resolved
                location. Please verify the
                State, District and Locality
                before submitting.
              </div>
            )}

            {form.location_source ===
              "GPS_VERIFIED_MANUAL" && (
              <div className="form-alert success-alert">
                GPS location matches your
                manually entered location.
                Location verified.
              </div>
            )}

            {form.location_source ===
              "GPS" &&
              form.location_accuracy_meters && (
              <div className="field-hint">
                GPS detected • Accuracy
                approximately{" "}
                {Math.round(
                  Number(
                    form.location_accuracy_meters
                  )
                )}{" "}
                meters
              </div>
            )}

            {form.location_source ===
              "GPS" &&
              !form.location_verified && (
              <div className="field-hint">
                GPS coordinates captured, but
                administrative location has not
                been fully verified.
              </div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="latitude">
                  Latitude
                </label>

                <input
                  id="latitude"
                  name="latitude"
                  type="number"
                  step="any"
                  value={form.latitude}
                  onChange={handleChange}
                  placeholder="30.3165"
                />
              </div>

              <div className="form-group">
                <label htmlFor="longitude">
                  Longitude
                </label>

                <input
                  id="longitude"
                  name="longitude"
                  type="number"
                  step="any"
                  value={form.longitude}
                  onChange={handleChange}
                  placeholder="78.0322"
                />
              </div>
            </div>
          </section>

          <section className="form-section">
            <div className="section-heading">
              <h2>Evidence</h2>

              <p>
                Upload photos, videos, or
                documents that help verify the
                challenge.
              </p>
            </div>

            <label
              htmlFor="evidence"
              className="upload-box"
            >
              <Upload size={28} />

              <strong>
                Click to upload evidence
              </strong>

              <span>
                JPG, PNG, WEBP, MP4, WEBM, MOV
                or PDF
              </span>

              <input
                id="evidence"
                type="file"
                multiple
                accept=".jpg,.jpeg,.png,.webp,.mp4,.webm,.mov,.pdf"
                onChange={handleFiles}
              />
            </label>

            {files.length > 0 && (
              <div className="selected-files">
                {files.map(
                  (file, index) => (
                    <div
                      className="selected-file"
                      key={`${file.name}-${index}`}
                    >
                      <div>
                        <strong>
                          {file.name}
                        </strong>

                        <span>
                          {(
                            file.size /
                            1024 /
                            1024
                          ).toFixed(2)}{" "}
                          MB
                        </span>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          removeFile(index)
                        }
                        aria-label={`Remove ${file.name}`}
                      >
                        <X size={18} />
                      </button>
                    </div>
                  )
                )}
              </div>
            )}
          </section>

          <div className="submit-actions">
            <button
              type="button"
              className="cancel-button"
              onClick={() =>
                navigate(
                  "/citizen/dashboard"
                )
              }
              disabled={
                isSubmitting ||
                isResolvingLocation
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              className="submit-button"
              disabled={
                isSubmitting ||
                isResolvingLocation ||
                form.location_source ===
                  "CONFLICT"
              }
            >
              {isSubmitting
                ? isRunningAI
                  ? "Analyzing..."
                  : "Submitting..."
                : "Submit Challenge"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}