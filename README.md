<div align="center">
  <p>
    <img alt="HexHunter Logo" src="https://raw.githubusercontent.com/scholarsmate/Hex-Hunter/main/images/HexHunter-Logo.png" width=160>
    <h1>Hex-Hunter<br/>find encoded data</h1>
  </p>
</div>

Hex-Hunter, and similar data detection tools, are important in a variety of fields for several reasons:

1. **Cybersecurity**: Malicious actors often use data encoding to hide their activities or to deliver payloads in an
   obfuscated form. By identifying encoded data within files, cybersecurity professionals can detect these attempts, 
   understand the nature of the threat, and design appropriate countermeasures.

2. **Forensic Analysis**: During digital forensic investigations, encoded data can provide critical insights. The
   encoded data may contain evidence, such as hidden messages or transactions, illicit content, or traces of
   unauthorized activity.

3. **Data Recovery**: If files have been damaged or corrupted, tools like Hex-Hunter can help recover parts of the data 
   by recognizing and extracting encoded segments.

4. **Research and Development**: Researchers and developers can use such tools to better understand encoding schemes and
   how they are used or misused in real-world applications.

5. **Reverse Engineering and Malware Analysis**: Finding and decoding encoded data can often be a starting point for
   reverse-engineering software or analyzing malware.

6. **Compliance and Auditing**: Encoded data can sometimes be used to bypass security controls or hide non-compliance
   with data handling policies. Identifying encoded data can be a step in auditing and ensuring compliance.

By extending Hex-Hunter to detect other forms of encoded data, it could be made even more useful in these and other
contexts. Given the increasing reliance on digital data and the rising threat of cybercrime, tools like Hex-Hunter can
play an important role in maintaining security and integrity of digital resources.

## Binary to Text Encodings
Binary to text encodings are methods designed to encode data using only characters in the set of 94 _printable_ US-ASCII
characters (decimal values in the range of 32 – 126, inclusive).

| Byte Character | Byte Character | Byte Character | Byte Character |
|----------------|----------------|----------------|----------------|
| 32 ' ' (space) | 56 8           | 80 P           | 104 h          |
| 33 !           | 57 9           | 81 Q           | 105 i          |
| 34 "           | 58 :           | 82 R           | 106 j          |
| 35 #           | 59 ;           | 83 S           | 107 k          |
| 36 $           | 60 <           | 84 T           | 108 l          |
| 37 %           | 61 =           | 85 U           | 109 m          |
| 38 &           | 62 >           | 86 V           | 110 n          |
| 39 '           | 63 ?           | 87 W           | 111 o          |
| 40 (           | 64 @           | 88 X           | 112 p          |
| 41 )           | 65 A           | 89 Y           | 113 q          |
| 42 *           | 66 B           | 90 Z           | 114 r          |
| 43 +           | 67 C           | 91 [           | 115 s          |
| 44 ,           | 68 D           | 92 \           | 116 t          |
| 45 -           | 69 E           | 93 ]           | 117 u          |
| 46 .           | 70 F           | 94 ^           | 118 v          |
| 47 /           | 71 G           | 95 _           | 119 w          |
| 48 0           | 72 H           | 96 `           | 120 x          |
| 49 1           | 73 I           | 97 a           | 121 y          |
| 50 2           | 74 J           | 98 b           | 122 z          |
| 51 3           | 75 K           | 99 c           | 123 {          |
| 52 4           | 76 L           | 100 d          | 124 |          |
| 53 5           | 77 M           | 101 e          | 125 }          |
| 54 6           | 78 N           | 102 f          | 126 ~          |
| 55 7           | 79 O           | 103 g          |                |

Here is the set of 94 printable characters in python:

```python
>>> [chr(i) for i in range(32,127)]
[' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
>>>
```


### Domain and Range

Text encodings are defined as functions that map bytes into a set of printable US-ASCII characters.  The domain of these
functions is the set of 256 possible byte values and the range is the set of valid outputs from the encoding function.  
In the case of the text encoding functions, the range is always smaller than the domain, so a byte in the domain will
always map to one or more bytes in the range.  Since the range is always smaller than the domain, the number of range
bytes from a text encoder function will always be equal to or greater than the number of domain bytes.

For many of the encodings, the number of range bytes can be precisely calculated based only on the number of domain
bytes.  We will call this set of text encodings “fixed-range encodings”.  

Other encodings will depend on the value of the domain bytes to determine the number of bytes required to encode the
output bytes yielding a range of possible output lengths (best case to worse case).

### Line Break - CRLF

The term CRLF, in this document, refers to the sequence of octets corresponding to the two US-ASCII characters for
Carriage Return (CR, decimal value 13) and Line Feed (LF, decimal value 10) which, when taken together, in this order,
denote a line break.

## General Algorithm for Segment Bounding

<div align="center">
  <img alt="HexHunter General Algorithm Flow" src="https://raw.githubusercontent.com/scholarsmate/Hex-Hunter/main/images/HexHunter-GeneralFlow.png" width=600>
</div>

To locate the start of an encoded data segment, iterate over the octets until an octet that is in the range of the
encoding is found.  From this starting location, iterate over the octets following the starting octet, appending them to
the segment until an octet is found that is not in the range of the encoding, or the end of the data/stream has been
reached.  The segment is then scrutinized further (sometimes the initial segment gets shrunk or grown), using
encoding-specific techniques, to determine if encoded data is suspected or not.

<div align="center">
  <img alt="HexHunter General Validation Flow" src="https://raw.githubusercontent.com/scholarsmate/Hex-Hunter/main/images/HexHunter-GeneralValidation.png" width=600>
</div>

The segment is then evaluated against a series of encoding-specific criteria to determine if the segment (or a slice
thereof) is valid with respect to the given encoding format.  The encoded data could have encoding-legal bytes directly
before and/or after the encoded data that will be part of the segment being evaluated.  If possible, the evaluation will
make a reasonable attempt to determine a valid slice of the segment.

## Popular Encodings

### Base 64 

Fixed range: yes
Case-sensitive: yes
Overhead: 33-37% (33% by the encoding itself and up to 4% for the inserted line breaks)
Popular for: MIME encoding

Base 64 is a family of encoding schemes that encode binary data by treating it numerically and translating it into a
base-64 representation, encoding 3 bytes of domain data into 4 bytes of range data.  Every four characters of Base64
encoded text (4 sextets = 4 × 6 = 24 bits) representing three octets of domain data (3 octets = 3 × 8 = 24 bits).

#### Range

The character sets that make up the 64-character range required for Base64 vary among implementations. In general, the 
set of the 64 characters are both 1) part of a subset common to most character encodings, and 2) printable. This
combination of properties helps ensure that data will not be modified in transit through systems such as email, which are
not traditionally 8-bit clean. For example, MIME's Base64 implementation uses A-Z, a-z, and 0-9 characters for the first
sixty-two values, as well as the "+" and "/" characters for the last two. Other variations, share these properties but
differ in the characters chosen for the last two values, for example, the URL and filename safe "RFC 4648 / Base64URL"
variant, which uses "-" and "_".

#### Line Breaks

Base64 encoded data is a continuous stream of characters generally without any whitespace.  According to the MIME
(RFC 2045) specification (https://www.ietf.org/rfc/rfc2045.txt), however states that the encoded lines must be no more 
than 76 characters long, not counting the trailing CRLF. 

#### Output padding

When the length of the input data is not a multiple of three, the encoded output can have padding added so that its
length is a multiple of four. The padding character indicates to the decoder that no further bits are needed to fully 
decode the data.  Traditionally “=” is used as the padding character.

#### Canonical Representation

The canonical Base 64 representation is detailed in RPC-4648 section 4.

The Base 64 encoding is designed to represent arbitrary sequences of octets in a form that allows the use of both
upper- and lowercase letters but that need not be human readable.

A 65-character subset of US-ASCII is used, enabling 6 bits to be represented per printable character.  (The extra 65th
character, "=", is used to signify a special processing function.)

The encoding process represents 24-bit groups of input bits as output strings of 4 encoded characters.  Proceeding from
left to right, a 24-bit input group is formed by concatenating 3 8-bit input groups. These 24 bits are then treated as 4
concatenated 6-bit groups, each of which is translated into a single character in the base 64 alphabet.

Each 6-bit group is used as an index into an array of 64 printable characters.  The character referenced by the index is
placed in the output string.

#### Base 64 Alphabet

| Value Encoding | Value Encoding | Value Encoding | Value Encoding |
|----------------|----------------|----------------|----------------|
|     0 A        |   17 R         |  34 i          | 51 z           |
|     1 B        |   18 S         |  35 j          | 52 0           |
|     2 C        |   19 T         |  36 k          | 53 1           |
|     3 D        |   20 U         |  37 l          | 54 2           |
|     4 E        |   21 V         |  38 m          | 55 3           |
|     5 F        |   22 W         |  39 n          | 56 4           |
|     6 G        |   23 X         |  40 o          | 57 5           |
|     7 H        |   24 Y         |  41 p          | 58 6           |
|     8 I        |   25 Z         |  42 q          | 59 7           |
|     9 J        |   26 a         |  43 r          | 60 8           |
|    10 K        |   27 b         |  44 s          | 61 9           |
|    11 L        |   28 c         |  45 t          | 62 +           |
|    12 M        |   29 d         |  46 u          | 63 /           |
|    13 N        |   30 e         |  47 v          |                |
|    14 O        |   31 f         |  48 w          | (pad) =        |
|    15 P        |   32 g         |  49 x          |                |
|    16 Q        |   33 h         |  50 y          |                |

Special processing is performed if fewer than 24 bits are available at the end of the data being encoded.  A full
encoding quantum is always completed at the end of a quantity.  When fewer than 24 input bits are available in an input
group, bits with value zero are added (on the right) to form an integral number of 6-bit groups.  Padding at the end of
the data is performed using the '=' character.  Since all base 64 input is an integral number of octets, only the
following 3 cases can arise:

1.	The final quantum of encoding input is an integral multiple of 24 bits; here, the final unit of encoded output will be
    an integral multiple of 4 characters with no "=" padding.

2.	The final quantum of encoding input is exactly 8 bits; here, the final unit of encoded output will be two characters 
    followed by two "=" padding characters.

3.	The final quantum of encoding input is exactly 16 bits; here, the final unit of encoded output will be three 
    characters followed by one "=" padding character.

#### Variations

1. **URL-Safe** - encode into an URL- and filename- friendly Base64 variant (RFC 4648 / Base64URL) where the `+` and `/`
characters are respectively replaced by `-` and `_`, and the padding `=` characters are omitted.

#### Base 64 Specific Bounding

The range is the 64 characters in the canonical Base 64 alphabet, along with the pad (“=”), “-“, “_”, CRLF, and LF.
This range covers the canonical Base 64, and Base64URL, along with possible line breaks and padding.  The size of this
range is 69.

To find base64-encoded data, the algorithm follows the general algorithm building a segment with base64-legal bytes.  The
segment evaluation then proceeds as follows:

1. Does the segment meet a configurable minimum length requirement?  If it does, proceed to step 2, else, the segment is
   considered not valid.

2. Can the segment be base64-decoded?  If so, the segment is considered valid, else, proceed to step 3.

3. If the segment cannot be decoded, and the last byte in the segment is equal to '=', slice off the _first byte_ of the
   segment, else, slice off the _last byte_ of the segment and return to step 1.

#### Additional Tuning

1. **Block detection** - base64-encoded data are often encoded in blocks where the character sequences are broken up
   every 76 characters (e.g., MIME) with a line break.  If line breaks appear in the segment at regular 76-character
   intervals, this information can help to bound the segment.

#### Examples 

Input: [100 bytes]

```text
!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~123456
```

Output: [136 bytes]

```text
ISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fjEyMzQ1Ng==
```

76-character wide chunks: [137 bytes]

```text
ISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZ
WltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fjEyMzQ1Ng==
```

Base64URL URL-Safe encoding: [135 bytes]

```text
ICEiIyQlJlwnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4_QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fjEyMw
```

Base64URL URL-Safe encoding with 76-character wide chunks: [136 bytes]

```text
ISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZ
WltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fjEyMzQ1Ng
```

### Base16 (Hexadecimal Encoding)

Base16 encoding, also known as hexadecimal encoding, represents binary data as a text string using the characters 0-9
and A-F. Each binary byte (8 bits) is represented by two hexadecimal digits, meaning a byte of data can have values
ranging from 00 to FF (0-255 in decimal).

To find hex-encoded data, the algorithm follows the general algorithm building a string with hexadecimal-legal bytes.
The string evaluation then proceeds as follows:

1. Does the string meet a configurable minimum length requirement?  If it does, proceed to step 2, else, the string is
considered not valid.
2. Can the string be hex-decoded (the string length should be even)?  If so, the string is considered valid, else,
proceed to step 3.
3. If the string cannot be decoded, pop off the last byte of the string and return to step 1.

#### Examples

Input: [100 bytes]

```text
!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~123456
```

Output: [200 bytes]

```text
2122232425262728292A2B2C2D2E2F303132333435363738393A3B3C3D3E3F404142434445464748494A4B4C4D4E4F505152535455565758595A5B5C5D5E5F606162636465666768696A6B6C6D6E6F707172737475767778797A7B7C7D7E313233343536
```

#### Additional Tuning

1. **Case sensitivity** - Hex-legal bytes include the alphabetical characters `A`, `B`, `C`, `D`, `E`, and `F`, and are
legal in upper and lower case.  In general an encoder will use either upper or lower case and won't mix cases.  For
example an encoder would encode the binary `10101011` as either `AB` (upper case) or `ab` (lower case), but not `Ab`
(mixed case) or `aB` (mixed case).  We can use this tuning to ensure that our strings only contain letters of the same
case to further discriminate string membership.

### Base32

Base32 encoding represents binary data as text using a set of 32 different characters: the twenty-six upper-case
letters A–Z and the digits 2–7. This set of characters is chosen because they are unambiguous and widely used in both
human and machine-readable contexts. Each group of 5 bits in the binary data (from the total of 8 bits in a byte)
corresponds to one Base32 character. This results in a text string that's longer than the original data but that can be
transmitted more safely and reliably over various systems.

#### Examples

Input: [100 bytes]

```text
!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~123456
```

Output: [160 bytes]

```text
EERCGJBFEYTSQKJKFMWC2LRPGAYTEMZUGU3DOOBZHI5TYPJ6H5AECQSDIRCUMR2IJFFEWTCNJZHVAUKSKNKFKVSXLBMVUW24LVPF6YDBMJRWIZLGM5UGS2TLNRWW433QOFZHG5DVOZ3XQ6L2PN6H27RRGIZTINJW
```

### Base85

Base85 encoding, also known as Ascii85, is a type of binary-to-text encoding developed to be more space-efficient than
Base64. It represents 4 bytes (32 bits) of binary data as 5 ASCII characters. The advantage of Base85 is that it's more
compact than Base64, making it useful for encoding large amounts of binary data, like images, in situations where space
is a concern.

#### Examples

Input: [100 bytes]

```text
!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~123456
```

Output: [125 bytes]

```text
AtECrB_<~*DJm;0EiNxGF)}kWH8wXmIXXK$Jw87`K|(`BMMg(RNlHshO-@fxQBqS>RaRG6Sz23MU0z>cVPa!sWoBn+X=-b1ZEkOHadLBXb#`}nd3t+%eSR@AGc+|e 
```

## References

1. Base 64 - https://datatracker.ietf.org/doc/html/rfc4648#section-4
