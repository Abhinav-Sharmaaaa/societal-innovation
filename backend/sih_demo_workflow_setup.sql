-- SIH demo setup for authority hierarchy, override testing, and CH-8 innovation flow.
-- Run against the societal_innovation PostgreSQL database.
-- Safe to re-run: organization + competency inserts are duplicate-safe.

BEGIN;

-- 1) Establish the real hierarchy: Municipality #1 is below District Authority #2.
UPDATE organizations
SET parent_organization_id = 2
WHERE id = 1;

-- 2) Add a second waste-management government authority in Dehradun.
-- This gives the Review Officer a genuinely different authority to select for Override.
INSERT INTO organizations (
    name,
    organization_type,
    description,
    district,
    state,
    email,
    phone,
    website,
    is_active
)
SELECT
    'Dehradun Urban Services Department',
    'GOVERNMENT_DEPARTMENT'::organizationtype,
    'Demo government authority for waste-management coordination and urban service operations.',
    'Dehradun',
    'Uttarakhand',
    NULL,
    NULL,
    NULL,
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM organizations
    WHERE name = 'Dehradun Urban Services Department'
      AND district = 'Dehradun'
      AND state = 'Uttarakhand'
);

-- 3) Give the new authority competencies relevant to CH-8.
INSERT INTO organization_competencies (organization_id, category)
SELECT o.id, 'WASTE_MANAGEMENT'::challengecategory
FROM organizations o
WHERE o.name = 'Dehradun Urban Services Department'
  AND o.district = 'Dehradun'
  AND o.state = 'Uttarakhand'
ON CONFLICT (organization_id, category) DO NOTHING;

INSERT INTO organization_competencies (organization_id, category)
SELECT o.id, 'ENVIRONMENT'::challengecategory
FROM organizations o
WHERE o.name = 'Dehradun Urban Services Department'
  AND o.district = 'Dehradun'
  AND o.state = 'Uttarakhand'
ON CONFLICT (organization_id, category) DO NOTHING;

-- 4) CH-8 is our innovation-flow demonstration challenge.
-- Keep AI decision = HUMAN_REVIEW to preserve human-in-the-loop semantics,
-- but mark the innovation requirement as positive so the challenge can enter
-- the university/industry pipeline after authorized review.
UPDATE challenges
SET
    innovation_required = TRUE,
    ai_innovation_decision = 'HUMAN_REVIEW',
    ai_innovation_requires_human_review = TRUE,
    ai_innovation_type = 'PROCESS_INNOVATION',
    ai_innovation_type_decision = 'HUMAN_REVIEW',
    ai_innovation_type_requires_human_review = TRUE,
    ai_innovation_type_top_3 = '[{"rank":1,"type":"PROCESS_INNOVATION"},{"rank":2,"type":"RESEARCH_REQUIRED"},{"rank":3,"type":"GIS_REMOTE_SENSING"}]'::json,
    routing_reason = COALESCE(routing_reason, '') || ' Innovation flow enabled for this demo challenge after human review.'
WHERE id = 8;

COMMIT;

-- Verification queries
SELECT id, name, organization_type, state, district, parent_organization_id
FROM organizations
WHERE id IN (1,2)
   OR name = 'Dehradun Urban Services Department'
ORDER BY id;

SELECT o.id, o.name, oc.category
FROM organizations o
JOIN organization_competencies oc ON oc.organization_id = o.id
WHERE o.name = 'Dehradun Urban Services Department'
ORDER BY oc.category;

SELECT id, title, innovation_required, ai_innovation_decision, ai_innovation_type, current_authority_id
FROM challenges
WHERE id = 8;
