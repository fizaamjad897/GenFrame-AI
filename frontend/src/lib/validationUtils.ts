/**
 * Email validation utilities
 */

/**
 * Validates email format according to commonly accepted standards
 * Checks for:
 * - Valid characters in local part
 * - Presence of @ symbol
 * - Valid domain format
 * - Valid TLD
 *
 * @param email - Email address to validate
 * @returns true if email is valid, false otherwise
 */
export function validateEmail(email: string): boolean {
  if (!email || typeof email !== "string") {
    return false;
  }

  // Trim whitespace
  const trimmed = email.trim();

  // Basic length checks
  if (trimmed.length === 0 || trimmed.length > 254) {
    return false;
  }

  // Must contain exactly one @
  const atCount = (trimmed.match(/@/g) || []).length;
  if (atCount !== 1) {
    return false;
  }

  const [localPart, domain] = trimmed.split("@");

  // Validate local part (before @)
  if (!validateEmailLocalPart(localPart)) {
    return false;
  }

  // Validate domain part (after @)
  if (!validateEmailDomain(domain)) {
    return false;
  }

  return true;
}

/**
 * Validates the local part of an email (before @)
 *
 * @param localPart - Local part of email
 * @returns true if valid, false otherwise
 */
function validateEmailLocalPart(localPart: string): boolean {
  // Local part must be 1-64 characters
  if (localPart.length === 0 || localPart.length > 64) {
    return false;
  }

  // Cannot start or end with dot
  if (localPart.startsWith(".") || localPart.endsWith(".")) {
    return false;
  }

  // Cannot have consecutive dots
  if (localPart.includes("..")) {
    return false;
  }

  // Valid characters: letters, digits, dots, hyphens, underscores, plus signs
  const localPartRegex = /^[a-zA-Z0-9._+-]+$/;
  return localPartRegex.test(localPart);
}

/**
 * Validates the domain part of an email (after @)
 *
 * @param domain - Domain part of email
 * @returns true if valid, false otherwise
 */
function validateEmailDomain(domain: string): boolean {
  // Domain must be 1-255 characters
  if (domain.length === 0 || domain.length > 255) {
    return false;
  }

  // Cannot start or end with dot or hyphen
  if (
    domain.startsWith(".") ||
    domain.endsWith(".") ||
    domain.startsWith("-") ||
    domain.endsWith("-")
  ) {
    return false;
  }

  // Must contain at least one dot
  if (!domain.includes(".")) {
    return false;
  }

  // Cannot have consecutive dots
  if (domain.includes("..")) {
    return false;
  }

  // Split into labels (parts between dots)
  const labels = domain.split(".");

  // Each label must be 1-63 characters
  // Labels can contain letters, digits, and hyphens
  // Labels cannot start or end with hyphen
  const labelRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;

  for (const label of labels) {
    if (label.length === 0 || label.length > 63) {
      return false;
    }
    if (!labelRegex.test(label)) {
      return false;
    }
  }

  // TLD (last label) must be at least 2 characters and contain only letters
  const tld = labels[labels.length - 1];
  if (tld.length < 2 || !/^[a-zA-Z]{2,}$/.test(tld)) {
    return false;
  }

  return true;
}

/**
 * Gets an error message for email validation failure
 *
 * @param email - Email address to validate
 * @returns Error message if invalid, empty string if valid
 */
export function getEmailValidationError(email: string): string {
  if (!email || typeof email !== "string") {
    return "Email is required";
  }

  const trimmed = email.trim();

  if (trimmed.length === 0) {
    return "Email is required";
  }

  // Use the validateEmail function to check if valid
  if (!validateEmail(trimmed)) {
    return "Please enter a valid email address";
  }

  return "";
}
