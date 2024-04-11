from os.path import splitext, isfile
import sqlite3
import pickle

'''
External File class
Intended to be inherited from and be used for file handlers

Parameters:
    file_name : the name of the file (including extension)
    file_path : the path where to store the file (include "/" on the end of string)

Methods:
    get_filename : Returns the filename (including extension)
    get_name : Returns the filename (not including extension)
    get_path : Returns the file path (including file name) 
'''
class ExternalFile:
    def __init__(self, file_name, file_path):
        self._file_name = file_name
        self._file_path = file_path + file_name

    def get_filename(self):
        return self._file_name

    def get_name(self):
        #"splitext" returns a tuple with the name and extension seperated
        return splitext(self._file_name)[0]

    def get_path(self):
        return self._file_path

    #Placeholder for closing a file
    def close(self):
        pass
    
    #Placeholder for creating a file
    def create_file(self):
        file = open(self._file_path, "x")
        file.close()

'''
Table Class
Not intended to be used on its own; Instances are made in the "database" class

Parameters:
    table_name : the name of the table the class holds
    database : the database object which manages the table
    columns : list of column titles

Methods:
    make_where(**conditions) : forms a "WHERE" sql query using the given conditions
    execute_sql : run an sql command using the parent database's cursor, returns output
    get_contents(**conditions) : perform a "SELECT * FROM table" with the following conditions
    add_entry(**columns) : add an entry to the table, using the column's values
    remove_entry(**conditions) : remove entry from the database with the following conditions
    get_name() : returns the name of the table
'''
class Table:
    def __init__(self, table_name, database, *columns):
        self.table_name = table_name
        self.columns = columns
        self.database = database #database OBJECT (parent)


    #Columns are the column titles
    #   keyword argument keys should be titles and values should be which value they should match
    def make_where(self, **conditions):
        out = "WHERE "

        for key in conditions.keys():
            if key not in self.columns:
                raise Exception(f"Error; Field '{key}' not in table")

            out += str(key) + "='" + str(conditions[key]) + "' AND "

        #Remove trailing "AND"
        out = out[:-4]
            
        return out


    #Uses the parent database's cursor to execute an sql query
    #   returns the output of the query
    def execute_sql(self, sql):
        # cursor = self.database.cursor
        # cursor.execute(sql)
        # return cursor.fetchall()
        return self.database.execute_sql(sql)

    #Gets entries from this table
    #   conditions : keys are column titles, values are the value they should match
    def get_contents(self, **conditions):
        return self.execute_sql(f"SELECT * FROM {self.table_name} " + self.make_where(**conditions))

    #Adds an entry to this table
    #   columns : keys are column titles, values are the value they should hold
    def add_entry(self, **columns):
        sql_columns = ""
        sql_values = ""

        #Combine column names and a the respective values
        for column_name in columns.keys():
            sql_columns += str(column_name) + ", "

            if isinstance(columns[column_name], str):
                sql_values += "'" + str(columns[column_name]) + "', "
            else:
                sql_values += str(columns[column_name]) + ", "
        
        #Remove trailing comma
        sql_columns = sql_columns[:-2]
        sql_values = sql_values[:-2]

        sql = f"({sql_columns}) VALUES ({sql_values})"
        self.execute_sql(f"INSERT INTO {self.table_name} {sql}")

    #Get the highest entry for given column
    #   column_name : name of column to get extreme value
    def highest_entry(self, column_name):
        values = self.execute_sql(f'''SELECT * FROM {self.table_name} ORDER BY {column_name} DESC''')

        if len(values) == 0:
            return 0

        return values[0][0] #index 0 = highest value


    def remove_entry(self, **conditions):
        self.execute_sql(f"DELETE FROM {self.table_name} " + self.make_where(**conditions))

    def get_name(self):
        return self.table_name


'''
Database class
Responsible for handling .db files and all the tables within

Parameters:
    file_name : the name of the datbase file (including extension)
    file_path : the location of where the datbase file is or should be stored

Methods:
    create_table(table_name, *columns) : Create a table with the given table name, columns are the column titles
    get_table(table_name) : returns the table object held by the class
    get_tables() : returns the dictionary of table names and objects
    get_contents(table_name, conditions) : calls "get_contents()" in the specified table, returns output
    add_entry(table_name, columns) : calls "add_entry()" in the specified table
    remove_entry(table_name, conditions) : calls "remove_entry()" in the specified table
    execute_sql(sql) : execute a given sql query, returns output
    close() : closes the database and cursor
'''
class Database(ExternalFile):
    def __init__(self, file_name, file_path):
        super().__init__(file_name, file_path)

        #Table dictionary
        #   keys : table names
        #   values : table objects
        self.tables = {}

        #Create the database file if it does not already exist
        if isfile(self._file_path) == False:
            self.create_file()

        self.database = sqlite3.connect(self._file_path)

        #Note this was intended to be within each table class
        self.cursor = self.database.cursor()

        #This returns a list of all the tables in the database which are already there
        orig_tables = self.execute_sql("SELECT name FROM sqlite_master")
        for table in orig_tables:
            _table = table[0]

            #This returns all the column titles from a given table
            #   each name is returned in a tuple as 1 entry
            column_names = self.execute_sql(f"SELECT name FROM PRAGMA_TABLE_INFO('{_table}')")

            #*[_name[0] for _name in column_names] gets the first index from each tuple and then seperates the list
            self.tables[_table] = Table(_table, self, *[_name[0] for _name in column_names])



    #Create a table with the given table name
    #   columns : keys are titles, values are their datatype
    #       key column title as a string, value is the datatype such as "str" or "int"
    def create_table(self, table_name, **columns):

        #Check if table already exists
        if table_name in self.tables.keys():
            raise Exception(f"Error; Table '{table_name}' already exists.")

        sql = f"CREATE TABLE {table_name} ("

        #Add each column from the "columns" tuple
        #   additionally checks the datatype and specifies which type to assign to the column
        for column in columns.keys():
            if columns[column] == str:
                sql += f"{column} TEXT, "
            elif columns[column] == int:
                sql += f"{column} INT, "
            elif columns[column] == float:
                sql += f"{column} FLOAT, "
            elif columns[column] == bool:
                sql += f"{column} BOOL, "
            else:
                raise Exception("Error; Invalid datatype, column and table was not created")
        

        #Remove the trailing comma
        if sql[-2:] == ", ":
            sql = sql[:-2] #sql[:-2] = entire string except final 2 characters

        #Close the bracket
        sql += ")"

        self.cursor.execute(sql)
        table_obj = Table(table_name, self, *columns.keys())
        self.tables[table_name] = table_obj



    #Returns the table OBJECT
    #   table_name : the name of the table (string)
    #   raises error if table does not exist.
    def get_table(self, table_name):
        
        #"Tables" is dictionary of tables
        #Perform error check
        if table_name not in self.tables.keys():
            raise Exception(f"Error; table '{table_name}' not in database.")


        #returns the table object
        return self.tables[table_name]


    #Return table dictionary
    def get_tables(self):
        return self.tables


    #Perform a "SELECT * FROM table_name WHERE conditions"
    #   returns the output of the SQL query
    #raises error if table does not exist
    #conditions : keys as column titles and values as the value they should match
    def get_contents(self, table_name, **conditions):
        table = self.get_table(table_name)

        return table.get_contents(**conditions)


    #Perform a "INSERT INTO table_name ..."
    #raises error if table does not exist
    #columns : keys as column titles and values as the value they should take
    def add_entry(self, table_name, **columns):
        table = self.get_table(table_name)
        
        table.add_entry(**columns)


    #Perfrom a "DELETE FROM table_name WHERE conditions"
    #raises error if table does not exist
    #conditions : keys as column titles and values as the value they should match
    def remove_entry(self, table_name, **conditions):
        table = self.get_table(table_name)
        
        table.remove_entry(**conditions)


    #Execute a given sql string,
    #   There is no input validation 
    def execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.database.commit()
            return self.cursor.fetchall()

        #Display error in a more useful format
        except sqlite3.OperationalError as _error:
            print(_error)
            raise sqlite3.OperationalError(f"Error; Invalid sql:\n\t{sql}")

    #Return the highest entry from the database
    def highest_entry(self, table_name, column_name):
        table = self.get_table(table_name)

        return table.highest_entry(column_name)

    def close(self):
        self.cursor.close()
        self.database.close()


'''
TextFile class

Parameters:
    file_name : the name of the file (including extension)
    file_path : the path towards the file (without file name)

Methods:
    get_file : returns an opened version of the file
'''
class TextFile(ExternalFile):
    def __init__(self, file_name, file_path):
        super().__init__(file_name, file_path)

        #Create the text file if it does not already exist
        if isfile(self._file_path) == False:
            self.create_file()
    

    #Returns an opened version of the file
    def get_file(self, open_mode):
        return open(self.get_path(), open_mode)


    #Return the contents of the entire file
    def read(self):
        file = self.get_file("r")
        output = file.read()
        file.close()

        return output


    #Return a list of each line in the file
    def readlines(self):
        file = self.get_file("r")
        output = file.readlines()
        file.close()

        return output


    #Write to the file
    #   string : the string to write to the file
    #   append : writes to the file without overwriting the entire file
    def write(self, string, append=False):
        if append == True:
            file = self.get_file("a")
        else:
            file = self.get_file("w")

        file.write(str(string))
        file.close()

    
    #Write a serialised version of the data to the file
    #   data : data/dataset to be serialised
    def write_serialised(self, data):
        serialed_string = pickle.dumps(data)

        file = self.get_file("wb")
        file.write(serialed_string)
        file.close()

    
    #Return a de-serialised version of the contents in the file
    def read_serialised(self):
        file = self.get_file("rb")
        output = pickle.loads(file.read())
        file.close()

        return output

if __name__ == "__main__":
    test_file = TextFile("TestFile.txt", "./output/")
    print(test_file.read_serialised())

