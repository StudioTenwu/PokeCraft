// Markdown rendering utility for AICraft Companion
// Safely renders markdown to HTML with XSS protection

/**
 * Render markdown to safe HTML
 * @param {string} markdownText - Raw markdown text from agent
 * @returns {string} - Sanitized HTML safe for innerHTML
 */
function renderMarkdown(markdownText) {
  if (!markdownText) {
    return '';
  }

  // Parse markdown to HTML using marked.js
  const rawHTML = marked.parse(markdownText, {
    breaks: true,  // Convert \n to <br>
    gfm: true,     // GitHub Flavored Markdown
  });

  // Sanitize HTML to prevent XSS attacks
  const safeHTML = DOMPurify.sanitize(rawHTML, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'code', 'pre',
      'a', 'ul', 'ol', 'li', 'blockquote',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'span', 'div'
    ],
    ALLOWED_ATTR: ['href', 'title', 'class'],
    ALLOW_DATA_ATTR: false,
  });

  return safeHTML;
}

/**
 * Check if text contains markdown syntax
 * @param {string} text - Text to check
 * @returns {boolean} - True if text appears to contain markdown
 */
function hasMarkdown(text) {
  if (!text) return false;

  // Common markdown patterns
  const markdownPatterns = [
    /\*\*.*\*\*/,      // Bold
    /\*.*\*/,          // Italic
    /__.*__/,          // Bold (underscore)
    /_.*_/,            // Italic (underscore)
    /`.*`/,            // Inline code
    /```[\s\S]*```/,   // Code block
    /\[.*\]\(.*\)/,    // Link
    /^#{1,6}\s/m,      // Heading
    /^>\s/m,           // Blockquote
    /^[-*+]\s/m,       // Unordered list
    /^\d+\.\s/m,       // Ordered list
  ];

  return markdownPatterns.some(pattern => pattern.test(text));
}
