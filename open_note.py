import sys
import argparse
import logging
from types import new_class
from note.noteOperation import NoteOperation
from note.autoOperation import ImportOperation
from note.statsAnalysis import Stats



'''
DATABASE LEVEL PROMPT DESIGN:
---------------------------------------------------------------------------------------------------------------------------------------
you are thinking that why can the program to display the available database and new database action at the same time?
because that's more user-friendly. Because you are using terminal as interface, so operation has to be sequence by sequence,
this is terrible because some operation could happen in parallell, but don't worry because you have writting method/class instance,
if you interact with the program through an UI, you could activate available database listing and create new database at the same time,
because that's just a matter of activate two methods.

In this command line UI we also want to achieve that, so listing available database and available operation at that level as well.
use separate command like numeric and alphabets
never write program that cannot be execute in parallel 
---------------------------------------------------------------------------------------------------------------------------------------

PROGRAM LEVEL PROMPT DESIGN:
---------------------------------------------------------------------------------------------------------------------------------------
when you wanna be able to back to previous level from current level (document level back to collection operation level), 
the way to achieve this is by separating each level in function, and use a main() function that wrapped out sub-level method
---------------------------------------------------------------------------------------------------------------------------------------

'''



# Database Level 
def database_level(new_connection):
    '''
    The funciton taken in a mongoDB connection, and prompt user to actions on database level (create, delete, select, etc)
    will update two arguments 1. a list of all databases after user's action 2. a database selected by user (if any)
    '''

    # List available databases and prompt user to choose
    databases = new_connection.list_db()
    while True:  # Loop until a valid selection is made
        # Before working with any database, ask the user if they want to create a new database
        user_command = input("Database Index[0-∞] | Create New Database[n] | Delete Database[d] | Close Note[Enter]: \n> ")

        if user_command == "n":
            new_connection.create_database()  # Call the method to create a new database
            databases = new_connection.list_db()  # Update the list of databases
            continue    # Continue to prompt the user
                        # the "continue" operation skip whatever code after it (collections_prompt)
                        # and then back to the begining of the iteration (while loop) and restart the loop 
                        # asking user to enter input again, whenever user doesn't enter "n"
                        # it will go to either close the connection or enter the selected database 
                        # the rest of the code gets executing, same for the next continue in the collection part 
        if user_command == "d":
            # when coming to deleting, we need to let user type themselves
            db_for_deletion_name = input("Type The Database Name For Deletion: ").strip() 
            # get the database from cilent(cluster), pass it to delete_database method
            db_for_deletion = new_connection.client[db_for_deletion_name]
            # call delete_database method
            new_connection.delete_database(db_for_deletion)

        elif user_command == "":
            new_connection.close_connection()
        else:
            try:
                selected_db_index = int(user_command)
                if 0 <= selected_db_index < len(new_connection.db_list):
                    # based on index, find corresponding databse object
                    selected_db = new_connection.db_list[selected_db_index]
                    print(f"You have chosen the database: ---{selected_db.name}---")
                    break  # Exit the loop when a valid selection is made
                else:
                    print("Index out of range. Try again.")
            except ValueError:
                print("Not a valid input. Try again.")

    # update selected database value 
    new_connection.selected_db = selected_db
    # print out collection object to see what's inside
    # print(new_connection.selected_db['general'])
    # print(new_connection.selected_db['general'].name)






# Collection Level
def collection_level(new_connection):

    '''
    this function take in a mongoDB connection again, after database level operation, 
    (the class object should have store a list of existing database, and a selected database object separately)
                                                         --------
    prompt user to take actions on collection level, and |update| the value of selected collection 
                                                         --------
    since already have selected db stored, so we don't need to create an extra collection list to store all collections 
    we can directly access through selected database
    '''
    # first get selected database from class 
    selected_db = new_connection.selected_db
    # then get all the collection object from this selected database
    collections = [selected_db[collection_name] for collection_name in selected_db.list_collection_names()]

    # List available collections within the selected database and prompt user to choose
    new_connection.list_collections(collections)


    while True:  # Loop until a valid selection is made
        user_command = input("Collection Index[0-∞] | Create New Collection[n] | Delete Collection[d] | Close Note[Enter] | Go Back[b]: \n> ")

        if user_command == "n":
            new_connection.new_collection(selected_db)  # Call the method to create a new collection
            collections = [selected_db[collection_name] for collection_name in selected_db.list_collection_names()]
            # print out update collection list
            new_connection.list_collections(collections)
            continue  # Continue to prompt the user

        elif user_command == "d":
            new_connection.delete_collection()
            # update collections after deletion
            collections = [selected_db[collection_name] for collection_name in selected_db.list_collection_names()]
            # print out list after deletion
            new_connection.list_collections(collections)
        # beck to database operation level
        elif user_command == "b":
            # return database_level(new_connection)
            # database_level(new_connection)
            return 'database'

        elif user_command == "":
            new_connection.close_connection()
        else:
            try:
                selected_collection_index = int(user_command)
                if 0 <= selected_collection_index < len(collections):
                    selected_collection = collections[selected_collection_index]
                    # update the self.selected_collection in class object
                    new_connection.selected_collection = selected_collection
                    print(f"You have chosen the collection: ---{new_connection.selected_collection.name}---")
                    break  # Exit the loop when a valid selection is made
                else:
                    print("Index out of range. Try again.")
            except ValueError:
                print("Not a valid input. Try again.")

    # count the number of documents inside a collections
    count = selected_collection.count_documents({})
    print(f"\n{count} documents in the collection.")
    return "document"




# Document Level (action)
def document_level(new_connection):

    # get selected database and collection 
    selected_db = new_connection.selected_db 
    selected_collection = new_connection.selected_collection
    # create new stats object for data analysis
    collection_analysis = Stats(selected_db, selected_collection)
    # create new auto Operation for entering data automatically 
    autoEnter = ImportOperation(selected_db, selected_collection)

    # actions: list of instruction string paired with class method 
    # methods are stored in arrays, such that one instruction could execute multiple methods
    actions = [
        ("Insert", [new_connection.insert_document]),
        ("Search", [new_connection.search_document]),
        ("Update", [new_connection.update_document]),
        ("Delete", [new_connection.delete]),
        ("Schema", [new_connection.schema_operation]), # new schema operation, multiple actions within schema
        ("Import", [autoEnter.import_json]),
        ("Stats", [collection_analysis.menu]),
    ]

    # prompt user to different action 
    while True:
        print("\nActions: ")
        for i, (name, _) in enumerate(actions):
            # print(f"[{i}] {name}", end=" ")     # print option in one line
            print(f"[{i}] {name}")

        # save action option, not key value
        selected_action_index = input("\nEnter action number | <Enter> for EXIT | Go Back[b] :\n> ")
        if selected_action_index == "":
            new_connection.close_connection()
            # print("Note Closed...")
            # break
        
        # go back previous level, which is collection operation
        elif selected_action_index == "b":
            # return collection_level((new_connection, selected_db.name))
            return 'collection'
            # pass

        # convert the action input into int() 
        try:
            selected_action_index = int(selected_action_index)
            # check if the index is valid
            if 0 <= selected_action_index < len(actions):
                user_action, action_functions = actions[selected_action_index]
                # two arguments need to be passed in for function/method 
                # since schema and stats methods are stored in array which inside a list of tuple 
                # and I know right now there is only one function in the array, so locate it with zero index 
                if user_action == "Schema":
                    action_functions[0](selected_db, selected_collection)
                # no input needed 
                elif user_action == "Stats" or user_action == "Import" or user_action == "Refer":
                    action_functions[0]()   # for stats operation, make sure to keep all analysis inside stats class
                                            # break the loop to outside when user ask for
                # signle input argyment
                else:
                    for action_function in action_functions:
                        action_function(selected_collection) # call each function in the action method list
            else:
                print("Index out of range")

        except ValueError:
            print("-----------------------------------")
            print("| Not a Valid Input, Enter Index. |")
            print("-----------------------------------")
            continue





# main menu for nagivation 
def main_menu(new_connection):
    # inditialize two startup value
    current_level = 'database'

    # loop 
    while current_level:
        if current_level == 'database':
            database_level(new_connection)
            current_level = 'collection'
        elif current_level == 'collection':
            current_level = collection_level(new_connection)
        elif current_level == 'document':
            current_level = document_level(new_connection)
        else:
            break





def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description='Connect to MongoDB')
    parser.add_argument('--username', required=True, help='Username for MongoDB connection')
    parser.add_argument('--password', required=True, help='Password for MongoDB connection')
    args = parser.parse_args()

    # logging info
    logging.info(f"Connecting with username: {args.username}")

    # create new NoteOperation object, to interact with note of movies
    new_connection = NoteOperation(args.username, args.password)
    # connect to cluster
    new_connection.connect()

    # listing menu 
    main_menu(new_connection)

    return




if __name__ == '__main__':
    main()

