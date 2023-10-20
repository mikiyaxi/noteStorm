
import os 
from time import sleep
import sys
from pymongo import MongoClient 

class NoteOperation:
    # take in username and password for connecting to mongoDB where store notes
    def __init__(self, username, password):
        # basic data
        self.username = username 
        self.passwd = password
        self.client = None 

        # db_list, document
        self.db_list = []
        # selected database object
        self.selected_db = None
        # selected collection object 
        self.selected_collection = None


    # connect to mongoDB's database, and store the all database into self.db_list
    # all create/delete method should at the end update self.xxx value for (databases, collections, document)
    def connect(self):
        # create mongoDB specified string which needed as url for connecting database
        connection_string = f"mongodb+srv://{self.username}:{self.passwd}@cluster0.cfpainh.mongodb.net/?retryWrites=true&w=majority"
        # actual connection
        self.client = MongoClient(connection_string)
        # store all "databases object" into class variable, excluding admin and local
        self.db_list = [self.client[db] for db in self.client.list_database_names() if db not in ["admin", "config", "local"]]



    # close connection also exit the program 
    def close_connection(self):
        if self.client:                 # if there is a connection
            self.client.close()
            print("Note Closed...")
            sleep(0.2)                  # sleep for 0.2 second
            sys.exit(0)



    def get_database(self, name):
        # choose a database given their name 
        return self.client[name]



    # list all the database currently have
    def list_db(self):

        if self.db_list:
            print("Available Database:")
            print("-------------------")
            for i, db in enumerate(self.db_list):
                print(f"[{i}] {db.name}")
            print("-------------------")
        else:
            create_db_choice = input("No databases found. Would you like to create a new database? (y/n): ")
            if create_db_choice.lower() == 'y':
                self.create_database()
                # after creating new database, call itself so that it can start over for listing database for choice
                return self.list_db()
            else:
                self.close_connection()



    # create database 
    def create_database(self):
        # Prompt user for the new database name
        new_db_name = input("Enter the name for the new database: ").strip()
        if new_db_name == "":
            print("Invalid database name. Please try again.")
            return self.create_database()   # recursively call

        # Get the new database object (it won't be physically created until a collection is added)
        new_db = self.client[new_db_name]

        # Prompt user to create a collection within the new database
        # database will not be physically created until a collection is created
        print(f"Database '{new_db_name}' created. Now let's create a collection within this database.")
        self.new_collection(new_db)
        # after creating new database, append it to self.db_list
        self.db_list.append(new_db)



    def delete_database(self, db):
        confirmation = input("Comfirm? [y/n]: ")
        try:
            if confirmation == "y":
                self.client.drop_database(db)
                sleep(0.2)
                print(f'==== Database "{db.name}" has been deleted ====\n')
            else:
                print("No Action Taken")
        except:
            print("No Permission")


    # delete database, I don't know what's wrong with my permission 
    # a way to get around this is by deleting all the collections inside a database 
    # after that the database will be automatically deleted(physically not exist)
    def delete_database_method_2(self, db):
        confirmation = input("Comfirm? [y/n]: ")
        try:
            if confirmation == "y":
                for collection in db.list_collection_names():
                    db[collection].drop()
                sleep(0.2)
                print(f'==== Database "{db.name}" has been deleted ====')
            else:
                print("No Action Taken")
        except:
            print("No Permission")






    # list all the collections currently have 
    def list_collections(self, collection_list):
        if collection_list:
            print("\nAvailable Collections:")
            print("------------------------")
            # it's a list of collection object
            for i, collection in enumerate(collection_list):
                print(f"[{i}] {collection.name}")
            print("------------------------")
        else:
            print("No collections found in the selected database.")
            create_collection_choice = input("Come on, create a new collection? (y/n): ").strip().lower()
            if create_collection_choice == 'y':
                self.new_collection(selected_db)
                collections = selected_db.list_collection_names()
        # return collections, selected_db



    # create collection, also asking user to enter key and corresponding type for creating schema along the way
    def new_collection(self, db):
        # Prompt user for the new collection name
        new_collection_name = input("Give a name to the new collection | <Enter> for exit:\n> ").strip()
        if new_collection_name == "":
            self.close_connection()
        
        # call _create_schema function is enough
        schema = self._create_schema()

        # create new collection
        db.create_collection(new_collection_name, validator=schema)
        print(f'Collection "{new_collection_name}" created with schema')



    # delete collection 
    def delete_collection(self):

        # get all collections given selected database 
        collection_list = [self.selected_db[collection_name] for collection_name in self.selected_db.list_collection_names()]

        print("\nChoose One to Delete:")
        for i, collection in enumerate(collection_list):
            print(f"[{i}] {collection.name}")

        try:
            selected_collection_index = input("\nCollection Index | <Enter> for EXIT:\n> ")
            if selected_collection_index == "":
                # new_connection.close_connection()
                print("Note Closed...")
                self.close_connection()

            alert = input("Confirm? [y/n]")
            if alert == "y":
                # Convert input to integer 
                selected_collection_index = int(selected_collection_index)
                # get the selected collection object 
                selected_collection = collection_list[selected_collection_index]
                # drop it 
                selected_collection.drop()
                sleep(0.2)
                print(f'==== Collection "{collection_list[selected_collection_index].name}" has been deleted. ====\n')
            else:
                print("No Action Taken...")
            
        except:
            print("Not a Valid Input, Enter Index.")
            self.delete_collection()  # recursive call




    # define keys for creating schema 
    def define_keys(self, properties, count=0):
        # counter for keys
        count += 1
        new_key = input(f"Key {count}: ").strip()
        if new_key == "":
            return
        new_type = input(f">> {new_key.capitalize()} Type: ").strip()
        print()

        if new_type == "int":
            properties[new_key] = {"bsonType": "int"}
        elif new_type == "array":
            properties[new_key] = {"bsonType": "array"}
        elif new_type == "string":
            properties[new_key] = {"bsonType": "string"}
        else:
            properties[new_key] = {}

        self.define_keys(properties, count) # Recursive call at the end



    # create schema 
    def _create_schema(self):
        # prompt user to enter new keys and type for schema 
        properties = {}
        print("========================================================================================")
        print("Enter New Key Name(string) & Type(int, string, array) | <Enter> To Skip(No Key/Non-Type)")
        print("========================================================================================")
        self.define_keys(properties) # call recurisve function to define keys 
        # define schame 
        schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "properties": properties
            }
        }
        return schema



    # document update function
    def _update_schema(self, collection):

        # Retrieve the schema for the collection
        schema = collection.options().get('validator', {}).get('$jsonSchema', {}).get('properties', {})
        # valid bson types 
        valid_bson_types = ["string", "int", "array", "object", "double", "bool", "date", "null"]

        while True:
            print("\nExisting Schema Keys:")
            for i, key in enumerate(schema.keys()):
                print(f"[{i}] {key}: {schema[key]}")

            # prompt user for update options 
            update_options = input("Update Type [r] | Add Keys [a] | Remove Keys [d] | <Enter> Exit: ")

            # Update Keys
            if update_options == "r":
                selected_key_index = int(input("Enter Keys Index: | <Enter> For Exit: \n>").strip())
                selected_key = list(schema.keys())[selected_key_index]
                new_bson_type = input(f"Enter new BSON type for {selected_key}, <Enter> for Non Type: ").strip()
                if new_bson_type == "":
                    new_bson_type = {}
                if new_bson_type not in valid_bson_types:
                    print("Invalid BSON type.")
                    continue
                schema[selected_key]['bsonType'] = new_bson_type

            # Add Keys
            elif update_options == "a":
                new_key_name = input("Enter new key name: ").strip()
                new_key_bson_type = input("Enter new key BSON type (string/int), <Enter> for Non Type: ").strip()
                if new_key_bson_type == "":
                    new_key_bson_type = {}
                if new_key_bson_type not in valid_bson_types:
                    print("Invalid BSON type.")
                    continue
                schema[new_key_name] = {"bsonType": new_key_bson_type}

            # Delete Keys
            elif update_options == "d":
                try:
                    selected_key_index = int(input("Enter Keys Index: | <Enter> For Exit: \n>").strip())
                    selected_key = list(schema.keys())[selected_key_index]
                    del schema[selected_key]
                except:
                    print("Invalid input.")
                    continue
            else:
                # self.client.close()
                break

        # # Update the schema using collMod command 
        print(f"\n-------------\n Schema: \n {schema}\n")
        print(f'Schema Updated For Collection "{collection.name}"')
        return schema

    # all schema operations
    # ================ have authentication issues ================
    def schema_operation(self, db, collection):
        # Map action names to functions
        schema_actions = [
            # "create_schema", 
            "update_schema",
            "delete_schema",
        ]

        # Prompt user to different action
        while True:
            print("\nSchema Operation: ")
            for i, name in enumerate(schema_actions):
                print(f"[{i}] {name}", end=" ")

            # Get user's choice
            selected_action_index = input("\nEnter action number | <Enter> For Go Back:\n> ")
            if selected_action_index == "":
                break

            # Execute selected action
            try:
                selected_action_index = int(selected_action_index)
                # if schema_actions[selected_action_index] == "create_schema":
                #     # first to create a schema mannully 
                #     schema = self._create_schema()
                #     validator = {"$jsonSchema": schema}
                #     db.command("collMod", collection.name, validator=validator)
                #     print(f"Schema created for collection {collection}")
                if schema_actions[selected_action_index] == "update_schema":
                    # get the update schemea 
                    updated_schema = self._update_schema(collection)
                    # use the collMod existing schema 
                    db.command("collMod", collection.name, validator={"$jsonSchema": updated_schema})
                    print(f'Schema Updated For Collection "{collection.name}"')
                elif schema_actions[selected_action_index] == "delete_schema":
                    # delete
                    db.command("collMod", collection.name, validator={})
                    print(f'Schema Deleted For Collection "{collection.name}"')
            except (ValueError, IndexError):
                print("Not a valid input. Try again.")





    # insert data function (for multiple json document)
    def insert_document(self, collection):
        # Retrieve the schema for the collection
        schema = collection.options().get('validator', {}).get('$jsonSchema', {}).get('properties', {})
        if schema == {}:
            option = input("No Existing Scheme In This Collection. Do You Want to Create New Schema? [y/n]: ")
            if option == "y":
                # call _create_schema function is enough
                schema = self._create_schema()
                # might not have permission issue
                try:
                    self.selected_db.command("collMod", self.selected_collection.name, validator=schema)
                    # after adding it then retrive immediately 
                    schema = collection.options().get('validator', {}).get('$jsonSchema', {}).get('properties', {})
                except:
                    print("No Permission")
                    self.close_connection()
            else:
                print("Add Keys Manually Aside From Basic Key...")

        # Start with the basic keys from the schema
        new_document = {}
        print('====================================\n"/" as delimiter for multiple values\n====================================')
        for key, key_properties in schema.items():
            key_type = key_properties.get('bsonType')

            # Recursive call to handle the input
            new_document[key] = self._insert_one(key, key_type)

        # Allow user to add additional keys if they are not enforced by the schema
        while True:
            additional_key = input("Enter an additional key [Key_Name] | <Enter> for PASS: ")
            if additional_key.strip() == "":
                break
            if additional_key in schema:
                print(f"{additional_key} is already defined in the schema.")
                continue
            additional_value = input(f"Enter the value for {additional_key}: ")
            new_document[additional_key] = additional_value

        # Insert the new document
        result = collection.insert_one(new_document)
        print(f"Inserted ID: {result.inserted_id}\n")

        # ask if user need to refer collection 
        whetherRefer = input("Do you want to refer to other collection? <y/Y> for yes | <Enter> for No: ")
        if whetherRefer == "":
            return 
        elif whetherRefer.lower() == "y":
            # give the just inserted id
            self.refer_document(result.inserted_id)
        else:
            print("Invalid Input")


    # for single json data, key and key_type are coming from schema in the collection
    def _insert_one(self, key, key_type=None):
        # input check if empty string
        value_line = input(f"Enter {key}: ")

        # split the multiple input with / and automatically turn them into array type
        values = value_line.split('/')
        # check if key type is numeric value
        if key_type == 'int':
            try:
                values = [int(value) for value in values]
            except ValueError:
                print(f'Error: "{key}" key value only takes in numeric value')
                return self._insert_one(key, key_type)
        elif values == "":
            return None
        # return value for insert_document method
        return values if len(values) > 1 else values[0]



    # find id given collection name and some key name
    def find_id(self):
        collection_name = input("Which Collection To Refer?: ")
        movie_name = input("Which Movie To Refer (enter title): ")
        collection = self.selected_db[collection_name]
        document = collection.find_one({"title": movie_name})
        
        if document:
            return collection, document['_id']
        else:
            print("Movie not found")
            return None



    # Refer Document (ask for reference after insert, search, update)
    def refer_document(self, id_to_refer):
        collection, document_id = self.find_id()
        # Add the new soundtrack's _id to the movie's 'soundtracks' field
        # $set add single value, $push add append multiple value into array 
        # I use $push here, because that's more flexible for reference
        try:
            self.selected_db[collection.name].update_one(
                {'_id': document_id},
                {'$push': {f'{self.selected_collection.name}': id_to_refer}}
            )
            print(f"Successfully Create Reference in {collection.name}")
        except:
            print("Refer Unsuccessfully")

        return 




    # given a document, convert from bson to json and print out
    # actually I need to format the display
    '''
    To display the values of keys that refer to other collections, 
    you'll need to perform a join operation between the collections. 
    In MongoDB, you can use the `$lookup` operator within the `aggregate` method to achieve this.

    ```python
    from pymongo import MongoClient

    client = MongoClient('mongodb://localhost:27017/')
    db = client['database_name']

    pipeline = [
        {
            '$lookup': {
                'from': 'soundtracks',          # The collection to join with
                'localField': 'soundtrack',     # The field in the main collection (e.g., movies) that contains the reference
                'foreignField': '_id',          # The field in the joined collection (e.g., soundtracks) that matches the reference
                'as': 'soundtrack_details'     # The new field name where the joined data will be stored
            }
        }
    ]

    movies_with_soundtrack_details = db['movies'].aggregate(pipeline)

    for movie in movies_with_soundtrack_details:
        print(movie)
    ```

    This code snippet will join the `movies` collection with the `soundtracks` collection 
    based on the `soundtrack` field in the `movies` collection and the `_id` field in the `soundtracks` collection. 
    The joined soundtrack details will be stored in a new field named `soundtrack_details`.

    You can modify the `'from'`, `'localField'`, and `'foreignField'` values to match the actual names and structure of your collections.

    Note that the `$lookup` operator creates an array of matching documents, 
    so even if there is only one matching document in the joined collection, 
    the `soundtrack_details` field will contain an array with one element. 
    You may wish to use additional aggregation stages to further process the result if needed.
    '''
    def display_document(self, document):
        import json
        # when you use dumps method, any non-ASCII characters will be displayed with escape sequences
        document_json = json.dumps(document, indent=2, default=str, ensure_ascii=False)     # set ensure_ascii for enforcement
        print(document_json)




    # search movie document with key name 
    def search_document(self, collection):
        # Retrieve the schema for the collection
        schema = collection.options().get('validator', {}).get('$jsonSchema', {}).get('properties', {})
        # List basic keys in schema for user to choose
        print("Find Document (key-based):")
        # find existing keys in schema 
        keys_list = [key for key in schema.keys()]
        for i, key in enumerate(keys_list):
            print(f"({i}) {key}")

        # Prompt user to select a key
        search_key_index = int(input("Enter the number of the key you want to search: "))
        search_key = keys_list[search_key_index]

        # start the loop if invalid input received
        while True:
            # Prompt user to enter the value of the selected key,
            key_value = input(f"Match document with {search_key}'s value: ")

            # get the type of selected key based on the schema 
            expected_type = schema[search_key].get("bsonType")
            # check if search input meet the type restriction based on scheme 
            try:
                # check if the selected key require int type 
                if expected_type == 'int':
                    # turn input into integer
                    key_value = int(key_value)

                break # if input key value match the expected key value, break the loop
            except ValueError:
                print(f"Error: {search_key} key value must be of type {expected_type}")
                continue


        # Query the collection for documents with the given key and value
        matching_documents = list(collection.find({search_key: key_value}))

        # Check if any documents were found
        if not matching_documents:
            print(f"No documents found with {search_key}: {key_value}.")
            return None

        # If multiple documents match, display them and ask the user to select one
        if len(matching_documents) > 1:
            print(f'Found {len(matching_documents)} documents with {search_key} "{key_value}"')

            # sort all the document by year in ascending order 
            matching_documents.sort(key=lambda x: x.get('year', 0))

            # this method will print out the numeric label, movie title, release year of the key you entered
            for i, doc in enumerate(matching_documents):
                print(f"[{i}] {doc['title']} ({doc.get('year', 'N/A')})")

            # option to re-enter and exit 
            while True:
                selected_index = input("Enter Index | <Enter> For Exit: ")
                if selected_index == "":
                    # self.close_connection()
                    # no need to close the connection, just exit to the document level
                    return
                else:
                    try:
                        selected_index = int(selected_index)
                        selected_document = matching_documents[selected_index]
                        break
                    except ValueError:
                        print("Not a Valid Input...")

        else:
            selected_document = matching_documents[0]

        # Print out the selected document
        self.display_document(selected_document)

        return selected_document



    # update a single key
    # def _update_one(self, update_key, collection, document_to_update):
    def _update_one(self, collection, document_to_update):

        # Get the keys from the selected document 
        key_list = list(document_to_update.keys())

        # Prompt user for the key they want to update or add
        update_key = input("Key Name | <Enter> to Exit:\n> ")
        if update_key.strip() == "":
            return

        if update_key not in key_list:
            update_option = input(f"{update_key} is not a basic key in schema. Adding key to document(y/n)? ")
            if update_option == "y":
                # Prompt user for the new value, using the _insert_one method to handle data types
                update_value = self._insert_one(update_key)

                # Create the update query
                update_query = {"$set": {update_key: update_value}}

                # Update the selected document in the collection
                result = collection.update_one({"_id": document_to_update["_id"]}, update_query)

                # Check if the update was successful
                if result.modified_count > 0:
                    print(f"Updated {result.modified_count} document(s).")
                else:
                    print("No documents were updated. Check the title and key.")
            else:
                print("No Action Taken.")
        else:
            # if key is in the basic keys for this collections, update it with the newly entered value 
            # first get the corresponding key type 
            key_type = type(document_to_update[update_key])
            # print(key_type)
            update_value = self._insert_one(update_key, key_type)
            # create the update query 
            update_query = {"$set": {update_key: update_value}}
            # update the selected document in the collection
            result = collection.update_one({"_id": document_to_update["_id"]}, update_query)

        # recursively call _update_one if user wants to continue updating within the same document
        print("More Updates?")
        self._update_one(collection, document_to_update)


    # document update function
    def update_document(self, collection):

        # Retrieve the schema for the collection
        # schema = collection.options().get('validator', {}).get('$jsonSchema', {}).get('properties', {})
        # find existing keys in schema 
        # keys_list = [key for key in schema.keys()]

        # call the search method to find the one to update 
        document_to_update = self.search_document(collection)

        # call _update_one method 
        print("Choose a key to update.")
        print("-----------------------------------")
        self._update_one(collection, document_to_update)
        print("---------- Update Finish ----------")



    # delete single key method: two arguments are needed
    # 1) modify the document 
    # 2) update the document in the respective collections
    def delete_key(self, document, collection):
        # Prompt user for the key they want to remove
        delete_key = input("Choose a key to delete: ")

        # Create the update query using the "$unset" operator
        update_query = {"$unset": {delete_key: ""}}

        # Update the selected document in the collection, removing the specified key
        result = collection.update_one({"_id": document["_id"]}, update_query)

        # Check if the update was successful
        if result.modified_count > 0:
            print(f"Removed key from {result.modified_count} document(s).")
        else:
            print("No documents were updated. Check the key.")



    # delete the whole document in the collections
    def delete_document(self, document, collection):

        # actual deletion
        result = collection.delete_one({"_id": document["_id"]})
        if result.deleted_count > 0:
            print(f"Deleted {result.deleted_count} document(s).")
        else:
            print("No documents were deleted. Check the title.")



    # the whole delete method wrapped up two delete options
    def delete(self, collection):
        # Use search_document to find the document
        document_to_modify = self.search_document(collection)
        if document_to_modify is None:
            return

        # Prompt user for the type of deletion: key or entire document
        delete_type = input("Choose deletion type: (1) Delete Key, (2) Delete Entire Document: ")

        # Delete specific keys
        if delete_type == '1':
            while True:
                self.delete_key(document_to_modify, collection)

                # Ask the user if they want to continue deleting keys
                continue_deleting = input("Do you want to delete another key? (y/n): ")
                if continue_deleting.lower() != 'y':
                    break
        # Delete the entire document
        elif delete_type == '2':
            # Prompt user for confirmation
            confirmation = input(f"Are you sure you want to delete the entire document? (y/n): ")
            if confirmation.lower() == 'y':
                self.delete_document(document_to_modify, collection)
            else:
                print("Deletion Cancelled.")
        else:
            print("Invalid option. Deletion cancelled.")










