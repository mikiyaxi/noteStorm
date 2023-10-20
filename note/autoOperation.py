


# import json file directly into database
class ImportOperation:

    def __init__(self, db, collection):
        # store database object and collection object
        self.selected_db = db 
        self.selected_collection = collection
        
        return

    
    def get_external_file(self):

        path = input("Enter the path where you data is located: ")
        print("your path: ", path)

        return


    def import_json(self):
        print("cool")
        return

