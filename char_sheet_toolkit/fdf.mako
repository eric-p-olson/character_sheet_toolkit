<%!
     def utf16be(text):
        """fdf string must be utf16be if they are not ascii"""
        if any(ord(c) > 127 for c in text):
            utf16_be = text.encode("utf-16-be")  # Convert to UTF-16 Big-Endian bytes
            return "þÿ" + "".join(chr(b) for b in utf16_be)  # Convert bytes to %XX format
        else:
            return text
%>

%%FDF-1.2
1 0 obj
<<
/FDF<<
## UF: univeral path, F: local path
/UF(${base_pdf_file})
/F(${base_pdf_file})
/Fields[
% for field in field_assignments:
%  if field_assignments[field].startswith('/'):
<</T(${field})/V${field_assignments[field]}>>
%  else:
<</T(${field})/V(${field_assignments[field]|utf16be})>>
%  endif
% endfor
]>>>>
endobj

trailer
<</Root 1 0 R>>
%%%EOF
