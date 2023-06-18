#Guess Who, Clue, and a combination of both. Three "game" functions!
#Credit to Chat GPT for generating script
import random

# Define a function to play the Guess Who game
def guess_who():
    # Define a list of characters
    characters = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve', 'Frank', 'Grace', 'Helen', 'Ivan', 'Jane']

    # Select a random character
    secret_character = random.choice(characters)

    # Keep asking the player questions until they guess the secret character
    while True:
        question = input("Ask a yes/no question about the character: ")
        if question.lower() == "quit":
            print("The secret character was", secret_character)
            break
        answer = input(f"Is the answer 'yes' or 'no' to the question '{question}'? ")
        if answer.lower() == "yes":
            # Remove characters that don't match the answer to the question
            characters = [c for c in characters if c != secret_character and question.lower() in c.lower()]
        else:
            # Remove characters that match the answer to the question
            characters = [c for c in characters if c != secret_character and question.lower() not in c.lower()]

        if len(characters) == 1:
            if characters[0] == secret_character:
                print("You win!")
            else:
                print("Sorry, you lose. The secret character was", secret_character)
            break

# Define a function to play the Clue game
def clue():
    # Define lists of suspects, weapons, and rooms
    suspects = ['Colonel Mustard', 'Miss Scarlett', 'Professor Plum', 'Mrs. White', 'Mr. Green', 'Mrs. Peacock']
    weapons = ['Candlestick', 'Dagger', 'Lead pipe', 'Revolver', 'Rope', 'Spanner']
    rooms = ['Kitchen', 'Ballroom', 'Conservatory', 'Billiard Room', 'Library', 'Study', 'Hall', 'Lounge', 'Dining Room']

    # Select a random suspect, weapon, and room
    secret_suspect = random.choice(suspects)
    secret_weapon = random.choice(weapons)
    secret_room = random.choice(rooms)

    # Keep asking the player to make a guess until they guess all three items
    while True:
        print("You are in the foyer.")
        suspect_guess = input("Who do you think committed the murder? ")
        weapon_guess = input("What weapon do you think was used? ")
        room_guess = input("Where do you think the murder took place? ")
        if suspect_guess == secret_suspect and weapon_guess == secret_weapon and room_guess == secret_room:
            print("Congratulations! You solved the murder!")
            break
        else:
            print("Sorry, that's not correct. You are still in the foyer.")

# Define a function to play the Guess Who Clue game
def guess_who_clue():
    # Call the guess_who() function
    guess_who()

    # Call the clue() function
    clue()

# Call the guess_who_clue() function to play the combined game
guess_who_clue()
