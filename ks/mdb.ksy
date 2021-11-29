meta:
  id: mdb
  file-extension: mdb
  endian: le          # Little ENDIAN 
seq:
  # DB consists of PAGES with a size of 4096 Bytes (4k) or 0x1000 Bytes. 
  - id: pages
    type: page
    size: 4096
    repeat: eos
types:
  page:
    instances:
      page_type:
        pos: 0xA
        type: u1
    seq:
      # FIND the TYPE of PAGES in the DB
      - id: page
        type:
          switch-on: page_type
          cases:
                8: head
                2: data
                1: link
    types:
      # Begin HEADER PAGE, that have information about the first page (root page). there is two HEADER PAGES, the PAGE-Count know which is the more current
      head:
        instances:
          backup_count:
            type: u2
            pos: 0x48
            terminator: 0
          backup_point:
            type: u8
            pos: 0x50
          page_count:
            type: u2
            pos: 0x78
            terminator: 0
          page_point:
            type: u8
            pos: 0x80
          version_count:
            type: u2
            pos: 0x90
            terminator: 0
        seq:
          - id: header
            size: 16
      # Begin LINK page, that Page have information about PAGE INDEX stored, to point the the NEXT LINK-PAGE or to a DATA-PAGE
      link:
        seq:
          # first 16 Byte of a page is the HEADER of a PAGE
          - id: header
            type: page_header
          - id: cell_pointers
            type: u2
            repeat: until
            repeat-until: _io.pos == header.cell_pointers_list_length
        instances:
          # table of contents of the PAGE and the cell pointer pointed to the begin of a CELL in that PAGE
          # at the begin of a page (after the header), there is placed the table of contents with CELL pointers to point to the CELL ENTRIES in that page. The CELL ENTRIES begin at the end of the page and grow to the begin of the page, the CELL pointers grow toward to the end of the Page
          # [CELL HEADER][table of content -->][unallocated memory][<---][CELL ENTRY3][CELL ENTRY2][CELL ENTRY1]
          cell_entries:
            type: cell_entries(_index) # <= pass `_index` into cell_entries to repeat it for all cellpointers that exits in the table of contents
            repeat: expr
            repeat-expr: cell_pointers.size
        types:
          page_header:
            seq:
              - id: page_index
                size: 8
              - id: div1
                size: 2
              - id: type
                size: 1
              - id: div2
                size: 1
              - id: cell_pointers_list_length # length of the table of contents 
                type: u2
              - id: last_cell_pointer_entry # last CELL Entry in the table of contents 
                type: u2
          cell_entries:
            params:
              - id: i               # => receive `_index` as `i` here
                type: u2
            instances:
              cell_entry:
                pos: _parent.cell_pointers[i]
                size: 6
              cell_type:
                pos: _parent.cell_pointers[i] + 6
                type: u2
      # Begin DATA page, that Page have the tables or entry for tables stored. 
      data:
        seq:
          # first 16 Byte of a page is the HEADER of a PAGE
          - id: header
            type: page_header
          - id: cell_pointers
            type: u2
            repeat: until
            repeat-until: _io.pos == header.cell_pointers_list_length
            #repeat-until: _ == header.last_cell_pointer_entry
        instances:
          # table of contents of the PAGE and the cell pointer pointed to the begin of a CELL in that PAGE
          # at the begin of a page (after the header), there is placed the table of contents with CELL pointers to point to the CELL ENTRIES in that page. The CELL ENTRIES begin at the end of the page and grow to the begin of the page, the CELL pointers grow toward to the end of the Page
          # [CELL HEADER][table of content -->][unallocated memory][<---][CELL ENTRY3][CELL ENTRY2][CELL ENTRY1]
          cell_entries:
            type: cell_entries(_index) # <= pass `_index` into cell_entries to repeat it for all cellpointers that exits in the table of contents
            repeat: expr
            repeat-expr: cell_pointers.size
            
        types:
          page_header:
            seq:
              - id: page_index
                size: 8
              - id: div1
                size: 2
              - id: type
                size: 1
              - id: div2
                size: 1
              - id: cell_pointers_list_length
                type: u2
              - id: last_cell_pointer_entry
                type: u2
          cell_entries:
            params:
              - id: i               # => receive `_index` as `i` here
                type: u2
            instances:
              entry_header:
                pos: _parent.cell_pointers[i]
                type: header
            # value of a cell entry could be a entry for a table or a table, excepted the table[0], that is the '.default' table with information about the Box
              cell_entry:
                pos: _parent.cell_pointers[i] + 16
                type:
                  switch-on: entry_header.type
                  cases:
                        0: table
                        _: entry
            types:
              header:    
                seq: 
                  - id: length
                    type: u4
                  - id: div
                    size: 4
                  - id: type
                    type: u2
                  #- id: div2
                  #  size: 1
                  - id: table_point
                    type: u2be
                  - id: div3
                    size: 2
                  - id: index
                    type: u2be
                instances:
                  entry_offset:
                    value: _parent._parent.cell_pointers[_parent.i]
              # Begin ENTRIES of a VALUE
              entry:
                seq:
                  - id: entry_value
                    size: _parent.entry_header.length
                    type: fb
                types:
                # Begin FLATBUFFER structures for Values (entries of a table)
                  fb:
                    seq:
                      - id: header      # pointer to root
                        type: u4
                    instances:
                      # pointer to begin of ENTRY VTABLE
                      root:
                        pos: header
                        size: 4
                        type: pointer
                      # Begin VTABLE of ENTITIES
                      vtable:
                        pos: header - root.pointer
                        type: vtable
                    types:
                      pointer:
                        seq:
                          - id: pointer
                            type: u4
                      # VTABLE of each ENTRY - sequences of Bytes which VTABLE Information about the ENTRY - div means unkown information
                      vtable:
                        seq:
                          - id: size_vtable
                            type: u2
                          - id: size_vtabledata
                            type: u2
                          - id: vtable_data_pointers
                            type: u2
                            #size: 2
                            #terminator: 0
                            repeat: until
                            repeat-until: _io.pos == _parent.header
                      # the vtable of entries should be analyzed at the phyton programm, because it could be that entries did not inputed in an order
                      # that will regulatde with the offset for the vtable data (VTABLE_DATA_POINTERS).
                      # with kaitai struct it is currently not possible to parse dynamic length 
                      # e.g. an vtable data could be 0x1000 0000 or 0x0200 0000 00 - the length of the bytes are needed to restruct the Data, with an terminator: 0 the length will be faulty
                      # 
                        instances:
                          vtable_data:
                            pos: _parent.header 
                            size: _parent._parent._parent.entry_header.length - _parent.header 
                              
                              
                              
              # Begin TABLES 
              table:
                seq:
                  - id: table_value
                    size: _parent.entry_header.length
                    type: fb
                types:
                  # Begin FLATBUFFER structures for ENTITIES (Tables)
                  fb:
                    seq:
                      - id: header  # pointer to root
                        type: u4
                    instances:
                      # pointer to begin of ENTITY VTABLE
                      root:
                        pos: header
                        size: 4
                        type: pointer
                      # Begin VTABLE of ENTITIES
                      vtable:
                        pos: header - root.pointer
                        type: vtable
                      # where ENTITY UID is placed
                      uid:
                        pos: header + vtable.posuid
                        type: u8
                      # where ENTITY ID is placed
                      id:
                        pos: header + vtable.posid
                        type: u4
                      # the offset of the vectors where information placed about the number of PROPERTIES (columns)
                      pvector:
                        pos: header + vtable.pos_vector
                        #pos: root + vtable.pos_size_vector
                        type: u4
                      # calculate the offset where the ENTITY name is placed
                      point_entity_name:
                        pos: header + vtable.pos_entity_name
                        type: u4
                      length_entity_name:
                        pos: header + vtable.size_vtabledata + point_entity_name - 4
                        type: u4
                      # Name of the table
                      entity_name:
                        pos: header + vtable.size_vtabledata + point_entity_name
                        size: length_entity_name
                        type: str
                        encoding: UTF-8
                      # read the numbers of Properties (columns) of the ENTITY (table)
                      number_of_properties:
                        pos: header + vtable.size_vtabledata #‚+ pvector - 1
                        #pos: root + 4 + pvector 
                        type: u4
                      # parse the next i * 4 Bytes, i is the number of PROPERTIES (columns)
                      prop_pointers:
                        pos: header + vtable.size_vtabledata + 4
                        #pos: root + 4 + pvector + 4
                        type: u4
                        repeat: expr
                        repeat-expr: number_of_properties 
                      properties:
                        type: property(_index) # <= pass `_index` into property
                        repeat: expr
                        repeat-expr: number_of_properties 
                    types:
                      pointer:
                        seq:
                          - id: pointer
                            type: u4
                      # VTABLE of each ENTITY - sequences of Bytes which VTABLE Information about the ENTITY - div means unknown information
                      vtable:
                        seq:
                          - id: size_vtable
                            type: u2
                          - id: size_vtabledata
                            type: u2
                          - id: posuid
                            type: u2
                          - id: posid
                            type: u2
                          - id: pos_e
                            type: u2
                          - id: pos_entity_name
                            type: u2
                          - id: pos_size_vector
                            type: u2
                          - id: div
                            type: u2
                          - id: div1
                            type: u2
                          - id: pos_vector
                            type: u2
                          - id: pos_length_id
                            type: u2
                          - id: pos_length_uid
                            type: u2
                      property:
                          params:
                          - id: i               # => receive `_index` as `i` here
                            type: u2
                          instances:
                            # calculated the offset of the ENTITY PROPERTIES based of the PROPERTY POINTERS (prob_pointers)
                            entry_property:
                              pos: _parent.header + _parent.vtable.size_vtabledata + 4 * (i+1) + _parent.prop_pointers[i]
                              type: property
                              #if: i > 0
                          types:
                            property:
                              seq:
                                - id: root
                                  type: s4le
                              instances:
                                # VTABLE Properties with UID, ID, NAME
                                vtable:
                                  pos: (_parent._parent.header + _parent._parent.vtable.size_vtabledata + 4 * (_parent.i+1) + _parent._parent.prop_pointers[_parent.i] - root)
                                  type: vtable
                                  #if: pvtable >= 0
                                uid:
                                  pos: (_parent._parent.header + _parent._parent.vtable.size_vtabledata + 4 * (_parent.i+1) + _parent._parent.prop_pointers[_parent.i] + vtable.posuid)
                                  type: u8
                                  #if: _parent.i > 0
                                id: 
                                  pos: (_parent._parent.header + _parent._parent.vtable.size_vtabledata + 4 * (_parent.i+1) + _parent._parent.prop_pointers[_parent.i] + vtable.posid)
                                  type: u4
                                  #if: _parent.i > 0
                                # Sum the bytes from to two pointers to the offset of the property name
                                point_property_name:
                                  pos: (_parent._parent.header + _parent._parent.vtable.size_vtabledata + 4 * (_parent.i+1) + _parent._parent.prop_pointers[_parent.i] + vtable.pos_property_name)
                                  type: u4
                                  #if: _parent.i > 0
                                # find the length of the string 4 Bytes before the string starts
                                length_property_name:
                                  pos: (_parent._parent.header + _parent._parent.vtable.size_vtabledata + 4 * (_parent.i+1) + _parent._parent.prop_pointers[_parent.i] + vtable.size_vtabledata + point_property_name) - 4
                                  type: u4
                                  #if: _parent.i > 0
                                property_name:
                                  pos: (_parent._parent.header + _parent._parent.vtable.size_vtabledata + 4 * (_parent.i+1) + _parent._parent.prop_pointers[_parent.i] + vtable.size_vtabledata + point_property_name)
                                  size: length_property_name
                                  type: str
                                  encoding: UTF-8
                                  #if: _parent.i > 0
                              types:
                                # to find the VTABLE point at the data section (begin of VTABLE structure)
                                p_vtable:
                                  -seq:
                                    - id: pointer
                                      type: u4
                                # VTABLE sequence of PROPERTIES div means unknown DATA ... 
                                vtable:
                                  seq:
                                  - id: size_vtable
                                    type: u2
                                  - id: size_vtabledata
                                    type: u2
                                  - id: posuid
                                    type: u2
                                  - id: posid
                                    type: u2
                                  - id: pos_e
                                    type: u2
                                  - id: div
                                    type: u2
                                  - id: div1
                                    type: u2
                                  - id: div3
                                    type: u2
                                  - id: pos_property_name
                                    type: u2
                                  - id: pos_c
                                    type: u2
                                  - id: pos_b
                                    type: u2
                                  - id: div4
                                    type: u2
                                  - id: pos_property_name_length
                                    type: u2
                              