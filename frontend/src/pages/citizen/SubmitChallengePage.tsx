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

const urgencyLevels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;

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
  latitude: string;
  longitude: string;
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
    latitude: "",
    longitude: "",
  });

  const [files, setFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRunningAI, setIsRunningAI] = useState(false);
  const [error, setError] = useState("");
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
  }

  function handleFiles(event: React.ChangeEvent<HTMLInputElement>) {
    if (!event.target.files) {
      return;
    }

    const selectedFiles = Array.from(event.target.files);
    setFiles((previous) => [...previous, ...selectedFiles]);
  }

  function removeFile(index: number) {
    setFiles((previous) => previous.filter((_, i) => i !== index));
  }

  function getCurrentLocation() {
    setError("");

    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setForm((previous) => ({
          ...previous,
          latitude: position.coords.latitude.toString(),
          longitude: position.coords.longitude.toString(),
        }));
      },
      () => {
        setError(
          "Unable to get your location. Please allow location access or enter it manually."
        );
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
      setError("Title must contain at least 5 characters.");
      return;
    }

    if (form.description.trim().length < 20) {
      setError("Description must contain at least 20 characters.");
      return;
    }

    try {
      setIsSubmitting(true);

      const challengePayload = {
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
        urgency: form.urgency,
        affected_population: form.affected_population
          ? Number(form.affected_population)
          : null,
        estimated_economic_loss: form.estimated_economic_loss
          ? Number(form.estimated_economic_loss)
          : null,
        address: form.address.trim() || null,
        district: form.district.trim() || null,
        state: form.state.trim() || null,
        latitude: form.latitude ? Number(form.latitude) : null,
        longitude: form.longitude ? Number(form.longitude) : null,
      };

      // 1. Persist the challenge first.
      const response = await api.post(
        "/challenges",
        challengePayload
      );

      const challengeId = response.data.id;

      // 2. Upload evidence after the challenge exists.
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);

        await api.post(
          `/challenges/${challengeId}/evidence`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
      }

      // 3. Run the real trained ML triage model.
      setIsRunningAI(true);

      let triage: TriageResult | null = null;

      try {
        triage = await runChallengeTriage({
          title: challengePayload.title,
          description: challengePayload.description,
          category: challengePayload.category,
          affected_population: challengePayload.affected_population,
          estimated_economic_loss:
            challengePayload.estimated_economic_loss,
          address: challengePayload.address,
          district: challengePayload.district,
          state: challengePayload.state,
        });
      } catch (aiError) {
        console.error("AI triage failed:", aiError);
        setError(
          "Challenge was submitted, but AI analysis could not be completed. The challenge itself was saved successfully."
        );
      } finally {
        setIsRunningAI(false);
      }

      setSuccess(true);

      window.setTimeout(() => {
        navigate(`/citizen/challenges/${challengeId}`, {
          state: {
            aiAnalysis: triage,
          },
        });
      }, 800);
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        "Unable to submit the challenge. Please try again.";

      setError(
        Array.isArray(message)
          ? message.map((item) => item.msg).join(", ")
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
          onClick={() => navigate("/citizen/dashboard")}
          disabled={isSubmitting}
        >
          <ArrowLeft size={18} />
          Back to Dashboard
        </button>

        <div className="submit-header">
          <span className="submit-eyebrow">CITIZEN PORTAL</span>

          <h1>Report a Societal Challenge</h1>

          <p>
            Describe the problem you are experiencing. Your challenge
            will be analyzed and routed to the appropriate authority,
            university, or innovation partner.
          </p>
        </div>

        {error && (
          <div className="form-alert error-alert">
            {error}
          </div>
        )}

        {success && (
          <div className="form-alert success-alert">
            {isRunningAI
              ? "Challenge submitted. Running AI analysis..."
              : "Challenge submitted successfully. Redirecting..."}
          </div>
        )}

        <form className="challenge-form" onSubmit={handleSubmit}>
          <section className="form-section">
            <div className="section-heading">
              <h2>Challenge Information</h2>
              <p>Tell us clearly what problem needs to be solved.</p>
            </div>

            <div className="form-group">
              <label htmlFor="title">Challenge Title *</label>
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
              <label htmlFor="description">Problem Description *</label>
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
                {form.description.length} characters
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="category">Category *</label>
                <select
                  id="category"
                  name="category"
                  value={form.category}
                  onChange={handleChange}
                >
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category.replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="urgency">Urgency *</label>
                <select
                  id="urgency"
                  name="urgency"
                  value={form.urgency}
                  onChange={handleChange}
                >
                  {urgencyLevels.map((urgency) => (
                    <option key={urgency} value={urgency}>
                      {urgency}
                    </option>
                  ))}
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
                  value={form.affected_population}
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
                  value={form.estimated_economic_loss}
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
                Location helps route the challenge to the correct authority.
              </p>
            </div>

            <div className="form-group">
              <label htmlFor="address">Address / Area</label>
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
                <label htmlFor="district">District</label>
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
                <label htmlFor="state">State</label>
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

            <button
              type="button"
              className="location-button"
              onClick={getCurrentLocation}
            >
              <MapPin size={18} />
              Use My Current Location
            </button>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="latitude">Latitude</label>
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
                <label htmlFor="longitude">Longitude</label>
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
                Upload photos, videos, or documents that help verify the challenge.
              </p>
            </div>

            <label htmlFor="evidence" className="upload-box">
              <Upload size={28} />
              <strong>Click to upload evidence</strong>
              <span>JPG, PNG, WEBP, MP4, WEBM, MOV or PDF</span>

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
                {files.map((file, index) => (
                  <div
                    className="selected-file"
                    key={`${file.name}-${index}`}
                  >
                    <div>
                      <strong>{file.name}</strong>
                      <span>
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      aria-label={`Remove ${file.name}`}
                    >
                      <X size={18} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          <div className="submit-actions">
            <button
              type="button"
              className="cancel-button"
              onClick={() => navigate("/citizen/dashboard")}
              disabled={isSubmitting}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="submit-button"
              disabled={isSubmitting}
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
