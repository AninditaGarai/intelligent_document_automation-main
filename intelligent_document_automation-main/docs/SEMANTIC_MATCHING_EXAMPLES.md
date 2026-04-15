# Semantic Matching Explanations - Examples

This document demonstrates the **explainable semantic matching** output from the Intelligent Document Automation system.

---

## Overview

The semantic matching module compares extracted fields across documents and provides:
1. **Match Status** (Matched / Likely Matched / Partial Match / Not Matched)
2. **Numerical Score** (0-100, higher = better match)
3. **Human-Readable Explanation** (why the decision was made)
4. **Confidence Metrics** (extraction confidence for each value)

This implements **Explainable AI (XAI)** principles by making every decision auditable.

---

## Example 1: Perfect Match - Client Name

### Scenario
Matching client names across quotation and SOW documents:

```
Document 1 (Quotation): "ABC Corporation Limited"
Document 2 (SOW):       "ABC Corp Ltd"
```

### Processing
1. **Text Normalization**:
   - Doc1: "abc corporation limited"
   - Doc2: "abc corp ltd" → "abc corporation limited" (after abbreviation expansion)

2. **Similarity Calculation**:
   - Before: 78% similarity (abbreviations make them differ)
   - After: 100% match (normalized forms are identical)

3. **Confidence Adjustment**:
   - Extracted confidence: Doc1=80%, Doc2=75%
   - Both have reasonable extraction confidence

### Output
```
Field: Client Name
Status: Matched ✅
Match Score: 95.3/100

Value 1: ABC Corporation Limited (Confidence: 80%)
Value 2: ABC Corp Ltd (Confidence: 75%)

Explanation:
  High semantic similarity (95.3%). Values are essentially equivalent.
  Normalization expanded abbreviations: "Corp" → "Corporation", "Ltd" → "Limited"
  Normalized texts match: "abc corporation limited" = "abc corporation limited"
```

---

## Example 2: Likely Matched - Organization Name

### Scenario
Different formatting of same organization:

```
Document 1 (Contract): "XYZ Services Pvt. Ltd. (India)"
Document 2 (Invoice):  "XYZ Services Private Limited"
```

### Processing
1. **Text Normalization**:
   - Doc1: "xyz services pvt ltd india" (removed punctuation, converted case)
   - Doc2: "xyz services private limited"

2. **Similarity Calculation**:
   - Sequence Match: 85% (extra "india" causes mismatch)
   - Token Overlap: 75% (shared tokens: xyz, services, private/pvt, limited)
   - Weighted: (85% × 0.6) + (75% × 0.4) = 81%

3. **Match Classification**:
   - Score 81% falls into "Likely Matched (70-89%)" range

### Output
```
Field: Organization Name
Status: Likely Matched ⚠️
Match Score: 81.2/100

Value 1: XYZ Services Pvt. Ltd. (India) (Confidence: 85%)
Value 2: XYZ Services Private Limited (Confidence: 80%)

Explanation:
  Moderate semantic similarity (81.2%). Values are very similar with minor differences.
  - Normalized Doc1: "xyz services pvt ltd india"
  - Normalized Doc2: "xyz services private limited"
  Difference: Extra location tag "(India)" in first value.
  This could be the same organization with location specifications.
```

---

## Example 3: Partial Match - Currency

### Scenario
Currency specified in different formats:

```
Document 1: "$"
Document 2: "USD"
```

### Processing
1. **Extraction**:
   - Doc1: Currency symbol " $" → Mapped to "USD"
   - Doc2: Currency code "USD" → Already normalized

2. **Similarity**:
   - Both normalize to "USD"
   - Character match: 100% identical

3. **Confidence**:
   - Doc1 extraction confidence: 95% (symbol clearly visible)
   - Doc2 extraction confidence: 100% (explicit code)

### Output
```
Field: Currency
Status: Matched ✅
Match Score: 100.0/100

Value 1: USD (Confidence: 95%)
Value 2: USD (Confidence: 100%)

Explanation:
  Values are identical: both resolve to USD.
  Method: Exact match after normalization.
```

---

## Example 4: No Match - Mismatched Values

### Scenario
Different client names in two documents:

```
Document 1: "Global Tech Solutions"
Document 2: "TechSoft Industries"
```

### Processing
1. **Text Normalization**:
   - Doc1: "global tech solutions"
   - Doc2: "techsoft industries"

2. **Similarity Calculation**:
   - Sequence Match: 25% (only "tech" is common)
   - Token Overlap: 20% (only "tech" appears in both)
   - Weighted: (25% × 0.6) + (20% × 0.4) = 23%

3. **Match Classification**:
   - Score 23% < 50% threshold → "Not Matched"

### Output
```
Field: Client Name
Status: Not Matched ❌
Match Score: 23.4/100

Value 1: Global Tech Solutions (Confidence: 82%)
Value 2: TechSoft Industries (Confidence: 88%)

Explanation:
  Very low similarity (23.4%). Values appear to be different.
  - Normalized Doc1: "global tech solutions"
  - Normalized Doc2: "techsoft industries"
  Only token overlap: "tech"
  Recommendation: These are likely different organizations. Manual review recommended.
```

---

## Example 5: Missing Field - Billing Address

### Scenario
Billing address not clearly marked in documents:

```
Document 1: [Address section not found]
Document 2: [No explicit "Billing Address:" label]
```

### Processing
1. **Extraction Attempt**:
   - Pattern matching for "Address:", "Billing Address:" → Not found
   - Postal code pattern search → No match
   - Heuristic for "City, State" format → No match

2. **Confidence**:
   - Both documents: 0% confidence (field not found)

### Output
```
Field: Billing Address
Status: Not Found ⚠️
Match Score: 0/100

Value 1: Not Found (Confidence: 0%)
Value 2: Not Found (Confidence: 0%)

Explanation:
  Field missing in both documents.
  Neither document explicitly marks a billing address section.
  This information may not be required for these document types, or may be
  present in different locations (e.g., within contract definition section).
  Manual verification recommended if this field is critical.
```

---

## Example 6: One Value Missing

### Scenario
Field exists in one document but not the other:

```
Document 1 (Quotation): "INR" (Currency)
Document 2 (Contract):  [Currency not found]
```

### Processing
1. **Currency Extraction**:
   - Doc1: Symbol "₹" or text "INR" found → "INR" extracted
   - Doc2: No currency symbols/codes found

2. **Match Attempt**:
   - Cannot compare: one value missing

### Output
```
Field: Currency
Status: Not Matched 🔍
Match Score: 0/100

Value 1: INR (Confidence: 92%)
Value 2: Not Found (Confidence: 0%)

Explanation:
  Field missing in one document.
  Currency specified in Document 1: INR (Indian Rupee)
  Currency not explicitly stated in Document 2.
  Recommendation: The contract may not specify currency (inherited from other document)
  or currency information is embedded in price values. Check context.
```

---

## Example 7: Low Extraction Confidence Impact

### Scenario
Values were extracted with low confidence:

```
Document 1: "Bank of Indra Ltd" (Confidence: 45% - OCR uncertainty)
Document 2: "Bank of India Ltd" (Confidence: 92% - Clear text)
```

### Processing
1. **Similarity Calculation**:
   - Sequence Match: 96% ("Indra" vs "India" = 1 character difference)

2. **Confidence Adjustment**:
   - Doc1 has low extraction confidence (45%)
   - This affects overall match reliability

3. **Final Score**:
   - Raw similarity: 96%
   - Adjusted for low extraction confidence

### Output
```
Field: Organization Name
Status: Likely Matched ⚠️
Match Score: 78.5/100

Value 1: Bank of Indra Ltd (Confidence: 45% - LOW)
Value 2: Bank of India Ltd (Confidence: 92%)

Explanation:
  Moderate semantic similarity (78.5%). Values appear to be the same organization
  but with one critical difference: "Indra" vs "India".
  
  Analysis:
  - Could be OCR error: "India" was misread as "Indra"
  - Or could be different organizations (unlikely given similarity)
  
  Caution: Low extraction confidence (45%) in Document 1.
  The OCR was uncertain about this field.
  
  Recommendation: Manually verify the correct organization name,
  especially since confidence in Doc1 extraction is low. The "India" vs "Indra"
  distinction is critical for entity identification.
```

---

## Key Concepts in Explanations

### Match Status Hierarchy
- **Matched (≥90%)**: Use with confidence
- **Likely Matched (70-89%)**: Probably correct, verify if critical
- **Partial Match (50-69%)**: Significant differences, manual check needed
- **Not Matched (<50%)**: Values are different entities
- **Not Found**: Field missing from one or both documents

### Confidence Scoring
```
Extraction Confidence | Meaning
0-30%               | Very uncertain (OCR error likely)
31-60%              | Moderate uncertainty (needs verification)
61-80%              | Good confidence
81-100%             | High confidence
```

### Normalization Transformations
1. **Case**: "ABC" → "abc"
2. **Spacing**: "A  B" → "a b"
3. **Punctuation**: "A.B" → "ab"
4. **Abbreviations**: "Pvt Ltd" → "private limited"
5. **Special Characters**: "A&B" → "ab"

### Similarity Methods
- **Sequence Matching**: Longest contiguous matching substrings (60% weight)
- **Token Overlap**: Jaccard similarity of word tokens (40% weight)
- **Abbreviation Handling**: Dynamic dictionary expansion

---

## Using Explanations in Analysis

### When to Trust Matches
✅ Match Score ≥90% AND Extraction Confidence ≥80%  
✅ Explanations confirm semantic equivalence  
✅ No significant field missing in either document

### When to Verify Manually
⚠️ Match Score 70-89%  
⚠️ Extraction Confidence <60%  
⚠️ Values differ substantially but contain similar tokens

### When to Flag as Issues
❌ Match Score <50%  
❌ Field completely missing  
❌ Extraction produced "Not Found"

---

## Advanced Matching Scenarios

### Multi-variant Company Names
```
"Microsoft Corporation"
"Microsoft Corp"
"MSFT"
"Microsoft"

Matching: First two will match 95%+, third requires external lookup
```

### International Abbreviations
```
"Pvt Ltd" (Singapore/India)
"GmbH" (Germany)
"SARL" (France)
"BV" (Netherlands)

System: Recognizes first two, others need custom configuration
```

### Postal Code Variations
```
Query: "123456" vs "123-456" vs "123 456"
Normalization removes punctuation/spaces: all become "123456"
Match: 100%
```

---

## Viva Discussion Points

**Q: Why are explanations important?**  
A: They prove every decision is auditable and not a "black box" decision from an LLM.

**Q: How does this handle real-world OCR errors?**  
A: Normalization and token overlap tolerate minor errors. Confidence scores highlight when to verify.

**Q: Can abbreviations cause false positives?**  
A: Possible, but mapping is conservative. Longer matches more reliable than short ones.

**Q: How do you handle domain-specific terms?**  
A: Custom abbreviation mappings can be added to `SemanticMatcher.abbreviation_map`

---

## Conclusion

The semantic matching system provides **transparent, explainable decisions** that can be:
- Understood by humans
- Traced through code
- Validated against original documents
- Improved through feedback

This makes it production-ready for **audit trails and compliance requirements**.

