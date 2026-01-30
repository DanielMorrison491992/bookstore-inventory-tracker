import os
import sqlite3
from contextlib import closing
from thefuzz import process as fuzzy_match


def execute_sqlite_query(query, parameters=()):
    """
    Executes the sqlite query provided along with provided parameters

    Parameters:
    string: a string containing the sqlite query with appropriate placeholders

    list: a list of tuples containing the parameters that match up to the placeholders in the sqlite query string
            for use with the executemany function
    or
    tuple: tuple containing the parameters that match with the placeholders in the sqlite query string

    Returns:
    boolean: whether or not the query was executed successfully
    """
    # Open connection to database using the closing() context manager to handle connection closing
    try:
        with closing(sqlite3.connect("ebookstore.db")) as connection:
            # Use context manager to handle database commits and rollbacks
            with connection:
                cursor = connection.cursor()
                # Check for parameters, if they are in the form of a list pass to cursor.executemany()
                if parameters:
                    if isinstance(parameters, list):
                        cursor.executemany(query, parameters)
                        return True
                    # If parameters are a tupple pass to cursor.execute()
                    else:
                        cursor.execute(query, parameters)
                        return True
                # If no parameters simply pass query string to cursor.execute()
                else:
                    cursor.execute(query)
                    return True
    # Catch and print any sqlite errors to console for debugging
    except sqlite3.Error as err:
        print(f"Query Failed: {query}\nError: {str(err)}")
        return False


def retrieve_sqlite_query(query, parameters=()):
    """
    Executes the sqlite query provided along with provided parameters and returns the resulting data

    Parameters:
    string: a string containing the sqlite query with appropriate placeholders


    tuple: tuple containing the parameters that match with the placeholders in the sqlite query string

    Returns:
    list: list of tuples containing the data retrieved from database
    """
    # Open connection to database using the closing() context manager to handle connection closing
    try:
        with closing(sqlite3.connect("ebookstore.db")) as connection:
            # Use context manager to handle database commits and rollbacks
            with connection:
                cursor = connection.cursor()
                # If parameters are provided, pass them to cursor.execute() along with the qury string
                if parameters:
                    cursor.execute(query, parameters)
                    result = cursor.fetchall()
                    return result
                # If no parameters provided simply execute query string
                else:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    return result
    # Catch and print any sqlite errors to console for debugging
    except sqlite3.Error as err:
        print(f"Query Failed: {query}\nError: {str(err)}")
        return False


def init_book_database():
    """
    Initializes and populates book table in database
    """
    # Generate book table

    create_book_table_query = """ 
    CREATE TABLE IF NOT EXISTS book(
    id INTEGER(4) PRIMARY KEY,
    title TEXT,
    authorID INTEGER(4),
    qty INTEGER ) ;
"""
    books_created = execute_sqlite_query(create_book_table_query)
    if not books_created:
        print("Error creating book table. Please contact system Admin")
        return

    # Populate book table with initial book entries
    populate_book_query = """
    INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)
"""

    initial_books = [
        (3001, "A Tale of Two Cities", 1290, 30),
        (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
        (3003, "TheLion, the Witch and the Wardrobe", 2356, 25),
        (3004, "The Lord of the Rings", 6380, 37),
        (3005, "Alice's Adventures in Wonderland", 5620, 12),
    ]
    books_added = execute_sqlite_query(populate_book_query, initial_books)
    if not books_added:
        print("Error populating book table. Please contact system Admin")
        return


def init_author_database():
    """
    Initializes and populates author table in database
    """
    create_author_table_query = """ 
    CREATE TABLE IF NOT EXISTS author(
    id INTEGER(4) PRIMARY KEY,
    name TEXT,
    country TEXT);
    """
    author_created = execute_sqlite_query(create_author_table_query)
    if not author_created:
        print("Error creating author table. Please contact system Admin")
        return
    # Populate author table with initial author entries
    populate_author_query = """
    INSERT INTO author (id, name, country) VALUES (?, ?, ?)
"""
    initial_authors = [
        (1290, "Charles Dickens", "England"),
        (8937, "J.K. Rowling", "England"),
        (2356, "C.S. Lewis", "Ireland"),
        (6380, "J.R.R Tolkien", "South Africa"),
        (5620, "Lewis Carroll", "England"),
    ]
    authors_added = execute_sqlite_query(populate_author_query, initial_authors)
    if not authors_added:
        print("Error populating author table. Please contact system Admin")
        return


def get_valid_option_input(valid_range):
    """
    Recursively requests an int input from within a given range, repeating until a valid input is given

    Parameters:
    list: a list of integers representing valid inputs

    Returns:
    int: a valid integer input from user
    """
    # Request input from user, returning the value if it is within the valid range
    try:
        int_selected = int(input("Select an option by number "))
        if int_selected in valid_range:
            return int_selected
        # invalid integers lead to repeated prompt
        else:
            print("Invalid selection, please try again")
            return get_valid_option_input(valid_range)
    # Non-integer inputs will raise a value error, repeating the process of requesting and validating input
    except ValueError:
        print("Invalid selection, please try again")
        return get_valid_option_input(valid_range)


def get_yes_no(input_prompt):
    """
    Recursively requests a y / n response from user until a valid response is given returning a boolean matching their response

    Parameters:
    string: The input prompt to display

    Returns:
    boolean: The user's decision
    """
    # Request input from user
    user_input = input(f"{input_prompt} y/n ").lower()
    # Validate response, treating RETURN as yes
    match user_input:
        case "y":
            return True
        case "":
            return True
        case "n":
            return False
        case _:
            print("Invalid selection, please try again")
            return get_yes_no(input_prompt)


def get_valid_string(input_prompt):
    """
    recursively requests a string input from user and validates that the string is not empty

    Parameters:
    string: the input prompt to be displayed

    Returns:
    string: the non-empty string input from the user
    """
    # Request input for given prompt
    user_input = input(input_prompt)
    # If string is empty re-prompt user
    if user_input == "":
        print("Input must contain characters, please try again")
        return get_valid_string(input_prompt)
    # Return any non-empty string inputted
    else:
        return user_input


def get_valid_integer(input_prompt):
    """
    Recursively requests an integer input from the user, repeating the prompt if a non-integer value is provided

    Parameters:
    string: the input prompt to be displayed

    Returns:
    int: the integer inputted by the user
    """
    # Request integer from user
    try:
        user_input = int(input(input_prompt))
        return user_input
    # A non-integer input will raise a ValueError and restart the process
    except ValueError:
        print("Invalid input, please try again")
        get_valid_integer(input_prompt)


def get_valid_id(table):
    """
    Recursively requests a 4 digit integer from the user and validates that the integer does not already exist in the given table

    Parameters:
    string: The table to validate against
    Returns:
    int: a unique 4 digit integer
    """
    # Request input from user, any failure in validation prompts the process to repeat until a valid integer is given
    try:
        new_id = int(input(f"Please input a unique 4 digit {table} id number "))
        # validate that integer is 4 digits long
        if len(str(new_id)) != 4:
            print("Invalid input, please input a four digit number")
            return get_valid_id(table)
        # Check that the integer given is not already a key in the given table
        id_exists = check_id_exists(table, new_id)
        if id_exists:
            print("id number already exists, please input a unique id")
            return get_valid_id(table)
        return new_id
    # Entering a non-integer input will raise a ValueError, causing process to repeat
    except ValueError:
        print("Invalid input, please input a four digit number")
        return get_valid_id(table)


def get_existing_id(table):
    """
    Recursively requests a four digit integer from the user, validating that the integer exists as a primary key in the specified table
    Parameters:
    string: a string representing the table that should be validated against

    Returns:
    int: a validated 4 digit integer
    """
    try:
        # Request input from user
        new_id = int(input(f"Please input {table} ID "))
        # Validate input length
        if len(str(new_id)) != 4:
            print("Invalid input, please input a four digit number")
            return get_existing_id(table)
        # Check to ensure that given integer exists
        id_exists = check_id_exists(table, new_id)
        # If integer is correct length and exists in given table, return integer
        if id_exists:
            return new_id
        else:
            print(
                f"ID does not match any existing {table} IDs, please enter an existing ID"
            )
            return get_existing_id(table)
    # non-integers will raise a ValueError and prompt the user for new input
    except ValueError:
        print("Invalid input, please input a four digit number")
        return get_existing_id(table)


def retrieve_similar_titles(title, excluded_title=""):
    """
    Searches book table for entries with similar title values to the given title string

    Parameters:
    string: the title against which other titles are compared to detect partial matches
    string: optional, a title to exclude from comparison

    Returns:
    list: a list of data pertaining to book entries with partially matching titles
    """
    # Retrieve all book data
    book_data = retrieve_sqlite_query(
        """
    SELECT 
    book.title,
    author.name,
    author.country,
    author.id,
    book.id,
    book.qty 
    FROM book
    INNER JOIN author
    ON book.authorID = author.id
"""
    )
    book_titles = []
    # Remove data with excluded title from data set
    for book in book_data:
        if book[0] != excluded_title:
            book_titles.append(book[0])
    # Generate similarity scores for each book title
    title_similarity_scores = fuzzy_match.extract(title, book_titles)
    similar_book_data = []
    # append data with similarity scores above 90 to book_data_list
    for score_tuple in title_similarity_scores:
        if score_tuple[1] >= 90:
            for book in book_data:
                if book[0] == score_tuple[0]:
                    similar_book_data.append(book)
    # Return similar books
    return similar_book_data


def retrieve_similar_authors(new_author_name):
    """
    Searches author table for entries with similar author_name values to the given author name string

    Parameters:
    string: the author name against which other author names will be matched

    Returns:
    list: a list of author data pertaining to author entries with partially matching author names
    """
    # Retrieve author data
    author_data = retrieve_sqlite_query(
        """
    SELECT * FROM author
"""
    )
    # Append all author names to author_names table
    author_names = []
    for author in author_data:
        author_names.append(author[1])

    similar_author_data = []
    # Generate similarity scores for every author name in author_names
    author_similarity_scores = fuzzy_match.extract(new_author_name, author_names)
    # Capture all author names with similarity scores higher than 75 for return
    for score_tuple in author_similarity_scores:
        if score_tuple[1] >= 75:
            for author in author_data:
                if author[1] == score_tuple[0]:
                    similar_author_data.append(author)
    # Return partially matching author names
    return similar_author_data


def check_id_exists(table, id):
    """
    Checks if a given id exists on the specified table
    Parameters:
    string: the table to be checked, either book or author
    int: a 4 digit integer to check for
    Returns:
    boolean: whether or not the given id exists in the given table
    """
    query_string = None
    # Define sqlite query string according to the specified table
    if table == "book":
        query_string = """
    SELECT * FROM book WHERE id = ?
"""
    elif table == "author":
        query_string = """
    SELECT * FROM author WHERE id = ?
"""
    else:
        print("Error: Table does not exist")
        return
    # Check if the id exists on the given table and return true or false accordingly
    matching_id = retrieve_sqlite_query(query_string, (id,))
    if matching_id:
        return True
    else:
        return False


def add_author():
    """
    Handles the process of adding an author by requesting the required inputs from the user
    Checks to see if a similar author exists on the database already and provides the option to
    use that author rather than creating a new one

    Returns:
    list: a list of data pertaining to an existing author
    or
    int: the id of the newly created author
    """
    # Request input from user
    new_author_name = get_valid_string("Please input author name ")
    # Check for similar author names
    similar_authors = retrieve_similar_authors(new_author_name)
    # If authors with similar names exist, display their details and give the user the option of selecting
    # one of them rather than creating a new author
    if similar_authors:
        print("Similar Authors found in database")
        for index, author in enumerate(similar_authors):
            print(f"Number: {index} Name: {author[1]}. Country: {author[2]}")
        # Ask if user wants to use existing author
        use_existing_author = get_yes_no("Do you wish to use an existing author? ")
        if use_existing_author:
            # prompt user to select author by number and return that author
            target_author_index = get_valid_option_input(range(len(similar_authors)))
            return similar_authors[target_author_index][0]
    # If user chooses to create new author get further author details
    new_author_country = get_valid_string("Please input authors country of origin ")
    new_author_id = get_valid_id("author")
    # Add new author to author table
    author_created = execute_sqlite_query(
        """
    INSERT INTO author (id, name, country)
    VALUES (?,?,?)
""",
        (new_author_id, new_author_name, new_author_country),
    )
    # return ID of newly created author
    if author_created:
        return new_author_id
    else:
        return None


def add_book():
    """
    Handles the process of adding a new book to the database by prompting for user inputs and inserting
    a new book entry into the book table. Provides rudimentart check to (hopefully) prevent duplicate
    entries
    

    """
    # Request user input
    new_title = get_valid_string("Please input the title ")
    # Check if similar titles exist
    similar_titles = retrieve_similar_titles(new_title)
    # Display similar titles and ask user if they wish to continue adding a book
    if similar_titles:
        print("Book may already exist in database as: ")
        for entry in similar_titles:
            print(f"Title: {entry[0]}, Author: {entry[1]}, Author Country: {entry[2]}")
        continue_adding = get_yes_no(f"Continue adding {new_title} to database? ")
        if not continue_adding:
            print("Add Book aborted")
            return
    new_book_id = get_valid_id("book")
    # Allow user to select an existing author or generate a new author if required
    author_id = add_author()
    # If author generation fails, print appropriate error message
    if author_id is None:
        print("Error generating new Author, add book aborted")
        return
    new_book_quantity = get_valid_integer("Please input stock quantity ")
    # Add new book to book table
    book_added = execute_sqlite_query(
        """
    INSERT INTO book (id, title, authorID, qty)
    VALUES (?,?,?,?)
""",
        (new_book_id, new_title, author_id, new_book_quantity),
    )
    # Print appropriate message depending on success of database operation
    if book_added:
        print(f"New Book {new_title} added to database successfully")
        return
    else:
        print(f"Error adding new book {new_title} to database")


def view_all_books():
    """
    
    Retrieves all books from the database and displays them in a user-friendly manner

    """
    # Retrieve book data
    book_data = retrieve_sqlite_query(
        """
     SELECT 
    book.id,
    book.title,
    author.name,
    author.country,
    book.qty
    FROM book
    INNER JOIN author
    ON book.authorID = author.id
"""
    )
    # Iterate through book data, displaying each book seperately
    for book in book_data:
        print(
            f"""
----------
Book ID: {book[0]}
Title: {book[1]}
Author: {book[2]}
Author Country: {book[3]}
Current Stock: {book[4]}              
----------              
"""
        )


def update_creates_orphan(author_id):
    """
    Checks the database to assess whether altering the author_id property of a book will leave the corresponding author table entry without any book entries

    Parameters:
    int: the author id to assess

    Returns:
    boolean: whether or not changing the author id on one book will create an orphan author entry
    """
    # Retrive books linked to author
    books_by_author = retrieve_sqlite_query(
        """
    SELECT id FROM book WHERE authorID = ?
""",
        (author_id,),
    )
    # If author only has one book, then changing the authorID of any book associated with author_id will result in an orphan entry in author table
    if len(books_by_author) < 2:
        return True
    return False

def get_affected_books(author_id):
    """
    Retrieves all books linked to an author ID, used downstream to determine if altering an author field will affect more
    than one book object
    Parameters:
    integer: four digit author ID 

    Returns:
    list: A list of book data
    """
    # Retrive book data
    affected_books = retrieve_sqlite_query("""
    SELECT id, title FROM book where authorID = ?
""",(author_id,))
    # Return book data
    return affected_books


def update_quantity(book_id, current_quant):
    """
    Handles the process of updating the quantity property of a given book 
    Parameters:
    int: a 4 digit book ID
    int: the new quantity

    Returns:
    int: the new quantity for the given book
    or
    boolean: indicating the operation was unsuccessful

    """
    print(f"Current stock is: {current_quant}")
    # Get new quantity value from user
    new_quant = get_valid_integer("Please input the new stock quantity ")
    # Update quantity in database
    quant_updated = execute_sqlite_query(
        """
    UPDATE book SET qty = ? WHERE id = ?
""",
        (new_quant, book_id),
    )
    # Return new quantity if database operation was successful, return False if not
    if quant_updated:
        return new_quant
    return False


def update_title(book_id, current_title):
    """
    Handles the process of updating the title associated with a given book id.
    prompts user for input and displays any titles that are similar to the new title to 
    (hopefully) prevent duplication of titles

    Parameters:
    int: 4 digit book id
    string: the current book title

    """
    print(f"Current title is: {current_title}")
    # Get new title from user
    new_title = get_valid_string("Please input new title ")
    # Check for similar titles
    similar_titles = retrieve_similar_titles(new_title, current_title)
    # If similar titles exist, alert the user and display them
    if similar_titles:
        print("Book title may already exist in database as:")
        for entry in similar_titles:
            print(f"Title: {entry[0]}, Author: {entry[1]}, Author Country: {entry[2]}")
        print(
            "To avoid duplication of books consider deleting the current entry rather than changing title"
        )
        # Check if user wants to continue with the title change
        continue_editing = get_yes_no("Continue editing book title? ")
        # If yes, update book entry with new title
        if continue_editing:
            print(f"Updating {current_title} to {new_title}")
            title_updated = execute_sqlite_query(
                """
            UPDATE book SET title = ? WHERE id =?
            """,
                (new_title, book_id),
            )
            if title_updated:
                print(f"Book: {current_title} renamed to {new_title} successfully")
                return
            else:
                print(
                    f"Error updating title on Book {current_title}, Please contact system admin"
                )
                return


def update_author_id(book_id, current_auth_id, current_auth_name, current_auth_country):
    """
    Handles the process of updating the author of a book entry. Allows user to add a new author
    or select an existing author to associate with the book entry
    Parameters:
    int: 4 digit id of the book to be updated
    int: 4 digit id of the existing author
    string: the current authors name
    string: the current authors country

    """
    # Display options to user
    print(
        """
--Options--
1. Assign book to existing author
2. Assign book to new author
0. Return to main menu
"""
    )
    option_selection = get_valid_option_input(range(3))
    match option_selection:
        # User chooses to update book using an existing author
        case 1:
            print("--Assigning book to existing Author--")
            # Get an existing author id from the user
            new_id = get_existing_id("author")
            # Check if this change will leave an author entry without any corresponding books, ie creat an orphan entry
            orphan = update_creates_orphan(current_auth_id)
            # Inform user that the change to author will result in deletion of the orphan author
            if orphan:
                print(
                    f"Changing the current book author id will result in the deletion of Author:{current_auth_name} from {current_auth_country}"
                )
                # Ask if user wishes to continue
                continue_editing = get_yes_no("Continue with author ID change?")
                # If no, abort operation with appropriate message
                if not continue_editing:
                    print("Author ID update aborted, returning to main menu")
                    return
            # If yes, update book entry in database
            book_edited = execute_sqlite_query(
                """
            UPDATE book SET authorID = ? WHERE id = ?
            """,
                (new_id, book_id),
            )
            # If book updated successfully delete any orphan entries created by the operation
            if book_edited:
                if orphan:
                    orphan_removed = execute_sqlite_query(
                        """
                    DELETE FROM author WHERE id =?
                    """,
                        (current_auth_id,),
                    )
                    if orphan_removed:
                        print(
                            f"Orphan Author {current_auth_name} from {current_auth_country} removed from database"
                        )
                    else:
                        print(
                            "Removal of Orphan entry unsuccessful, Please contact system administrator"
                        )
                print("Author ID changed successfully")
                return
            else:
                print("Error Editing Author ID, please contact system Administrator")
        case 2:
            # User chooses to add a new author
            print("--Assigning book to new author--")
            # Check to see if change would result in an orphan author entry
            orphan = update_creates_orphan(current_auth_id)
            # If so, inform the user that the change will result in deletion of the orphan author
            if orphan:
                print(
                    f"Changing the current book author id will result in the deletion of Author:{current_auth_name} from {current_auth_country}"
                )
                # Ask if user wishes to continue
                continue_editing = get_yes_no("Continue with author ID change?")
                # If no, abort operation
                if not continue_editing:
                    print("Author ID update aborted, returning to main menu")
                    return
            # Create new author and retrieve its ID using add_author(), displaying appropriate message if operation fails
            print("-Please provide author details-")
            new_id = add_author()
            if new_id is None:
                print(
                    "Error generating new author, please contact system Administrator"
                )
                return
            # Carry out book update
            book_edited = execute_sqlite_query(
                """
            UPDATE book SET authorID = ? WHERE id = ?
            """,
                (new_id, book_id),
            )
            # If operation is successful and an orphan entry was created, delete the orphan entry
            if book_edited:
                if orphan:
                    orphan_removed = execute_sqlite_query(
                        """
                    DELETE FROM author WHERE id =?
                    """,
                        (current_auth_id,),
                    )
                    if orphan_removed:
                        print(
                            f"Orphan Author {current_auth_name} from {current_auth_country} removed from database"
                        )
                    else:
                        print(
                            "Removal of Orphan entry unsuccessful, Please contact system administrator"
                        )
                print("Author ID changed successfully")
                return
            else:
                print("Error Editing Author ID, please contact system Administrator")
        case 0:
            print("Author ID update aborted, returning to main menu")
            return False


def update_author_name(author_id, current_name):
    """
    Handles the process of updating the name of an author, informing the user of the books that will be affected by this change

    Parameters:
    int: 4 digit author id code
    string: The current name of the author
    """
    # Get a list of books affected by the change
    affected_books = get_affected_books(author_id)
    # Display affected books
    print("Modifying this author name will affect the following books:")
    for book in affected_books:
        print(f"ID: {book[0]}, Title: {book[1]}")
    # Ask user if they wish to continue with editing 
    continue_editing = get_yes_no("Continue editing author name?")
    # If not abort process
    if not continue_editing:
        print("Editing author name Aborted, returning to main menu")
        return
    # If yes get new name value for author and update database
    new_author_name = get_valid_string("Please input the new author name")
    author_name_edited = execute_sqlite_query("""
    UPDATE author SET name = ? WHERE id = ?
""",(new_author_name,author_id))
    if author_name_edited:
        print(f"Author name changed from {current_name} to {new_author_name}")
        return
    else:
        print(f"Error changing author name from {current_name} to {new_author_name}, please contact system Admin")
        return

def update_author_country(author_id, current_country):
    """
    Handles the process of updating the country of an author, informing the user of the books that will be affected by this change

    Parameters:
    int: 4 digit author id code
    string: The current country of the author
    """
    # Get a list of books affected by the change
    affected_books = get_affected_books(author_id)
    # Display affected books
    print("Modifying this author name will affect the following books:")
    for book in affected_books:
        print(f"ID: {book[0]}, Title: {book[1]}")
    # Ask user if they wish to continue with editing 
    continue_editing = get_yes_no("Continue editing author country?")
    # If not, abort process
    if not continue_editing:
        print("Editing author country Aborted, returning to main menu")
        return
    # If yes, get new country string from user and update author entry
    new_country = get_valid_string("Please input new author country")
    country_edited = execute_sqlite_query("""
    UPDATE author SET country = ? WHERE id = ?
""",(new_country,author_id))
    if country_edited:
        print(f"Author country changed from {current_country} to {new_country}")
        return
    else:
        print(f"Error changing author name from {current_country} to {new_country}, please contact system Admin")

def update_book():
    """
    Handles the process of updating a book.
    First requests a book id from the user then displays a sub-menu of updates that can be carried out
    """
    # Get valid book ID from user
    target_id = get_existing_id("book")
    # Retrieve book with matching ID 
    target_books = retrieve_sqlite_query(
        """
    SELECT 
    book.id,
    book.title,
    author.id,
    author.name,
    author.country,
    book.qty
    FROM book
    INNER JOIN author
    ON book.authorID = author.id
    WHERE book.id = ?
""",
        (target_id,),
    )
    book_id, book_title, author_id, author_name, author_country, current_stock = (
        target_books[0]
    )
    # Display selected book
    print("Selected Book:")
    print(
        f"""
----------
Book ID: {book_id}
Title: {book_title}
Author: {author_name}
Author ID: {author_id}
Author Country: {author_country}
Current Stock: {current_stock}              
----------              
"""
    )
    # Display options
    print(
        """
--Options--
1. Update Stock Quantity
2. Update Title
3. Update Author ID
4. Update Author Name
5. Update Author Country
0. Return To Main Menu
"""
    )
    # Get selection from user
    edit_selection = get_valid_option_input(range(6))
    # Call appropriate functions to carry out the selected option
    match edit_selection:

        case 1:
            print("--Updating Stock Quantity")
            new_quantity = update_quantity(book_id, current_stock)
            if new_quantity:
                print(f"{book_title} stock updated. New stock: {new_quantity}")
                return
            else:
                print(f"Error updating {book_title} stock, please contact system admin")
        case 2:
            print("--Updating Title")
            update_title(book_id, book_title)
        case 3:
            print("--Updating Author ID--")
            update_author_id(book_id, author_id, author_name, author_country)
        case 4:
            print("--Updating Author Name--")
            update_author_name(author_id, author_name)
        case 5:
            print("--Updating Author Country")
            update_author_country(author_id, author_country)
        case 0:
            return

def delete_book():
    """
    Handles the process of deleting a book from the database, checking for the creation of orphan
    author entries and deleting them 
    """
    # Get book id from user
    target_id = get_existing_id("book")
    # Retrieve and display book data
    target_book_list = retrieve_sqlite_query("""
    SELECT 
    book.id,
    book.title,
    author.id,
    author.name,
    author.country,
    book.qty
    FROM book
    INNER JOIN author
    ON book.authorID = author.id
    WHERE book.id = ?""",(target_id,))
    target_book = target_book_list[0]
    book_id, title, author_id, author_name, author_country, qty = target_book
    print("Book to be deleted:")
    print(
        f"""
        ----------
        Book ID: {book_id}
        Title: {title}
        Author: {author_name}
        Author ID: {author_id}
        Author Country: {author_country}
        Current Stock: {qty}              
        ----------              
"""
    )
    # Confirm delete operation
    confirm_delete = get_yes_no("Is this the book you wish to delete?")
    if not confirm_delete:
        print("Book delete aborted")
        return
    # Check if deletion of book would create an author entry with no corresponding books
    delete_creates_orphan = update_creates_orphan(author_id)
    # If orphans would be created, inform user and ask if they wish to continue
    if delete_creates_orphan:
        print(f"Deleting this book will also remove Author {author_name} from {author_country} with ID: {author_id} from database")
        continue_deleting = get_yes_no('Continue deleting?')
        # If not, abort process
        if not continue_deleting:
            print("Book delete aborted")
            return
    # If yes, delete book entry from book table
    print("Deleting Selected book")
    delete_successful = execute_sqlite_query("""
    DELETE FROM book WHERE id =?
    """,(book_id,))
    # If book sucessfully deleted and an orphan author entry was created, delete that author entry
    # Display appropriate messages depending on outcome of the delete operations
    if delete_successful:
        if delete_creates_orphan:
            orphan_deleted = execute_sqlite_query("""
            DELETE FROM author WHERE id = ?
            """,(author_id,))
            if orphan_deleted:
                print(f"Book {title} successfully deleted. Author {author_name} from {author_country} successfully deleted")
                return
            else:
                print(f"Book {title} Deleted, orphan Author entry created. Please contact system Admin")
                return
        print(f"Book {title} succesfully deleted")
    else:
        print(f"Error Deleting book {title}, please contact system Admin")

def search_by_id():
    """
    Retrieves and displays a book with id specified by the user
    """
    # Get book id from user
    target_id = get_existing_id("book")
    # Retrive book data
    target_book_list = retrieve_sqlite_query("""
    SELECT 
    book.id,
    book.title,
    author.id,
    author.name,
    author.country,
    book.qty
    FROM book
    INNER JOIN author
    ON book.authorID = author.id
    WHERE book.id = ?""",(target_id,))
    target_book = target_book_list[0]
    #Unpack book properties
    book_id, title, author_id, author_name, author_country, qty = target_book
    # Display book
    print("-Results-")
    print(
        f"""
    ----------
    Book ID: {book_id}
    Title: {title}
    Author: {author_name}
    Author ID: {author_id}
    Author Country: {author_country}
    Current Stock: {qty}              
    ----------              
"""
    )

def search_by_title():
    """
    Searches for and displays books with titles that closely match a given title string
    """
    # Get query from user
    query_title = get_valid_string("Please input title to search for ")
    # Retrieve books with titles similar to search query using retrieve_similar_titles()
    search_results = retrieve_similar_titles(query_title)
    # If there are results, display them
    if search_results:
        print("-Best Results-")
        for result in search_results:
            title, author_name, author_country, author_id, book_id, qty = result
            print(f"""
            ----------
            Book ID: {book_id}
            Title: {title}
            Author ID: {author_id}
            Author: {author_name}
            Author Country: {author_country}
            Current Stock: {qty}              
            ----------              
            """)
    # If no results found, display appropriate 
    else:
        print(f"No results for query {query_title} found")

def search_book():
    """
    Displays a search sub-menu and calls functions appropriate to the user selection
    """
    # Display menu
    print("""
    --Search Options--
    1. Search by ID
    2. Search by title
    0. Return to main menu
""")
    # Get selection from user
    search_option = get_valid_option_input(range(3))
    # Call appropriate function or exit according to user selection
    match search_option:
        case 1:
            print("--Searching by ID")
            search_by_id()
        case 2:
            print("--Searching by Title")
            search_by_title()
        case 0:
            return

# Database initialization on first startup using given dataset
if not os.path.exists("ebookstore.db"):
    init_book_database()
    init_author_database()

# Main menu loop
while True:
    print(
        """
--Welcome to BookShelf Database Manager---
    Select an Option Below:
    1. Enter Book
    2. Update Book
    3. Delete Book
    4. Search Book
    5. View Details of All Books
    0. Exit      
"""
    )
    menu_selection = get_valid_option_input(range(6))

    match menu_selection:
        case 1:
            print("---ENTERING NEW BOOK---")
            add_book()
        case 2:
            print("---UPDATING BOOK---")
            update_book()
        case 3:
            print("---DELETE BOOK---")
            delete_book()
        case 4:
            print("---SEARCH---")
            search_book()
        case 5:
            print("---VIEWING ALL BOOKS---")
            view_all_books()
        case 0:
            break
