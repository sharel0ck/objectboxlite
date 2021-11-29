#! /usr/local/bin/python3
import sys, argparse, datetime, json, struct
from cmd import Cmd
from ks.mdb import *


# objectbox expects date timestamp in milliseconds since UNIX epoch
def now_ms() -> int:
    seconds: float = datetime.datetime.utcnow().timestamp()
    return round(seconds * 1000)

def format_date(timestamp_ms: int) -> str:
    return "" if timestamp_ms == 0 else str(datetime.datetime.fromtimestamp(timestamp_ms / 1000))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", dest="file",
                        help="path of ObjectBox database file")
    #parser.add_argument("-k", "--knownPlaintext", dest="np", help="known plaintext, e.g. '78384 END'")
    options = parser.parse_args()
    return options

def get_data_pages(temp, page: int):
    # recursive function to find all data pages at the tree ...
    #temp = []
    if f.pages[page].page_type == 2:
        #print("index of data page is: " + str(page))
        temp.append(page)
        return 1
    else:
        if f.pages[page].page_type == 1:
            for item in list(f.pages[page].page.cell_entries):
                #print(str(int.from_bytes(f.pages[page].page.cell_entries[item.i].cell_entry, byteorder='little')))
                get_data_pages(temp, int.from_bytes(f.pages[page].page.cell_entries[item.i].cell_entry, byteorder='little'))
                #if f.pages[page].page.cell_entries[item.i].cell_type == 8 or f.pages[page].page.cell_entries[item.i].cell_type == 0:
                   #get_data_pages(temp[8], int.from_bytes(f.pages[page].page.cell_entries[item.i].cell_entry, byteorder='little'))
                #if f.pages[page].page.cell_entries[item.i].cell_type == 12:
                    #get_data_pages(temp[12], int.from_bytes(f.pages[page].page.cell_entries[item.i].cell_entry, byteorder='little'))
    #print(temp)

def printJsonReadable(obj):
    print(json.dumps(obj, indent=2))

class ObjectBoxLite(Cmd):
    prompt = "> "
    # list with the index numbers for data pages in the file
    data_pages = []
    #data_pages[8] = []
    #data_pages[12] = []
    objectboxlite_data = dict()
    objectboxlite_unknown_data = list()

    def __init__(self):
        # find all data pages in the tree
        if f.pages[0].page.page_count >= f.pages[1].page.page_count and f.pages[0].page.version_count >= f.pages[1].page.version_count:
            get_data_pages(self.data_pages, f.pages[0].page.page_point)
            
        if f.pages[1].page.page_count >= f.pages[0].page.page_count and f.pages[1].page.version_count >= f.pages[0].page.version_count:
            get_data_pages(self.data_pages, f.pages[1].page.page_point)
            
        
        # if there are no pages found to enter, program will exit
        if len(self.data_pages) == 0:
            print("Error: 'Could not find a page to start - DB could be incompatible'")
            sys.exit(0)

        #for i in data_pages:
            #print("data page found at index: " + str(i))   

        # get all TABLE-ENTRIES and ENTRIES-for-a-TABLE from all items in data_pages that are found and store it in the dict OBJECTBOXLITE_DATA 

        for page in self.data_pages:
            
            # get all entries for that page
            for entry in list(f.pages[page].page.cell_entries):
                # TABLE entries | skip table with index 0, because that is the table with ".default" string 
                # and some information about the Database - that currently is not investigated further
                if entry.entry_header.type == 0 and entry.entry_header.index > 0:
                    table_name = entry.cell_entry.table_value.entity_name
                    table_uid = entry.cell_entry.table_value.uid
                    table_id = entry.cell_entry.table_value.id
                    properties = {}
                    for property in list(entry.cell_entry.table_value.properties):
                        properties[property.i] = {}
                        property_name = property.entry_property.property_name
                        property_uid = property.entry_property.uid
                        property_id = property.entry_property.id
                        properties[property.i]["property"] = property_name
                        properties[property.i]["UID"] = property_uid
                        properties[property.i]["ID"] = property_id
                    self.objectboxlite_data[table_name] = {}
                    self.objectboxlite_data[table_name]["UID"] = table_uid
                    self.objectboxlite_data[table_name]["ID"] = table_id
                    self.objectboxlite_data[table_name]["mapping"] = (entry.entry_header.index * 4)
                    self.objectboxlite_data[table_name]["Properties"] = properties
                    self.objectboxlite_data[table_name]["Entries"] = {}

                # entries for a TABLE    
                if entry.entry_header.type != 0:
                    mapping = entry.entry_header.table_point
                    entries = {}
                    # rebuilt VTABLE of a ENTRY, taking into account the offset of the pointers that determine the sequence
                    # the sequence of VTABLE Data entries determined of the offsets for the DATA_Pointers and a length are not stored
                    # iterate each byte at the VTABLE DATA area, begin at the offset from the first pointer till the end of VTABLE DATA section
                    # the last vtable data entry determinate at the end of the VTABLE DATA section, all other determinate at the begin of the next 
                    # vtable data entry
                    entry_offset = entry.entry_header.entry_offset
                    
                
                    dict_vtable_data = {}
                    index = 0
                    try: #  try to read the entry - if anything wrong print a warning on which Offset is not readable
                        for i in range(0,len(entry.cell_entry.entry_value.vtable.vtable_data_pointers)):
                            offset = entry.cell_entry.entry_value.vtable.vtable_data_pointers[i]
                            vtable_data = entry.cell_entry.entry_value.vtable.vtable_data[offset:entry.cell_entry.entry_value.vtable.size_vtabledata]
                            # in bytes for float numbers could be a \x00 in, adjust to determinate at \x00\x00 and the next byte (from next pointer) are 
                            # not a \x00 Byte
                            # var i iterate the bytes from offset begin to the end of VTABLE_DATA section, if i found a \x00 and i + 1 too and i + 2 is not
                            # a \x00 Bytes, that means that the next pointer are found
                            # for the last entry at the VTABLE_DATA section i + 1 should be a \x00 Byte and i + 2 are the end of the bytes that should be
                            # iterated
                            
                            #print(len(entry.cell_entry.entry_value.vtable.vtable_data[offset:entry.cell_entry.entry_value.vtable.size_vtabledata]))

                            for i in range(0,len(vtable_data)):
                                #end = end + 1
                                if (vtable_data[i+1] == 0 and i+2 == len(vtable_data)):
                                    end = i + 2 
                                    dict_vtable_data[index] = {}
                                    dict_vtable_data[index]["i"] = index
                                    dict_vtable_data[index]["data_value"] = vtable_data[:end]
                                    dict_vtable_data[index]["string_value"] = ""
                                    dict_vtable_data[index]["size"] = end
                                    index = index + 1
                                    break
                                if (vtable_data[i] == 0 and vtable_data[i+1] == 0 and vtable_data[i+2] !=0 and i+1 != entry.cell_entry.entry_value.vtable.size_vtabledata):
                                    end = i + 1
                                    #rebuilt_vtable.append(vtable_data[begin:end])
                                    dict_vtable_data[index] = {}
                                    dict_vtable_data[index]["i"] = index
                                    dict_vtable_data[index]["data_value"] = vtable_data[:end]
                                    dict_vtable_data[index]["string_value"] = ""
                                    dict_vtable_data[index]["size"] = end
                                    index = index + 1
                                    break
                            #print(vtable_data[i])
                    except EOFError:
                        print("Warning: Found unreadable entry on Page '%i' and page-offset '%s'" %(page, hex(entry_offset)))
                        pass
                    # check VTABLE DATA of Strings - Note: for string the DATA store a pointer to the string after the DATA area 
                    # Strings and Values will store in a dict
                    # if a VTABLE DATA entry is a String, the string will be stored in the dict field string_value, if not the VTABLE DATA entry is a Value and will leave in the data_value field

                    for item in dict_vtable_data:
                        #print(dict_vtable_data)
                        
                        # offset depense at the sequence of the VTABLE Pointers and determined the sequence of the data for the columns
                        offset = offset = entry.cell_entry.entry_value.vtable.vtable_data_pointers[item]
                        # at that point a data_value could be a value that are stored in the VTABLE DATA section or a pointer to a STRING that is stored after
                        # VTABLE DATA section
                        string_offset = int.from_bytes(dict_vtable_data[item]["data_value"], "little")  
                        #print(offset)
                        #print(entry.cell_entry.entry_value.vtable.vtable_data[offset + string_offset:offset + string_offset + 1])

                        # check if the data_value is a STRING pointer, if yes calculate string_size and read string bytes and remove value at data_value/size field
                        # that shows that a string was found later in the program
                        #
                        # else string the length of Values, that could be Numbers or timestamp later
                        # leave it in the data_value field and adjust the size field-
                        if int.from_bytes(entry.cell_entry.entry_value.vtable.vtable_data[offset + string_offset:offset + string_offset + 1], "little") != 0 and item != 0:
                            string_size = int.from_bytes(entry.cell_entry.entry_value.vtable.vtable_data[offset + string_offset : offset + string_offset + 4], "little") 
                            dict_vtable_data[item]["string_size"] = string_size
                            #print(entry.cell_entry.entry_value.vtable.vtable_data[offset + string_offset + 4 : offset + string_offset + 4 + string_size ])
                            dict_vtable_data[item]["string_value"] = entry.cell_entry.entry_value.vtable.vtable_data[offset + string_offset + 4 : offset + string_offset + 4 + string_size ]
                            dict_vtable_data[item]["data_value"] = ""
                            dict_vtable_data[item]["size"] = ""
                        else:
                            if dict_vtable_data[item]["i"] != 0:
                                # remove the \x00 Bytes from the end of 'data_value'
                                #for byte in dict_vtable_data[item]["data_value"]:
                                #    print(byte)
                                #dict_vtable_data[item]["data_value"] = dict_vtable_data[item]["data_value"].split(b'\x00\x00')[0]
                                dict_vtable_data[item]["data_value"] = dict_vtable_data[item]["data_value"].rstrip(b'\x00')
                                dict_vtable_data[item]["size"] = len(dict_vtable_data[item]["data_value"])
                            #print(bytes(dict_vtable_data[item]["data_value"]))

                    # reconstruct the DATA Values that are numbers and store it in the gloabal dict
                    # strings will be put into global dict directly
                    
                    for item in dict_vtable_data:
                        entries[dict_vtable_data[item]["i"]] = {}
                        
                        # the first item in a VTABLE DATA is the ID / INDEX
                        if dict_vtable_data[item]["i"] == 0: 
                            entries[dict_vtable_data[item]["i"]]["id"] = int.from_bytes(dict_vtable_data[item]["data_value"], byteorder='little')
                        
                        # if string_value has a value, than decode Bytes an but it into Entries dict section
                        if dict_vtable_data[item]["string_value"] != "":
                            entries[dict_vtable_data[item]["i"]]["value"] = dict_vtable_data[item]["string_value"].decode("utf-8")

                        # if data_value have an value, then reconstruct the value from bytes
                        if dict_vtable_data[item]["data_value"] != "":
                            
                            # value with size smaller then 3 could be INTEGER, program try to unpack into INTEGER from Bytes
                            if int(dict_vtable_data[item]["size"]) <= 3:
                                try:
                                    entries[dict_vtable_data[item]["i"]]["value"] =  int.from_bytes(dict_vtable_data[item]["data_value"], byteorder='little', signed=False)
                                except AttributeError:
                                    pass
                            # value with size 4 could be unsined INTEGER, program try to unpack into a unsigned INTEGER and store it at ENTRY value
                            if int(dict_vtable_data[item]["size"]) == 4:
                                try:
                                    entries[dict_vtable_data[item]["i"]]["value"] =  struct.unpack('I', dict_vtable_data[item]["data_value"])
                                except AttributeError:
                                    pass
                            # value with size 6 could be a timestamp, program try to unpack into a timestamp and store it at ENTRY value
                            # timestamp consists 6 Bytes from left there are 2 Bytes short integer as header and the 4 Bytes are the timestamp number as
                            # long (little endian Python Type)
                            if int(dict_vtable_data[item]["size"]) == 6:
                                try:
                                    #print(dict_vtable_data[item]["data_value"].hex())
                                    #entries[dict_vtable_data[item]["i"]]["value"] =  struct.unpack('<L',  dict_vtable_data[item]["data_value"][2:])
                                    header,timestamp  =  struct.unpack('>hl', dict_vtable_data[item]["data_value"])
                                    entries[dict_vtable_data[item]["i"]]["value"] = str(datetime.datetime.fromtimestamp(timestamp).isoformat())
                                except AttributeError:
                                    pass
                            # value with size 8 could be a flout number, program try to unpack into a float number and store it at ENTRY value
                            if int(dict_vtable_data[item]["size"]) == 8:
                                try:
                                    entries[dict_vtable_data[item]["i"]]["value"] =  struct.unpack('<d', dict_vtable_data[item]["data_value"])[0]
                                except AttributeError:
                                    pass

                    # find the table for an entry | mapping came from Kaitai Struct parsing the tables
                    # at objectboxlite_data mapping are calculated first table start with 4, second are 8, third 12 and so on
                    # mapping = counttable * 4 
                    mapped = False # var to check if a table could found
                    for table in self.objectboxlite_data:
                        if self.objectboxlite_data[table]["mapping"] == mapping:
                            if entry.entry_header.index in self.objectboxlite_data[table]["Entries"]:
                                self.objectboxlite_data[table]["Entries"][entry.entry_header.index].append(entries)
                                mapped = True #Entry could mapped to a Table
                                break
                            else:
                                self.objectboxlite_data[table]["Entries"][entry.entry_header.index] = entries
                                mapped = True #Entry could mapped to a Table
                                break
                    if mapped == False: # if a Entry could not mapped to a Table, append the Entry to unknown data list
                        if len(entries) != 0: 
                            self.objectboxlite_unknown_data.append(entries)
                            
                            

        if len(self.objectboxlite_unknown_data) != 0:
            print("Warning: There is(are) entry(s) that could not mapped to a table. Use comand 'get_unmounts' to see that entry(s)")


        Cmd.__init__(self)

    def do_db_file(self, _):
        """list objectbox db file"""
        print("the db file is: " + box_db_file)

    def do_get_all(self, _):
        """list all boxes, properties and entries"""
        printJsonReadable(self.objectboxlite_data)
        print("")
        print("Unmountable Entries below is line:")
        print("")
        self.do_get_unmounts(_)

    def do_get_tables(self, _):
        """list all tables (boxes)"""
        for tables in self.objectboxlite_data:
            print(tables)

    def do_get_entries(self, table: str):
        """list all entries of a table with giving table name. Use 'get_tables' first."""
       
        try:
            # For debug: printJsonReadable(self.objectboxlite_data[table])
            # read the Table Headers from Properties into a list and that list will be append 
            # to the data list so store all information
            header = list()
            data = list()
            for i in self.objectboxlite_data[table]["Properties"].keys():
                header.append(str(self.objectboxlite_data[table]["Properties"][i]["property"]))
                #print("{:<10}".format(i))
            data.append(header)
            # get all Entries for the specified table and append it to the list data
            for entry in self.objectboxlite_data[table]["Entries"].keys():
                temp  = list()
                for item in self.objectboxlite_data[table]["Entries"][entry]:
                    if item == 0:
                        temp.append(str(self.objectboxlite_data[table]["Entries"][entry][item]["id"]))
                    else:
                        if "value" in self.objectboxlite_data[table]["Entries"][entry][item].keys():
                            temp.append(str(self.objectboxlite_data[table]["Entries"][entry][item]["value"]))
                        else:
                            temp.append("")
                # each row will be read into the temp list. If all infos from a Entry are in the temp, 
                # then it will be append to the data list
                data.append(temp)
            
            # calculate the max len of the largest word in each column and padded 2
            # source of the snipped:
            # https://stackoverflow.com/questions/6018916/find-max-length-of-each-column-in-a-list-of-lists
            
            # first it will calculate the len of header words.
            # all columns have a word in the header
            col_width = [2 + len(str(word)) for word in data[0]]
            # second it will calculate the len of the largest word in each column
            temp = [max(2 + len(str(word)) for word in row) for row in zip(*data)]
            # it could happened there is no data in a column (after the head line), e.g. a 
            # clolumn "description" has no entry
            # the col_width will verified with the temp array of the max len entries in a column
            # if there is a larger word in the temp it will replace the prev. len in col_width
            for i in range(0, len(temp)):
                if col_width[i] < temp[i]:
                    col_width[i] = temp[i]

            # for each row in data, can be print with the size of the column
            for row in data:
                print("".join(row[i].ljust(col_width[i]) for i in range(0, len(row))))
        except KeyError:
            print("Error: The specified Table could not found. Use command 'get_entries Table1' or use 'get_tables' first.")
            pass
    def do_get_unmounts(self, _):
        """print entries, that could not mount into a table"""
        if len(self.objectboxlite_unknown_data) == 0:
            print("No entries here - all should be mount into a table")
        else:
            for item in self.objectboxlite_unknown_data:
                print(item)
                print("")

    def do_exit(self, _):
        """close the program"""
        raise SystemExit()
            


if __name__ == '__main__':
    # get one DB File as argument
    box_db_file = ""
    args = get_args()
    box_db_file = args.file    
    if (box_db_file == None):
        print("Usage: 'python3 ObjextBoxlite -f <path to ObjectBox database file>'")
        sys.exit(0)

    # create object of kaitai struct parser class
    f = Mdb.from_file(box_db_file)
    # for Debugging
    #f = Mdb.from_file("/Users/thahn/Documents/FAU/9.Semester/PythonProjects/objectbox-user-db/data.mdb")
    #f = Mdb.from_file("/Users/thahn/Documents/FAU/9.Semester/JavaProjects/ObjectBox/objectbox-user-db/data.mdb")
    #f = Mdb.from_file("/Users/thahn/Documents/FAU/9.Semester/AndroidStudio/data.mdb")
    #f = Mdb.from_file("/Users/thahn/Documents/FAU/9.Semester/Notizen/ObjectBoxApps/MoodSpace/objectbox/data.mdb")
    #f = Mdb.from_file("/Users/thahn/Documents/FAU/9.Semester/Notizen/ObjectBoxApps/Bosch/objectbox_example_02/objectbox/data.mdb")
    #f = Mdb.from_file("/Users/thahn/Documents/FAU/9.Semester/Notizen/ObjectBoxApps/Bosch/objectbox_example_01/objectbox/data.mdb")

    # start App
    app = ObjectBoxLite()
    app.cmdloop('Welcome to the ObjectBoxLite - a forensic app for ObjectBox database files. Type help or ? for a list of commands.')