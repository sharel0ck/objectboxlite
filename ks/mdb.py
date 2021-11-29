# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mdb(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_pages = []
        self.pages = []
        i = 0
        while not self._io.is_eof():
            self._raw_pages.append(self._io.read_bytes(4096))
            _io__raw_pages = KaitaiStream(BytesIO(self._raw_pages[-1]))
            self.pages.append(Mdb.Page(_io__raw_pages, self, self._root))
            i += 1


    class Page(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.page_type
            if _on == 1:
                self.page = Mdb.Page.Link(self._io, self, self._root)
            elif _on == 2:
                self.page = Mdb.Page.Data(self._io, self, self._root)
            elif _on == 8:
                self.page = Mdb.Page.Head(self._io, self, self._root)

        class Head(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.header = self._io.read_bytes(16)

            @property
            def page_count(self):
                if hasattr(self, '_m_page_count'):
                    return self._m_page_count if hasattr(self, '_m_page_count') else None

                _pos = self._io.pos()
                self._io.seek(120)
                self._m_page_count = self._io.read_u2le()
                self._io.seek(_pos)
                return self._m_page_count if hasattr(self, '_m_page_count') else None

            @property
            def page_point(self):
                if hasattr(self, '_m_page_point'):
                    return self._m_page_point if hasattr(self, '_m_page_point') else None

                _pos = self._io.pos()
                self._io.seek(128)
                self._m_page_point = self._io.read_u8le()
                self._io.seek(_pos)
                return self._m_page_point if hasattr(self, '_m_page_point') else None

            @property
            def backup_point(self):
                if hasattr(self, '_m_backup_point'):
                    return self._m_backup_point if hasattr(self, '_m_backup_point') else None

                _pos = self._io.pos()
                self._io.seek(80)
                self._m_backup_point = self._io.read_u8le()
                self._io.seek(_pos)
                return self._m_backup_point if hasattr(self, '_m_backup_point') else None

            @property
            def backup_count(self):
                if hasattr(self, '_m_backup_count'):
                    return self._m_backup_count if hasattr(self, '_m_backup_count') else None

                _pos = self._io.pos()
                self._io.seek(72)
                self._m_backup_count = self._io.read_u2le()
                self._io.seek(_pos)
                return self._m_backup_count if hasattr(self, '_m_backup_count') else None

            @property
            def version_count(self):
                if hasattr(self, '_m_version_count'):
                    return self._m_version_count if hasattr(self, '_m_version_count') else None

                _pos = self._io.pos()
                self._io.seek(144)
                self._m_version_count = self._io.read_u2le()
                self._io.seek(_pos)
                return self._m_version_count if hasattr(self, '_m_version_count') else None


        class Link(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.header = Mdb.Page.Link.PageHeader(self._io, self, self._root)
                self.cell_pointers = []
                i = 0
                while True:
                    _ = self._io.read_u2le()
                    self.cell_pointers.append(_)
                    if self._io.pos() == self.header.cell_pointers_list_length:
                        break
                    i += 1

            class PageHeader(KaitaiStruct):
                def __init__(self, _io, _parent=None, _root=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self._read()

                def _read(self):
                    self.page_index = self._io.read_bytes(8)
                    self.div1 = self._io.read_bytes(2)
                    self.type = self._io.read_bytes(1)
                    self.div2 = self._io.read_bytes(1)
                    self.cell_pointers_list_length = self._io.read_u2le()
                    self.last_cell_pointer_entry = self._io.read_u2le()


            class CellEntries(KaitaiStruct):
                def __init__(self, i, _io, _parent=None, _root=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self.i = i
                    self._read()

                def _read(self):
                    pass

                @property
                def cell_entry(self):
                    if hasattr(self, '_m_cell_entry'):
                        return self._m_cell_entry if hasattr(self, '_m_cell_entry') else None

                    _pos = self._io.pos()
                    self._io.seek(self._parent.cell_pointers[self.i])
                    self._m_cell_entry = self._io.read_bytes(6)
                    self._io.seek(_pos)
                    return self._m_cell_entry if hasattr(self, '_m_cell_entry') else None

                @property
                def cell_type(self):
                    if hasattr(self, '_m_cell_type'):
                        return self._m_cell_type if hasattr(self, '_m_cell_type') else None

                    _pos = self._io.pos()
                    self._io.seek((self._parent.cell_pointers[self.i] + 6))
                    self._m_cell_type = self._io.read_u2le()
                    self._io.seek(_pos)
                    return self._m_cell_type if hasattr(self, '_m_cell_type') else None


            @property
            def cell_entries(self):
                if hasattr(self, '_m_cell_entries'):
                    return self._m_cell_entries if hasattr(self, '_m_cell_entries') else None

                self._m_cell_entries = [None] * (len(self.cell_pointers))
                for i in range(len(self.cell_pointers)):
                    self._m_cell_entries[i] = Mdb.Page.Link.CellEntries(i, self._io, self, self._root)

                return self._m_cell_entries if hasattr(self, '_m_cell_entries') else None


        class Data(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.header = Mdb.Page.Data.PageHeader(self._io, self, self._root)
                self.cell_pointers = []
                i = 0
                while True:
                    _ = self._io.read_u2le()
                    self.cell_pointers.append(_)
                    if self._io.pos() == self.header.cell_pointers_list_length:
                        break
                    i += 1

            class PageHeader(KaitaiStruct):
                def __init__(self, _io, _parent=None, _root=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self._read()

                def _read(self):
                    self.page_index = self._io.read_bytes(8)
                    self.div1 = self._io.read_bytes(2)
                    self.type = self._io.read_bytes(1)
                    self.div2 = self._io.read_bytes(1)
                    self.cell_pointers_list_length = self._io.read_u2le()
                    self.last_cell_pointer_entry = self._io.read_u2le()


            class CellEntries(KaitaiStruct):
                def __init__(self, i, _io, _parent=None, _root=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self.i = i
                    self._read()

                def _read(self):
                    pass

                class Header(KaitaiStruct):
                    def __init__(self, _io, _parent=None, _root=None):
                        self._io = _io
                        self._parent = _parent
                        self._root = _root if _root else self
                        self._read()

                    def _read(self):
                        self.length = self._io.read_u4le()
                        self.div = self._io.read_bytes(4)
                        self.type = self._io.read_u2le()
                        self.table_point = self._io.read_u2be()
                        self.div3 = self._io.read_bytes(2)
                        self.index = self._io.read_u2be()

                    @property
                    def entry_offset(self):
                        if hasattr(self, '_m_entry_offset'):
                            return self._m_entry_offset if hasattr(self, '_m_entry_offset') else None

                        self._m_entry_offset = self._parent._parent.cell_pointers[self._parent.i]
                        return self._m_entry_offset if hasattr(self, '_m_entry_offset') else None


                class Entry(KaitaiStruct):
                    def __init__(self, _io, _parent=None, _root=None):
                        self._io = _io
                        self._parent = _parent
                        self._root = _root if _root else self
                        self._read()

                    def _read(self):
                        self._raw_entry_value = self._io.read_bytes(self._parent.entry_header.length)
                        _io__raw_entry_value = KaitaiStream(BytesIO(self._raw_entry_value))
                        self.entry_value = Mdb.Page.Data.CellEntries.Entry.Fb(_io__raw_entry_value, self, self._root)

                    class Fb(KaitaiStruct):
                        def __init__(self, _io, _parent=None, _root=None):
                            self._io = _io
                            self._parent = _parent
                            self._root = _root if _root else self
                            self._read()

                        def _read(self):
                            self.root = self._io.read_u4le()

                        class Pointer(KaitaiStruct):
                            def __init__(self, _io, _parent=None, _root=None):
                                self._io = _io
                                self._parent = _parent
                                self._root = _root if _root else self
                                self._read()

                            def _read(self):
                                self.pointer = self._io.read_u4le()


                        class Vtable(KaitaiStruct):
                            def __init__(self, _io, _parent=None, _root=None):
                                self._io = _io
                                self._parent = _parent
                                self._root = _root if _root else self
                                self._read()

                            def _read(self):
                                self.size_vtable = self._io.read_u2le()
                                self.size_vtabledata = self._io.read_u2le()
                                self.vtable_data_pointers = []
                                i = 0
                                while True:
                                    _ = self._io.read_u2le()
                                    self.vtable_data_pointers.append(_)
                                    if self._io.pos() == self._parent.root:
                                        break
                                    i += 1

                            @property
                            def vtable_data(self):
                                if hasattr(self, '_m_vtable_data'):
                                    return self._m_vtable_data if hasattr(self, '_m_vtable_data') else None

                                _pos = self._io.pos()
                                self._io.seek(self._parent.root)
                                self._m_vtable_data = self._io.read_bytes((self._parent._parent._parent.entry_header.length - self._parent.root))
                                self._io.seek(_pos)
                                return self._m_vtable_data if hasattr(self, '_m_vtable_data') else None


                        @property
                        def pvtable(self):
                            if hasattr(self, '_m_pvtable'):
                                return self._m_pvtable if hasattr(self, '_m_pvtable') else None

                            _pos = self._io.pos()
                            self._io.seek(self.root)
                            self._raw__m_pvtable = self._io.read_bytes(4)
                            _io__raw__m_pvtable = KaitaiStream(BytesIO(self._raw__m_pvtable))
                            self._m_pvtable = Mdb.Page.Data.CellEntries.Entry.Fb.Pointer(_io__raw__m_pvtable, self, self._root)
                            self._io.seek(_pos)
                            return self._m_pvtable if hasattr(self, '_m_pvtable') else None

                        @property
                        def vtable(self):
                            if hasattr(self, '_m_vtable'):
                                return self._m_vtable if hasattr(self, '_m_vtable') else None

                            _pos = self._io.pos()
                            self._io.seek((self.root - self.pvtable.pointer))
                            self._m_vtable = Mdb.Page.Data.CellEntries.Entry.Fb.Vtable(self._io, self, self._root)
                            self._io.seek(_pos)
                            return self._m_vtable if hasattr(self, '_m_vtable') else None



                class Table(KaitaiStruct):
                    def __init__(self, _io, _parent=None, _root=None):
                        self._io = _io
                        self._parent = _parent
                        self._root = _root if _root else self
                        self._read()

                    def _read(self):
                        self._raw_table_value = self._io.read_bytes(self._parent.entry_header.length)
                        _io__raw_table_value = KaitaiStream(BytesIO(self._raw_table_value))
                        self.table_value = Mdb.Page.Data.CellEntries.Table.Fb(_io__raw_table_value, self, self._root)

                    class Fb(KaitaiStruct):
                        def __init__(self, _io, _parent=None, _root=None):
                            self._io = _io
                            self._parent = _parent
                            self._root = _root if _root else self
                            self._read()

                        def _read(self):
                            self.root = self._io.read_u4le()

                        class Pointer(KaitaiStruct):
                            def __init__(self, _io, _parent=None, _root=None):
                                self._io = _io
                                self._parent = _parent
                                self._root = _root if _root else self
                                self._read()

                            def _read(self):
                                self.pointer = self._io.read_u4le()


                        class Vtable(KaitaiStruct):
                            def __init__(self, _io, _parent=None, _root=None):
                                self._io = _io
                                self._parent = _parent
                                self._root = _root if _root else self
                                self._read()

                            def _read(self):
                                self.size_vtable = self._io.read_u2le()
                                self.size_vtabledata = self._io.read_u2le()
                                self.posuid = self._io.read_u2le()
                                self.posid = self._io.read_u2le()
                                self.pos_e = self._io.read_u2le()
                                self.pos_entity_name = self._io.read_u2le()
                                self.pos_size_vector = self._io.read_u2le()
                                self.div = self._io.read_u2le()
                                self.div1 = self._io.read_u2le()
                                self.pos_vector = self._io.read_u2le()
                                self.pos_length_id = self._io.read_u2le()
                                self.pos_length_uid = self._io.read_u2le()


                        class Property(KaitaiStruct):
                            def __init__(self, i, _io, _parent=None, _root=None):
                                self._io = _io
                                self._parent = _parent
                                self._root = _root if _root else self
                                self.i = i
                                self._read()

                            def _read(self):
                                pass

                            class Property(KaitaiStruct):
                                def __init__(self, _io, _parent=None, _root=None):
                                    self._io = _io
                                    self._parent = _parent
                                    self._root = _root if _root else self
                                    self._read()

                                def _read(self):
                                    self.pvtable = self._io.read_s4le()

                                class PVtable(KaitaiStruct):
                                    def __init__(self, _io, _parent=None, _root=None):
                                        self._io = _io
                                        self._parent = _parent
                                        self._root = _root if _root else self
                                        self._read()

                                    def _read(self):
                                        pass


                                class Vtable(KaitaiStruct):
                                    def __init__(self, _io, _parent=None, _root=None):
                                        self._io = _io
                                        self._parent = _parent
                                        self._root = _root if _root else self
                                        self._read()

                                    def _read(self):
                                        self.size_vtable = self._io.read_u2le()
                                        self.size_vtabledata = self._io.read_u2le()
                                        self.posuid = self._io.read_u2le()
                                        self.posid = self._io.read_u2le()
                                        self.pos_e = self._io.read_u2le()
                                        self.div = self._io.read_u2le()
                                        self.div1 = self._io.read_u2le()
                                        self.div3 = self._io.read_u2le()
                                        self.pos_property_name = self._io.read_u2le()
                                        self.pos_c = self._io.read_u2le()
                                        self.pos_b = self._io.read_u2le()
                                        self.div4 = self._io.read_u2le()
                                        self.pos_property_name_length = self._io.read_u2le()


                                @property
                                def point_property_name(self):
                                    if hasattr(self, '_m_point_property_name'):
                                        return self._m_point_property_name if hasattr(self, '_m_point_property_name') else None

                                    _pos = self._io.pos()
                                    self._io.seek(((((self._parent._parent.root + self._parent._parent.vtable.size_vtabledata) + (4 * (self._parent.i + 1))) + self._parent._parent.prop_pointers[self._parent.i]) + self.vtable.pos_property_name))
                                    self._m_point_property_name = self._io.read_u4le()
                                    self._io.seek(_pos)
                                    return self._m_point_property_name if hasattr(self, '_m_point_property_name') else None

                                @property
                                def property_name(self):
                                    if hasattr(self, '_m_property_name'):
                                        return self._m_property_name if hasattr(self, '_m_property_name') else None

                                    _pos = self._io.pos()
                                    self._io.seek((((((self._parent._parent.root + self._parent._parent.vtable.size_vtabledata) + (4 * (self._parent.i + 1))) + self._parent._parent.prop_pointers[self._parent.i]) + self.vtable.size_vtabledata) + self.point_property_name))
                                    self._m_property_name = (self._io.read_bytes(self.length_property_name)).decode(u"UTF-8")
                                    self._io.seek(_pos)
                                    return self._m_property_name if hasattr(self, '_m_property_name') else None

                                @property
                                def vtable(self):
                                    if hasattr(self, '_m_vtable'):
                                        return self._m_vtable if hasattr(self, '_m_vtable') else None

                                    _pos = self._io.pos()
                                    self._io.seek(((((self._parent._parent.root + self._parent._parent.vtable.size_vtabledata) + (4 * (self._parent.i + 1))) + self._parent._parent.prop_pointers[self._parent.i]) - self.pvtable))
                                    self._m_vtable = Mdb.Page.Data.CellEntries.Table.Fb.Property.Property.Vtable(self._io, self, self._root)
                                    self._io.seek(_pos)
                                    return self._m_vtable if hasattr(self, '_m_vtable') else None

                                @property
                                def length_property_name(self):
                                    if hasattr(self, '_m_length_property_name'):
                                        return self._m_length_property_name if hasattr(self, '_m_length_property_name') else None

                                    _pos = self._io.pos()
                                    self._io.seek(((((((self._parent._parent.root + self._parent._parent.vtable.size_vtabledata) + (4 * (self._parent.i + 1))) + self._parent._parent.prop_pointers[self._parent.i]) + self.vtable.size_vtabledata) + self.point_property_name) - 4))
                                    self._m_length_property_name = self._io.read_u4le()
                                    self._io.seek(_pos)
                                    return self._m_length_property_name if hasattr(self, '_m_length_property_name') else None

                                @property
                                def id(self):
                                    if hasattr(self, '_m_id'):
                                        return self._m_id if hasattr(self, '_m_id') else None

                                    _pos = self._io.pos()
                                    self._io.seek(((((self._parent._parent.root + self._parent._parent.vtable.size_vtabledata) + (4 * (self._parent.i + 1))) + self._parent._parent.prop_pointers[self._parent.i]) + self.vtable.posid))
                                    self._m_id = self._io.read_u4le()
                                    self._io.seek(_pos)
                                    return self._m_id if hasattr(self, '_m_id') else None

                                @property
                                def uid(self):
                                    if hasattr(self, '_m_uid'):
                                        return self._m_uid if hasattr(self, '_m_uid') else None

                                    _pos = self._io.pos()
                                    self._io.seek(((((self._parent._parent.root + self._parent._parent.vtable.size_vtabledata) + (4 * (self._parent.i + 1))) + self._parent._parent.prop_pointers[self._parent.i]) + self.vtable.posuid))
                                    self._m_uid = self._io.read_u8le()
                                    self._io.seek(_pos)
                                    return self._m_uid if hasattr(self, '_m_uid') else None


                            @property
                            def entry_property(self):
                                if hasattr(self, '_m_entry_property'):
                                    return self._m_entry_property if hasattr(self, '_m_entry_property') else None

                                _pos = self._io.pos()
                                self._io.seek((((self._parent.root + self._parent.vtable.size_vtabledata) + (4 * (self.i + 1))) + self._parent.prop_pointers[self.i]))
                                self._m_entry_property = Mdb.Page.Data.CellEntries.Table.Fb.Property.Property(self._io, self, self._root)
                                self._io.seek(_pos)
                                return self._m_entry_property if hasattr(self, '_m_entry_property') else None


                        @property
                        def length_entity_name(self):
                            if hasattr(self, '_m_length_entity_name'):
                                return self._m_length_entity_name if hasattr(self, '_m_length_entity_name') else None

                            _pos = self._io.pos()
                            self._io.seek((((self.root + self.vtable.size_vtabledata) + self.point_entity_name) - 4))
                            self._m_length_entity_name = self._io.read_u4le()
                            self._io.seek(_pos)
                            return self._m_length_entity_name if hasattr(self, '_m_length_entity_name') else None

                        @property
                        def point_entity_name(self):
                            if hasattr(self, '_m_point_entity_name'):
                                return self._m_point_entity_name if hasattr(self, '_m_point_entity_name') else None

                            _pos = self._io.pos()
                            self._io.seek((self.root + self.vtable.pos_entity_name))
                            self._m_point_entity_name = self._io.read_u4le()
                            self._io.seek(_pos)
                            return self._m_point_entity_name if hasattr(self, '_m_point_entity_name') else None

                        @property
                        def pvector(self):
                            if hasattr(self, '_m_pvector'):
                                return self._m_pvector if hasattr(self, '_m_pvector') else None

                            _pos = self._io.pos()
                            self._io.seek((self.root + self.vtable.pos_vector))
                            self._m_pvector = self._io.read_u4le()
                            self._io.seek(_pos)
                            return self._m_pvector if hasattr(self, '_m_pvector') else None

                        @property
                        def pvtable(self):
                            if hasattr(self, '_m_pvtable'):
                                return self._m_pvtable if hasattr(self, '_m_pvtable') else None

                            _pos = self._io.pos()
                            self._io.seek(self.root)
                            self._raw__m_pvtable = self._io.read_bytes(4)
                            _io__raw__m_pvtable = KaitaiStream(BytesIO(self._raw__m_pvtable))
                            self._m_pvtable = Mdb.Page.Data.CellEntries.Table.Fb.Pointer(_io__raw__m_pvtable, self, self._root)
                            self._io.seek(_pos)
                            return self._m_pvtable if hasattr(self, '_m_pvtable') else None

                        @property
                        def vtable(self):
                            if hasattr(self, '_m_vtable'):
                                return self._m_vtable if hasattr(self, '_m_vtable') else None

                            _pos = self._io.pos()
                            self._io.seek((self.root - self.pvtable.pointer))
                            self._m_vtable = Mdb.Page.Data.CellEntries.Table.Fb.Vtable(self._io, self, self._root)
                            self._io.seek(_pos)
                            return self._m_vtable if hasattr(self, '_m_vtable') else None

                        @property
                        def id(self):
                            if hasattr(self, '_m_id'):
                                return self._m_id if hasattr(self, '_m_id') else None

                            _pos = self._io.pos()
                            self._io.seek((self.root + self.vtable.posid))
                            self._m_id = self._io.read_u4le()
                            self._io.seek(_pos)
                            return self._m_id if hasattr(self, '_m_id') else None

                        @property
                        def uid(self):
                            if hasattr(self, '_m_uid'):
                                return self._m_uid if hasattr(self, '_m_uid') else None

                            _pos = self._io.pos()
                            self._io.seek((self.root + self.vtable.posuid))
                            self._m_uid = self._io.read_u8le()
                            self._io.seek(_pos)
                            return self._m_uid if hasattr(self, '_m_uid') else None

                        @property
                        def entity_name(self):
                            if hasattr(self, '_m_entity_name'):
                                return self._m_entity_name if hasattr(self, '_m_entity_name') else None

                            _pos = self._io.pos()
                            self._io.seek(((self.root + self.vtable.size_vtabledata) + self.point_entity_name))
                            self._m_entity_name = (self._io.read_bytes(self.length_entity_name)).decode(u"UTF-8")
                            self._io.seek(_pos)
                            return self._m_entity_name if hasattr(self, '_m_entity_name') else None

                        @property
                        def prop_pointers(self):
                            if hasattr(self, '_m_prop_pointers'):
                                return self._m_prop_pointers if hasattr(self, '_m_prop_pointers') else None

                            _pos = self._io.pos()
                            self._io.seek(((self.root + self.vtable.size_vtabledata) + 4))
                            self._m_prop_pointers = [None] * (self.number_of_properties)
                            for i in range(self.number_of_properties):
                                self._m_prop_pointers[i] = self._io.read_u4le()

                            self._io.seek(_pos)
                            return self._m_prop_pointers if hasattr(self, '_m_prop_pointers') else None

                        @property
                        def properties(self):
                            if hasattr(self, '_m_properties'):
                                return self._m_properties if hasattr(self, '_m_properties') else None

                            self._m_properties = [None] * (self.number_of_properties)
                            for i in range(self.number_of_properties):
                                self._m_properties[i] = Mdb.Page.Data.CellEntries.Table.Fb.Property(i, self._io, self, self._root)

                            return self._m_properties if hasattr(self, '_m_properties') else None

                        @property
                        def number_of_properties(self):
                            if hasattr(self, '_m_number_of_properties'):
                                return self._m_number_of_properties if hasattr(self, '_m_number_of_properties') else None

                            _pos = self._io.pos()
                            self._io.seek((self.root + self.vtable.size_vtabledata))
                            self._m_number_of_properties = self._io.read_u4le()
                            self._io.seek(_pos)
                            return self._m_number_of_properties if hasattr(self, '_m_number_of_properties') else None



                @property
                def entry_header(self):
                    if hasattr(self, '_m_entry_header'):
                        return self._m_entry_header if hasattr(self, '_m_entry_header') else None

                    _pos = self._io.pos()
                    self._io.seek(self._parent.cell_pointers[self.i])
                    self._m_entry_header = Mdb.Page.Data.CellEntries.Header(self._io, self, self._root)
                    self._io.seek(_pos)
                    return self._m_entry_header if hasattr(self, '_m_entry_header') else None

                @property
                def cell_entry(self):
                    if hasattr(self, '_m_cell_entry'):
                        return self._m_cell_entry if hasattr(self, '_m_cell_entry') else None

                    _pos = self._io.pos()
                    self._io.seek((self._parent.cell_pointers[self.i] + 16))
                    _on = self.entry_header.type
                    if _on == 0:
                        self._m_cell_entry = Mdb.Page.Data.CellEntries.Table(self._io, self, self._root)
                    else:
                        self._m_cell_entry = Mdb.Page.Data.CellEntries.Entry(self._io, self, self._root)
                    self._io.seek(_pos)
                    return self._m_cell_entry if hasattr(self, '_m_cell_entry') else None


            @property
            def cell_entries(self):
                if hasattr(self, '_m_cell_entries'):
                    return self._m_cell_entries if hasattr(self, '_m_cell_entries') else None

                self._m_cell_entries = [None] * (len(self.cell_pointers))
                for i in range(len(self.cell_pointers)):
                    self._m_cell_entries[i] = Mdb.Page.Data.CellEntries(i, self._io, self, self._root)

                return self._m_cell_entries if hasattr(self, '_m_cell_entries') else None


        @property
        def page_type(self):
            if hasattr(self, '_m_page_type'):
                return self._m_page_type if hasattr(self, '_m_page_type') else None

            _pos = self._io.pos()
            self._io.seek(10)
            self._m_page_type = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_page_type if hasattr(self, '_m_page_type') else None



