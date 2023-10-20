



class Stats:

    def __init__(self, db, collection):
        # store database object and collection object
        self.selected_db = db 
        self.selected_collection = collection
        self.analysis = [
            "describe",
            "count",
        ]
        # record what analysis user want to do
        self.option = None
        return


    def menu(self):
        # list the analysis could be done
        print("\nAnalysis Option: ")
        print("----------------")
        for i, action in enumerate(self.analysis):
            print(f"[{i}] {action}")

        # store the choice
        self.option = input("Choose an analysis to do | <Enter> For Exit: ")
        # break the recursive call 
        if self.option == "":
            return 
        # test
        try:
            # check if options are correctly entered
            self.option = int(self.option)
            # perform analysis option
            if self.analysis[self.option] == "describe":
                self.describe()
            elif self.analysis[self.option] == "count":
                pass
        except ValueError:
            print("Only Enter Index")

        self.menu()


    def describe(self):
        collection = self.selected_db[self.selected_collection.name]
        count = collection.count_documents({})
        print(f"There are {count} records in this collection")

        



