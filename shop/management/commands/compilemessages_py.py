from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
import struct
import array


def generate_mo(po_file, mo_file):
    """
    Generate a .mo file from a .po file using pure Python.
    Based on Python's msgfmt.py tool.
    """
    ID = 1
    STR = 2
    
    # Parse the catalog
    lines = open(po_file, encoding='utf-8').readlines()
    
    section = None
    fuzzy = False
    
    # Start off assuming Latin-1, so everything decodes without failure,
    # until we know the exact encoding
    encoding = 'utf-8'
    
    # Dictionary of msgid -> msgstr
    catalog = {}
    msgid = msgstr = b''
    
    for line in lines:
        # If we get a comment line after a msgstr, this is a new entry
        if line[0] == '#' and section == STR:
            if msgid or msgstr:  # Allow empty msgid (header)
                catalog[msgid] = msgstr
            section = None
            fuzzy = False
            msgid = msgstr = b''
        
        # Skip comments and empty lines
        if line[0] == '#':
            if 'fuzzy' in line:
                fuzzy = True
            continue
        
        # Start of msgid
        if line.startswith('msgid'):
            if section == STR:
                if msgid or msgstr:  # Save previous entry
                    catalog[msgid] = msgstr
            section = ID
            line = line[5:]
            msgid = msgstr = b''
        # Start of msgstr
        elif line.startswith('msgstr'):
            section = STR
            line = line[6:]
        
        # Strip and continue
        line = line.strip()
        if not line:
            continue
        
        # Evaluate the string
        line = eval(line, {}, {})
        
        if section == ID:
            msgid += line.encode(encoding)
        elif section == STR:
            msgstr += line.encode(encoding)
    
    # Add last entry
    if msgid or msgstr:
        catalog[msgid] = msgstr
    
    # The keys are sorted in the .mo file
    keys = sorted(catalog.keys())
    
    # Compute the offsets for all strings
    offsets = []
    ids = strs = b''
    
    for id in keys:
        # For each string, we need to store (offset, length) in a table
        offsets.append((len(ids), len(id), len(strs), len(catalog[id])))
        ids += id + b'\0'
        strs += catalog[id] + b'\0'
    
    # The output consists of:
    # - Header (7 integers)
    # - Key index (len(keys) pairs of integers)
    # - Value index (len(keys) pairs of integers)
    # - Key/value data
    
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    
    # Build the key index
    koffsets = []
    voffsets = []
    
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, keystart + o1]
        voffsets += [l2, valuestart + o2]
    
    offsets = koffsets + voffsets
    
    # Write the output file
    with open(mo_file, 'wb') as output:
        output.write(struct.pack(
            'Iiiiiii',
            0x950412de,                 # Magic
            0,                          # Version
            len(keys),                  # # of entries
            7 * 4,                      # start of key index
            7 * 4 + len(keys) * 8,      # start of value index
            0, 0))                      # size and offset of hash table
        
        output.write(array.array('i', offsets).tobytes())
        output.write(ids)
        output.write(strs)


class Command(BaseCommand):
    help = 'Compile .po files to .mo without msgfmt (pure Python fallback)'

    def handle(self, *args, **options):
        base = Path.cwd()
        locale_dir = base / 'locale'
        
        if not locale_dir.exists():
            raise CommandError('No locale directory found at project root')

        compiled = []
        for lang_dir in locale_dir.iterdir():
            if not lang_dir.is_dir():
                continue
            lc_messages = lang_dir / 'LC_MESSAGES'
            if not lc_messages.exists():
                continue
            
            for po in lc_messages.glob('*.po'):
                mo = po.with_suffix('.mo')
                try:
                    generate_mo(str(po), str(mo))
                    compiled.append(str(mo))
                    self.stdout.write(f'Compiled: {mo}')
                except Exception as e:
                    raise CommandError(f'Error compiling {po}: {e}')

        if not compiled:
            self.stdout.write('No .po files found to compile.')
