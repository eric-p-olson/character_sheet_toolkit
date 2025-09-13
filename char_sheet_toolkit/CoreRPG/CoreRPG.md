## CoreRPG xml formatting
CoreRPG is the xml format used by Fantasy Grounds

CoreRPG_8_1 is the version used for DnD 5e, including 2024
:   `<root version="4.6" dataversion="20241002" release="8.1|CoreRPG:6">`
<br/>I have not seen any official information on this xml schema nor it's naming scheme

### Files
- `CoreRPG.character.mako` - character summary for GUI
- `CoreRPG_8_1-properties.py` - adds useful properties specific to release 8.1
- `CoreRPG_8_1-patch.py` - fixes minor issues with Fantasy Grounds xml data because certain feature properties are not leveled-up in their wizard. No specific non-SRC data is provided. 
- `CoreRPG_dnd_2024_utils.py` - general DnD 2024 SRD level functions (To Hit, Damage based only on decoding on the xml datai)

