<div align="center">
  <p>
    <img alt="HexHunter Logo" src="https://raw.githubusercontent.com/scholarsmate/Hex-Hunter/main/images/HexHunter-Logo.png" width=160>
    <h1>Hex-Hunter<br/>find encoded data</h1>
  </p>
</div>

## General Algorithm
<div align="center">
  <img alt="HexHunter General Algorithm Flow" src="https://raw.githubusercontent.com/scholarsmate/Hex-Hunter/main/images/HexHunter-GeneralFlow.png" width=600>
</div>
In general, the algorithm will evaluate the input stream byte by byte.  When it comes across a byte that is in the legal
byte range for a given encoding, it pushes that byte onto the end of an empty string.  As bytes continue to be in the
legal range of the given encoding, bytes continue to be pushed onto the end of the string until either we evaluate a
byte that is not in the legal range of the given encoding, or the input stream is exhausted.

<div align="center">
  <img alt="HexHunter General Validation Flow" src="https://raw.githubusercontent.com/scholarsmate/Hex-Hunter/main/images/HexHunter-GeneralValidation.png" width=600>
</div>

Once one of these two events happen, the string is evaluated against a series of encoding-specific criteria to determine
if the string (or a slice thereof) is valid with respect to the given encoding format.  The encoded data could have
encoding-legal bytes directly before and/or after the encoded data that will be part of the string being evaluated.  If
possible, the evaluation will make a reasonable attempt to determine a valid slice of the given string.

### Hex

To find hex-encoded data, the algorithm follows the general algorithm building a string with hexadecimal-legal bytes.
The string evaluation then proceeds as follows:

1. Does the string meet a configurable minimum length requirement?  If it does, proceed to step 2, else, the string is
considered not valid.
2. Can the string be hex-decoded (the string length should be even)?  If so, the string is considered valid, else,
proceed to step 3.
3. If the string cannot be decoded, pop off the last byte of the string and return to step 1.

#### Additional Tuning

1. **Case sensitivity** - Hex-legal bytes include the alphabetical characters `A`, `B`, `C`, `D`, `E`, and `F`, and are
legal in upper and lower case.  In general an encoder will use either upper or lower case and won't mix cases.  For
example an encoder would encode the binary `10101011` as either `AB` (upper case) or `ab` (lower case), but not `Ab`
(mixed case) or `aB` (mixed case).  We can use this tuning to ensure that our strings only contain letters of the same
case to further discriminate string membership.

### Base64

To find base64-encoded data, the algorithm follows the general algorithm building a string with base64-legal bytes.
The string evaluation then proceeds as follows:

1. Does the string meet a configurable minimum length requirement?  If it does, proceed to step 2, else, the string is
considered not valid.
2. Can the string be base64-decoded?  If so, the string is considered valid, else, proceed to step 3.
3. If the string cannot be decoded, and the last byte in the string is equal to '=', pop off the _first byte_ of the
string, else, pop off the _last byte_ of the string and return to step 1.

#### Additional Tuning

1. **Block detection** - base64-encoded data are often encoded in blocks where the character sequences are broken up
every 76 characters (e.g., MIME) with a newline.

#### Different Legal Ranges

1. **URL-Safe** - encode into an URL- and filename- friendly Base64 variant (RFC 4648 / Base64URL) where the `+` and `/`
characters are respectively replaced by `-` and `_`, and the padding `=` characters are omitted.
